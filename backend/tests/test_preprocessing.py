"""图像预处理测试（不依赖 TensorFlow）。"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.ml.image_preprocess import preprocess_for_shape

test_img = Image.new('RGB', (100, 100), color=(128, 128, 128))


def test_simple_mode_scales_to_0_1():
    arr = preprocess_for_shape(test_img, (100, 100, 3), mode='simple')
    assert arr.shape == (1, 100, 100, 3)
    assert np.allclose(arr[0, 50, 50, :], 128 / 255, atol=0.001)


def test_vgg_mode_caffe_bgr_mean_subtraction():
    arr = preprocess_for_shape(test_img, (100, 100, 3), mode='vgg')
    assert arr.shape == (1, 100, 100, 3)
    # RGB -> BGR 后分别减去 Caffe 均值
    expected = [128 - 103.939, 128 - 116.779, 128 - 123.68]
    assert np.allclose(arr[0, 50, 50, :], expected, atol=0.1)


def test_efficientnet_mode_is_passthrough_0_255():
    """SE 模型训练使用 TF2 efficientnet.preprocess_input（直通，保持 0-255）。

    归一化由模型内部的 Rescaling 层完成；无论环境是否安装 TensorFlow，
    该模式的行为都必须一致（回归防护：曾有 fallback 误除以 255）。
    """
    arr = preprocess_for_shape(test_img, (100, 100, 3), mode='efficientnet')
    assert arr.shape == (1, 100, 100, 3)
    assert np.allclose(arr[0, 50, 50, :], 128.0, atol=0.001)


def test_grayscale_mode():
    arr = preprocess_for_shape(test_img, (96, 96, 1), mode='simple')
    assert arr.shape == (1, 96, 96, 1)
    assert np.allclose(arr, 128 / 255, atol=0.001)


def test_resize_to_target_shape():
    arr = preprocess_for_shape(Image.new('RGB', (333, 217)), (96, 96, 1), mode='simple')
    assert arr.shape == (1, 96, 96, 1)
