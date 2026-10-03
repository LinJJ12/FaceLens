"""
图片预处理工具
支持：
- 固定到 (96,96,1) 的灰度输入
- 按目标形状 (H,W,C) 动态预处理
- 根据 Keras 模型或 SavedModel 推断输入形状并预处理
"""
from PIL import Image
import numpy as np
from typing import Optional, Tuple
import cv2
import threading
try:
    from mtcnn import MTCNN  # pip install mtcnn
    _MTCNN_AVAILABLE = True
except Exception:
    _MTCNN_AVAILABLE = False
import math

# MTCNN 检测器单例：构建三个子网络开销大，必须复用（视频逐帧分析尤其明显）
_MTCNN_DETECTOR = None
_MTCNN_LOCK = threading.Lock()


def get_mtcnn_detector():
    """获取进程级共享的 MTCNN 检测器；未安装 mtcnn 时返回 None。"""
    global _MTCNN_DETECTOR
    if not _MTCNN_AVAILABLE:
        return None
    if _MTCNN_DETECTOR is None:
        with _MTCNN_LOCK:
            if _MTCNN_DETECTOR is None:
                _MTCNN_DETECTOR = MTCNN()
    return _MTCNN_DETECTOR


# Haar 级联检测器同样只加载一次
_HAAR_CASCADE = None
_HAAR_LOCK = threading.Lock()


def get_haar_cascade():
    """获取进程级共享的 Haar 人脸级联检测器；加载失败返回 None。"""
    global _HAAR_CASCADE
    if _HAAR_CASCADE is None:
        with _HAAR_LOCK:
            if _HAAR_CASCADE is None:
                try:
                    cascade = cv2.CascadeClassifier(
                        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                    )
                    _HAAR_CASCADE = cascade if not cascade.empty() else False
                except Exception:
                    _HAAR_CASCADE = False
    return _HAAR_CASCADE or None


def preprocess_96x96_gray(image: Image.Image) -> np.ndarray:
    """将图片转灰度并调整到 (96,96,1)，返回 (1,96,96,1) 的 float32/0-1 数组。"""
    img = image.convert('L').resize((96, 96))
    arr = np.array(img).reshape(1, 96, 96, 1).astype(np.float32) / 255.0
    return arr


def enhance_clarity(image: Image.Image) -> Image.Image:
    """
    基于原图做清晰度增强（用于前端展示）：
    - LAB 空间对 L 通道做 CLAHE 对比度增强
    - 轻度反锐化（Unsharp Mask）提升边缘清晰
    返回与原图同尺寸的 PIL.Image
    """
    try:
        rgb = image.convert('RGB')
        bgr = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR)
        # CLAHE on L channel
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l2 = clahe.apply(l)
        lab2 = cv2.merge([l2, a, b])
        bgr2 = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)
        # Unsharp mask
        blur = cv2.GaussianBlur(bgr2, (0, 0), sigmaX=1.0, sigmaY=1.0)
        sharp = cv2.addWeighted(bgr2, 1.5, blur, -0.5, 0)
        # 限制溢出
        sharp = np.clip(sharp, 0, 255).astype(np.uint8)
        rgb_out = cv2.cvtColor(sharp, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_out)
    except Exception:
        # 失败则直接返回原图
        return image


