"""
测试SE SavedModel加载（需要 TensorFlow 与 SE 模型权重，缺一即跳过）
"""
import sys
import os
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

pytest.importorskip('tensorflow', reason='需要 TensorFlow 才能加载 SavedModel')

from src.config.settings import MODEL_PATHS

pytestmark = pytest.mark.skipif(
    not all(os.path.exists(str(MODEL_PATHS.get(n, ''))) for n in ('se81', 'se83')),
    reason='需要 SE 模型权重文件',
)

import numpy as np
import tensorflow as tf
from PIL import Image
from src.ml.image_preprocess import preprocess_for_model
from src.config.settings import MODEL_PATHS

def test_se_model():
    print("="*50)
    print("测试SE SavedModel加载")
    print("="*50)
    
    # 测试两个SE模型
    models_to_test = [
        ('SE-81', MODEL_PATHS['se81']),
        ('SE-83', MODEL_PATHS['se83'])
    ]
    
    all_passed = True
    
    for name, model_path in models_to_test:
        print(f"\n{'='*50}")
        print(f"测试 {name} 模型")
        print(f"{'='*50}")
        
        # 检查路径是否存在
        if not os.path.exists(model_path):
            print(f"✗ 模型路径不存在: {model_path}")
            all_passed = False
            continue
        
        print(f"\n1. 加载模型: {model_path}")
        model = None
        loaded_by_keras = False
        try:
            model = tf.keras.models.load_model(model_path)
            loaded_by_keras = True
            print("✓ Keras模型加载成功!")
        except Exception as e:
            print(f"Keras加载失败: {e}\n尝试tf.saved_model.load方式...")
            try:
                loaded = tf.saved_model.load(model_path)
                print("✓ tf.saved_model.load加载成功!")
            except Exception as e2:
                print(f"✗ tf.saved_model.load加载失败: {e2}")
                all_passed = False
                continue
        
        print("\n2. 模型信息:")
        if loaded_by_keras:
            print(f"   输入形状: {model.input_shape}")
            print(f"   输出形状: {model.output_shape}")
            print(f"   参数总数: {model.count_params():,}")
            print("\n3. 模型结构概览:")
            model.summary()
        else:
            print("   已用tf.saved_model.load加载,无Keras结构信息")
        
        print("\n4. 测试预测...")
        # 构造随机图片并按模型输入形状预处理
        rand_img = (np.random.rand(150, 150, 3) * 255).astype(np.uint8)
        pil_img = Image.fromarray(rand_img, mode='RGB')
        test_input = preprocess_for_model(
            pil_img,
            model=model if loaded_by_keras else None,
            loaded=None if loaded_by_keras else loaded,
            fallback=(96, 96, 1)
        )
        try:
            if loaded_by_keras:
                predictions = model.predict(test_input, verbose=0)
            else:
                # 兼容tf.saved_model.load导出的模型
                infer = None
                if hasattr(loaded, 'signatures') and 'serving_default' in loaded.signatures:
                    infer = loaded.signatures['serving_default']
                else:
                    infer = loaded
                # 构造输入字典并调用
                input_key = list(infer.structured_input_signature[1].keys())[0]
                outputs = infer(**{input_key: tf.constant(test_input)})
                out_key = list(outputs.keys())[0]
                predictions = outputs[out_key].numpy()
            print(f"✓ 预测成功!")
            print(f"   输出形状: {predictions.shape}")
            print(f"   概率和: {predictions.sum():.6f}")
            emotion_labels = ['anger', 'disgust', 'fear', 'happy', 'normal', 'sad', 'surprised']
            print(f"\n   预测分布:")
            for i, (label, prob) in enumerate(zip(emotion_labels, predictions[0])):
                print(f"      {label:10s}: {prob:.4f} {'█' * int(prob * 50)}")
            if predictions.shape == (1, 7) and np.isclose(predictions.sum(), 1.0, atol=1e-5):
                print("\n✓ 输出格式正确(7个类别,概率和≈1)")
            else:
                print("\n⚠ 输出格式可能有问题")
                all_passed = False
        except Exception as e:
            print(f"✗ 预测失败: {e}")
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("✓ 所有测试通过!")
        print("\n下一步:")
        print("1. 启动后端服务: python main.py")
        print("2. 在前端中选择 SE-81 或 SE-83 模型")
        print("3. 上传图片进行识别")
    else:
        print("✗ 部分测试失败,请检查错误信息")
    print(f"{'='*50}")
    
    return all_passed

if __name__ == '__main__':
    success = test_se_model()
    sys.exit(0 if success else 1)
