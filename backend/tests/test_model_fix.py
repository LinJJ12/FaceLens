"""
快速验证修复效果的脚本（需要 TensorFlow 与模型权重，缺一即跳过）
使用一张测试图片,分别用VGG和SE模型预测,查看置信度
"""
import sys
import os
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

pytest.importorskip('tensorflow', reason='需要 TensorFlow 才能验证模型')

import numpy as np
from PIL import Image
from src.ml.image_preprocess import preprocess_for_model, detect_and_align_mtcnn
from src.config.settings import MODEL_PATHS
import tensorflow as tf
from tensorflow import keras

EMOTION_LABELS = ['anger', 'disgust', 'fear', 'happy', 'normal', 'sad', 'surprised']
EMOTION_LABELS_CN = ['生气', '厌恶', '害怕', '高兴', '平静', '悲伤', '惊讶']

def load_model_safe(model_name):
    """安全加载模型"""
    model_paths = {
        'vgg': MODEL_PATHS['vgg'],
        'se81': MODEL_PATHS['se81'],
        'se83': MODEL_PATHS['se83']
    }
    
    path = model_paths.get(model_name)
    if not os.path.exists(path):
        print(f"❌ 模型文件不存在: {path}")
        return None
    
    try:
        if model_name == 'vgg':
            model = keras.models.load_model(path)
            return {'type': 'keras', 'obj': model}
        else:
            loaded = tf.saved_model.load(path)
            return {'type': 'saved', 'obj': loaded}
    except Exception as e:
        print(f"❌ 加载模型失败: {e}")
        return None

def predict_with_mode(image, model_entry, model_name, preprocess_mode):
    """使用指定的预处理模式进行预测"""
    # 预处理
    processed = preprocess_for_model(
        image,
        model=model_entry['obj'] if model_entry['type'] == 'keras' else None,
        loaded=model_entry['obj'] if model_entry['type'] == 'saved' else None,
        fallback=(100, 100, 3),
        mode=preprocess_mode
    )
    
    # 推理
    if model_entry['type'] == 'keras':
        preds = model_entry['obj'].predict(processed, verbose=0)
    else:
        infer = model_entry['obj'].signatures['serving_default']
        input_key = list(infer.structured_input_signature[1].keys())[0]
        output_tensor = infer(**{input_key: tf.constant(processed, dtype=tf.float32)})
        preds = list(output_tensor.values())[0].numpy()
    
    return preds[0]

def main():
    print("=" * 70)
    print("VGG/SE模型预处理修复验证")
    print("=" * 70)
    
    # 检查是否提供了图片路径
    if len(sys.argv) < 2:
        print("\n用法: python test_model_fix.py <图片路径>")
        print("例如: python test_model_fix.py test_face.jpg")
        print("\n如果没有测试图片,将跳过实际预测测试...")
        print("但预处理功能已通过 test_preprocessing.py 验证!")
        return
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"\n❌ 图片文件不存在: {image_path}")
        return
    
    # 加载图片
    image = Image.open(image_path)
    print(f"\n📷 加载图片: {image_path} ({image.size})")
    
    # 人脸对齐
    aligned = detect_and_align_mtcnn(image)
    if aligned:
        image = aligned
        print("✓ MTCNN人脸对齐成功")
    else:
        print("⚠ 未检测到人脸,使用原图")
    
    # 测试VGG模型
    print("\n" + "=" * 70)
    print("测试 VGG 模型")
    print("=" * 70)
    vgg_model = load_model_safe('vgg')
    if vgg_model:
        print("\n对比不同预处理模式的结果:")
        print("-" * 70)
        
        # 错误的预处理 (simple)
        print("\n❌ 使用错误的预处理 (simple, 0-1归一化):")
        preds_wrong = predict_with_mode(image, vgg_model, 'vgg', 'simple')
        pred_class = np.argmax(preds_wrong)
        confidence = preds_wrong[pred_class]
        print(f"   预测: {EMOTION_LABELS_CN[pred_class]} ({EMOTION_LABELS[pred_class]})")
        print(f"   置信度: {confidence:.2%}")
        print(f"   概率分布: {preds_wrong}")
        
        # 正确的预处理 (vgg)
        print("\n✅ 使用正确的预处理 (vgg, Caffe BGR-mean):")
        preds_correct = predict_with_mode(image, vgg_model, 'vgg', 'vgg')
        pred_class = np.argmax(preds_correct)
        confidence = preds_correct[pred_class]
        print(f"   预测: {EMOTION_LABELS_CN[pred_class]} ({EMOTION_LABELS[pred_class]})")
        print(f"   置信度: {confidence:.2%}")
        print(f"   概率分布: {preds_correct}")
    
    # 测试SE模型
    print("\n" + "=" * 70)
    print("测试 SE-83 模型")
    print("=" * 70)
    se_model = load_model_safe('se83')
    if se_model:
        print("\n对比不同预处理模式的结果:")
        print("-" * 70)
        
        # 错误的预处理 (simple)
        print("\n❌ 使用错误的预处理 (simple, 0-1归一化):")
        preds_wrong = predict_with_mode(image, se_model, 'se83', 'simple')
        pred_class = np.argmax(preds_wrong)
        confidence = preds_wrong[pred_class]
        print(f"   预测: {EMOTION_LABELS_CN[pred_class]} ({EMOTION_LABELS[pred_class]})")
        print(f"   置信度: {confidence:.2%}")
        print(f"   概率分布: {preds_wrong}")
        
        # 正确的预处理 (efficientnet)
        print("\n✅ 使用正确的预处理 (efficientnet, Torch [-1,1]):")
        preds_correct = predict_with_mode(image, se_model, 'se83', 'efficientnet')
        pred_class = np.argmax(preds_correct)
        confidence = preds_correct[pred_class]
        print(f"   预测: {EMOTION_LABELS_CN[pred_class]} ({EMOTION_LABELS[pred_class]})")
        print(f"   置信度: {confidence:.2%}")
        print(f"   概率分布: {preds_correct}")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成!")
    print("=" * 70)
    print("\n说明:")
    print("- 正确的预处理应该有更高的置信度和更合理的概率分布")
    print("- 如果错误预处理的置信度很低或预测不合理,说明修复是有效的")

if __name__ == '__main__':
    main()