def preprocess_for_shape(image: Image.Image, target_shape: Tuple[int, int, int], mode: str = 'simple') -> np.ndarray:
    """
    将图片处理为目标形状 (H, W, C)。
    - 若 C==1：转灰度 'L'
    - 若 C==3：转 'RGB'
    - mode: 'simple' (0-1), 'vgg' (VGG16 Caffe), 'efficientnet' (EfficientNet Torch)
    返回形状为 (1,H,W,C) 的 float32 数组。
    """
    h, w, c = target_shape
    if c == 1:
        img = image.convert('L').resize((w, h))
        arr = np.array(img).reshape(1, h, w, 1).astype(np.float32) / 255.0
    elif c == 3:
        img = image.convert('RGB').resize((w, h))
        arr = np.array(img).astype(np.float32)
        if arr.ndim == 2:
            arr = np.stack([arr]*3, axis=-1)
        arr = np.expand_dims(arr, 0)
        
        # 根据不同模型应用不同的预处理
        if mode == 'vgg':
            # VGG16 Caffe mode: RGB -> BGR, subtract mean [103.939, 116.779, 123.68]
            arr = arr[..., ::-1]  # RGB to BGR
            arr[..., 0] -= 103.939
            arr[..., 1] -= 116.779
            arr[..., 2] -= 123.68
        elif mode == 'efficientnet':
            # SE 模型训练时使用 tf.keras.applications.efficientnet.preprocess_input，
            # 在 TF 2.x 中它是直通（保持 0-255），归一化由模型内部的 Rescaling 层完成。
            # 这里显式透传，保证装不装 TensorFlow 行为一致。
            pass
        else:
            # simple mode: just scale to [0,1]
            arr = arr / 255.0
    else:
        # 其它通道数，尽量按RGB处理并再裁剪/扩展
        img = image.convert('RGB').resize((w, h))
        arr = np.array(img).astype(np.float32) / 255.0
        # 裁剪或填充到 c 通道
        if arr.shape[-1] >= c:
            arr = arr[..., :c]
        else:
            pad = c - arr.shape[-1]
            arr = np.concatenate([arr, np.zeros((*arr.shape[:2], pad), dtype=arr.dtype)], axis=-1)
        arr = np.expand_dims(arr, 0)
    return arr


def infer_input_shape_from_keras(model) -> Optional[Tuple[int, int, int]]:
    """从 Keras 模型推断 (H,W,C) 输入形状。失败则返回 None。"""
    try:
        ishape = getattr(model, 'input_shape', None)
        if isinstance(ishape, (list, tuple)):
            # 处理多输入，取第一个
            if isinstance(ishape[0], (list, tuple)) and len(ishape) > 0 and isinstance(ishape[0][0], (list, tuple)):
                ishape = ishape[0]
            # 形如 (None, H, W, C)
            if len(ishape) == 4:
                return int(ishape[1]), int(ishape[2]), int(ishape[3])
    except Exception:
        pass
    return None


def infer_input_shape_from_saved_model(loaded) -> Optional[Tuple[int, int, int]]:
    """从 tf.saved_model.load 的对象推断 (H,W,C) 输入形状。失败则返回 None。"""
    try:
        if hasattr(loaded, 'signatures') and 'serving_default' in loaded.signatures:
            infer = loaded.signatures['serving_default']
            # structured_input_signature: (args, kwargs)
            spec = list(infer.structured_input_signature[1].values())[0]
            # 期望形状: (None,H,W,C)
            shape = spec.shape
            if len(shape) == 4:
                return int(shape[1]), int(shape[2]), int(shape[3])
    except Exception:
        pass
    return None


def preprocess_for_model(image: Image.Image, model=None, loaded=None, fallback: Tuple[int,int,int]=(100,100,3), mode: str = 'simple') -> np.ndarray:
    """
    根据模型对象或 SavedModel 对象推断输入形状并进行预处理。
    优先从 Keras 模型获取；若无则从 SavedModel 获取；都失败时使用 fallback。
    mode: 'simple'(0-1), 'vgg'(Caffe), 'efficientnet'(Torch)
    """
    shape = None
    if model is not None:
        shape = infer_input_shape_from_keras(model)
    if shape is None and loaded is not None:
        shape = infer_input_shape_from_saved_model(loaded)
    if shape is None:
        shape = fallback
    return preprocess_for_shape(image, shape, mode=mode)


# 兼容旧函数名：从路径读取并按96x96灰度处理
def preprocess_image(image_path: str) -> np.ndarray:
    img = Image.open(image_path)
    return preprocess_96x96_gray(img)


