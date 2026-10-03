"""
测试后端API的脚本（手动联调用：需要运行中的后端，默认跳过）
运行: FACELENS_LIVE_API=1 pytest tests/test_api.py  （后端已启动时）
"""
import os
import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get('FACELENS_LIVE_API') != '1',
    reason='需要运行中的后端（设置 FACELENS_LIVE_API=1 并启动后端后启用）',
)
import requests
import json
import base64
from pathlib import Path

# API基础URL
BASE_URL = 'http://localhost:5000/api'

def test_health():
    """测试健康检查接口"""
    print("测试健康检查接口...")
    response = requests.get(f'{BASE_URL}/health')
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_models():
    """测试获取模型列表接口"""
    print("测试获取模型列表接口...")
    response = requests.get(f'{BASE_URL}/models')
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_predict(image_path, model='cnn', detect_face=True):
    """测试预测接口"""
    print(f"测试预测接口 (模型: {model})...")
    
    # 读取图片并转换为base64
    if not Path(image_path).exists():
        print(f"错误: 图片文件不存在: {image_path}")
        return
    
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # 发送请求
    data = {
        'image': f'data:image/jpeg;base64,{image_data}',
        'model': model,
        'detect_face': detect_face
    }
    
    response = requests.post(f'{BASE_URL}/predict', json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"识别结果: {result.get('emotion_cn')} ({result.get('emotion')})")
        print(f"置信度: {result.get('confidence'):.2%}")
        print(f"使用模型: {result.get('model_used')}")
        print("\n概率分布:")
        for emotion, prob in result.get('probabilities_cn', {}).items():
            print(f"  {emotion}: {prob:.2%}")
    else:
        print(f"错误: {response.text}")
    print()

def main():
    """主函数"""
    print("=" * 50)
    print("后端API测试脚本")
    print("=" * 50)
    print()
    
    try:
        # 1. 测试健康检查
        test_health()
        
        # 2. 测试获取模型列表
        test_models()
        
        # 3. 测试预测接口
        # 注意: 需要提供一张测试图片的路径
        # test_predict('path/to/test/image.jpg', model='cnn')
        
        print("提示: 要测试预测接口,请修改脚本中的图片路径")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到后端服务")
        print("请确保后端服务已启动 (python backend/app.py)")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    main()
