"""
人脸质量评估模块
评估人脸图像的质量,包括模糊度、亮度、对比度等
"""
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Tuple

def assess_face_quality(image: Image.Image) -> Dict:
    """
    评估人脸图像质量
    
    返回:
    {
        'blur_score': float,        # 清晰度分数 (0-100, 越高越清晰)
        'brightness': float,        # 亮度 (0-255)
        'contrast': float,          # 对比度 (0-100)
        'quality_score': float,     # 综合质量分 (0-100)
        'warnings': List[str],      # 警告信息
        'is_acceptable': bool       # 是否可接受
    }
    """
    # 转换为灰度图
    if image.mode != 'L':
        gray = np.array(image.convert('L'))
    else:
        gray = np.array(image)

    # 1. 评估模糊度 (使用拉普拉斯方差)
    blur_score = float(_assess_blur(gray))

    # 2. 评估亮度
    brightness = float(_assess_brightness(gray))

    # 3. 评估对比度
    contrast = float(_assess_contrast(gray))

    # 4. 计算综合质量分
    quality_score = float(_calculate_quality_score(blur_score, brightness, contrast))

    # 5. 生成警告信息
    warnings = _generate_warnings(blur_score, brightness, contrast)

    # 6. 判断是否可接受（显式转 bool：numpy 比较结果为 np.bool_，无法 JSON 序列化）
    is_acceptable = bool(quality_score >= 50 and len(warnings) == 0)

    return {
        'blur_score': round(blur_score, 2),
        'brightness': round(brightness, 2),
        'contrast': round(contrast, 2),
        'quality_score': round(quality_score, 2),
        'warnings': warnings,
        'is_acceptable': is_acceptable
    }


def _assess_blur(gray: np.ndarray) -> float:
    """
    评估图像模糊度
    使用拉普拉斯方差,值越大越清晰
    返回0-100的分数
    """
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # 将方差映射到0-100分数
    # 通常方差>100表示清晰,<50表示模糊
    if laplacian_var >= 100:
        score = 100
    elif laplacian_var >= 50:
        score = 50 + (laplacian_var - 50) * 1.0  # 50-100映射到50-100
    else:
        score = laplacian_var * 1.0  # 0-50映射到0-50
    
    return min(100, score)


def _assess_brightness(gray: np.ndarray) -> float:
    """
    评估图像亮度
    返回平均灰度值 (0-255)
    """
    return float(np.mean(gray))


def _assess_contrast(gray: np.ndarray) -> float:
    """
    评估图像对比度
    使用标准差表示对比度,返回0-100的分数
    """
    std = float(np.std(gray))
    
    # 将标准差映射到0-100分数
    # 通常std>60表示对比度好,<30表示对比度差
    if std >= 60:
        score = 100
    elif std >= 30:
        score = 50 + (std - 30) * 1.67  # 30-60映射到50-100
    else:
        score = std * 1.67  # 0-30映射到0-50
    
    return min(100, score)


def _calculate_quality_score(blur_score: float, brightness: float, contrast: float) -> float:
    """
    计算综合质量分
    权重: 清晰度50%, 亮度25%, 对比度25%
    """
    # 将亮度(0-255)归一化到0-100
    # 理想亮度范围: 80-180, 中心值127
    if 80 <= brightness <= 180:
        brightness_score = 100
    elif brightness < 80:
        brightness_score = max(0, brightness / 80 * 100)
    else:  # brightness > 180
        brightness_score = max(0, 100 - (brightness - 180) / 75 * 100)
    
    # 加权计算
    quality = blur_score * 0.5 + brightness_score * 0.25 + contrast * 0.25
    
    return quality


def _generate_warnings(blur_score: float, brightness: float, contrast: float) -> list:
    """生成警告信息"""
    warnings = []
    
    # 模糊检测
    if blur_score < 40:
        warnings.append('图像过于模糊,建议重新拍摄更清晰的照片')
    elif blur_score < 60:
        warnings.append('图像清晰度一般,可能影响识别准确率')
    
    # 亮度检测
    if brightness < 60:
        warnings.append('图像过暗,建议增加光照')
    elif brightness > 200:
        warnings.append('图像过亮,建议减少光照或避免强光直射')
    
    # 对比度检测
    if contrast < 40:
        warnings.append('图像对比度过低,建议调整光线或拍摄角度')
    
    return warnings


def get_quality_level(quality_score: float) -> Tuple[str, str]:
    """
    根据质量分返回等级和颜色
    
    返回: (等级, 颜色)
    """
    if quality_score >= 80:
        return '优秀', 'success'
    elif quality_score >= 60:
        return '良好', 'primary'
    elif quality_score >= 40:
        return '一般', 'warning'
    else:
        return '较差', 'danger'


if __name__ == '__main__':
    # 测试代码
    test_img = Image.new('L', (112, 112), 128)
    result = assess_face_quality(test_img)
    print("质量评估结果:")
    for key, value in result.items():
        print(f"  {key}: {value}")