# =============== 基于 MTCNN 的人脸检测与对齐 ===============
def detect_and_align_mtcnn(image: Image.Image, desired_size: int = 112, margin: int = 10) -> Optional[Image.Image]:
    """
    使用 MTCNN 检测人脸并进行五点对齐，输出对齐后的人脸图像。
    - desired_size: 输出图像的目标边长（正方形）
    - margin: 在裁剪时留出的边距像素
    返回：PIL.Image 或 None（未检测到）
    """
    detector = get_mtcnn_detector()
    if detector is None:
        return None

    rgb = image.convert('RGB')
    res = detector.detect_faces(np.array(rgb))
    if not res:
        return None

    # 选置信度最高的人脸
    face = max(res, key=lambda d: d.get('confidence', 0))
    box = face['box']  # [x, y, w, h]
    keypoints = face.get('keypoints', {})
    # 关键点
    le = keypoints.get('left_eye')
    re = keypoints.get('right_eye')
    nose = keypoints.get('nose')
    lm = keypoints.get('mouth_left')
    rm = keypoints.get('mouth_right')

    if not (le and re and nose and lm and rm):
        # 如果缺关键点，退化为 box 裁剪 + resize
        return _crop_face_box(rgb, box, margin, desired_size)

    # 基于五点的相似变换对齐（ArcFace 模板）
    aligned = _align_by_five_points(rgb, le, re, nose, lm, rm, output_size=(desired_size, desired_size))
    if aligned is not None:
        return aligned

    # 计算旋转角度，使双眼水平
    dx = re[0] - le[0]
    dy = re[1] - le[1]
    angle = math.degrees(math.atan2(dy, dx))
    # 旋转整张图（作为兜底方案）
    rotated = rgb.rotate(-angle, resample=Image.BILINEAR, expand=True)

    # 重新用 MTCNN 检测一次，得到旋转后的 box（更稳妥）
    res2 = detector.detect_faces(np.array(rotated))
    if not res2:
        # 退化为原 box 裁剪
        return _crop_face_box(rgb, box, margin, desired_size)

    face2 = max(res2, key=lambda d: d.get('confidence', 0))
    return _crop_face_box(rotated, face2['box'], margin, desired_size)


def _crop_face_box(image_rgb: Image.Image, box, margin: int, desired_size: int) -> Image.Image:
    """按人脸框裁剪并 resize 到目标尺寸；越界部分收口到图像边界内。"""
    x, y, w, h = box
    x1 = max(0, x - margin)
    y1 = max(0, y - margin)
    x2 = min(image_rgb.width, x + w + margin)
    y2 = min(image_rgb.height, y + h + margin)
    crop = image_rgb.crop((x1, y1, x2, y2))
    return crop.resize((desired_size, desired_size))


def _align_by_five_points(image_rgb: Image.Image,
                          left_eye: Tuple[int, int],
                          right_eye: Tuple[int, int],
                          nose: Tuple[int, int],
                          mouth_left: Tuple[int, int],
                          mouth_right: Tuple[int, int],
                          output_size: Tuple[int, int] = (112, 112)) -> Optional[Image.Image]:
    """
    使用五点特征做相似变换对齐，输出固定大小图像；采用反射填充避免黑边。
    模板采用 ArcFace 112x112 标准关键点坐标。
    """
    try:
        dst_w, dst_h = output_size[0], output_size[1]
        # ArcFace 112x112 模板关键点（float 精度）
        # 参考: https://github.com/deepinsight/insightface/issues/1026
        dst = np.array([
            [38.2946, 51.6963],   # left_eye
            [73.5318, 51.5014],   # right_eye
            [56.0252, 71.7366],   # nose
            [41.5493, 92.3655],   # mouth_left
            [70.7299, 92.2041],   # mouth_right
        ], dtype=np.float32)
        # 如果目标尺寸不是 112x112，按比例缩放模板
        if (dst_w, dst_h) != (112, 112):
            scale_x = dst_w / 112.0
            scale_y = dst_h / 112.0
            dst = np.stack([dst[:, 0] * scale_x, dst[:, 1] * scale_y], axis=1).astype(np.float32)

        src = np.array([
            [left_eye[0], left_eye[1]],
            [right_eye[0], right_eye[1]],
            [nose[0], nose[1]],
            [mouth_left[0], mouth_left[1]],
            [mouth_right[0], mouth_right[1]],
        ], dtype=np.float32)

        # 估计相似变换（只允许缩放+旋转+平移）
        # 使用所有五点做鲁棒估计
        M, _ = cv2.estimateAffinePartial2D(src, dst, method=cv2.LMEDS)
        if M is None:
            return None

        img = np.array(image_rgb)
        aligned = cv2.warpAffine(img, M, (dst_w, dst_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        return Image.fromarray(aligned)
    except Exception:
        return None

