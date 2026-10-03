"""
视频情绪识别处理模块
支持视频上传、帧提取、批量情绪识别
"""

import cv2
import numpy as np
from PIL import Image
import os
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import base64
import io

logger = logging.getLogger(__name__)


class VideoEmotionProcessor:
    """视频情绪识别处理器"""
    
    def __init__(self, upload_folder='uploads'):
        """
        初始化视频处理器
        Args:
            upload_folder: 视频上传保存目录
        """
        self.upload_folder = upload_folder
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            logger.info(f"创建上传目录: {upload_folder}")
    
    def save_video(self, video_data: bytes, filename: str = None) -> str:
        """
        保存上传的视频文件
        Args:
            video_data: 视频二进制数据
            filename: 文件名（可选）
        Returns:
            保存的文件路径
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"video_{timestamp}.mp4"
            
            filepath = os.path.join(self.upload_folder, filename)
            
            with open(filepath, 'wb') as f:
                f.write(video_data)
            
            logger.info(f"✅ 视频保存成功: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"❌ 视频保存失败: {str(e)}")
            raise
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        获取视频基本信息
        Args:
            video_path: 视频文件路径
        Returns:
            包含视频信息的字典
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {video_path}")
            
            # 获取视频属性
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            cap.release()
            
            info = {
                'fps': fps,
                'total_frames': total_frames,
                'width': width,
                'height': height,
                'duration': duration,
                'duration_formatted': self._format_duration(duration)
            }
            
            logger.info(f"📹 视频信息: {width}x{height}, {fps}fps, {info['duration_formatted']}")
            return info
        
        except Exception as e:
            logger.error(f"❌ 获取视频信息失败: {str(e)}")
            raise
    
    def _format_duration(self, seconds: float) -> str:
        """格式化时长为 HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def extract_frames(
        self, 
        video_path: str, 
        interval_seconds: float = 5.0,
        max_frames: int = 100
    ) -> List[Tuple[float, np.ndarray, str]]:
        """
        从视频中按时间间隔提取帧
        Args:
            video_path: 视频文件路径
            interval_seconds: 提取间隔（秒）
            max_frames: 最大提取帧数
        Returns:
            帧列表，每个元素为 (时间戳, 帧图像, base64图像)
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps and fps > 0 else 0

            # fps 异常（损坏/不可读的视频）时提前失败，避免后续除零
            if not fps or fps <= 0 or fps != fps:  # fps != fps 捕获 NaN
                cap.release()
                raise ValueError(f"无法读取视频帧率，文件可能已损坏: {video_path}")

            # 计算提取间隔的帧数（interval<=0 时强制为 1 帧一取，防止取模除零）
            frame_interval = max(1, int(fps * interval_seconds))
            
            logger.info(f"🎬 开始提取视频帧: 间隔={interval_seconds}秒, FPS={fps}, 总时长={duration:.1f}秒")
            
            frames = []
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # 按间隔提取帧
                if frame_count % frame_interval == 0 and extracted_count < max_frames:
                    timestamp = frame_count / fps
                    
                    # 转换BGR到RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # 转换为base64用于传输
                    pil_image = Image.fromarray(frame_rgb)
                    buffered = io.BytesIO()
                    pil_image.save(buffered, format="JPEG", quality=90)
                    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    img_data_url = f"data:image/jpeg;base64,{img_base64}"
                    
                    frames.append((timestamp, frame_rgb, img_data_url))
                    extracted_count += 1
                    
                    logger.info(f"  ✓ 提取帧 {extracted_count}/{max_frames} at {timestamp:.1f}s")
                
                frame_count += 1
                
                if extracted_count >= max_frames:
                    logger.warning(f"⚠️  达到最大帧数限制 ({max_frames}), 停止提取")
                    break
            
            cap.release()
            
            logger.info(f"✅ 帧提取完成: 共提取 {len(frames)} 帧")
            return frames
        
        except Exception as e:
            logger.error(f"❌ 帧提取失败: {str(e)}")
            raise
    
    def extract_frame_at_time(
        self, 
        video_path: str, 
        timestamp: float
    ) -> Optional[np.ndarray]:
        """
        提取指定时间点的帧
        Args:
            video_path: 视频文件路径
            timestamp: 时间戳（秒）
        Returns:
            帧图像或None
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            
            cap.release()
            
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return frame_rgb
            else:
                return None
        
        except Exception as e:
            logger.error(f"❌ 提取指定帧失败: {str(e)}")
            return None
    
    def get_thumbnail(self, video_path: str) -> Optional[str]:
        """
        获取视频缩略图（第一帧）
        Args:
            video_path: 视频文件路径
        Returns:
            base64编码的缩略图
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # 调整缩略图大小
                pil_image.thumbnail((320, 240))
                
                buffered = io.BytesIO()
                pil_image.save(buffered, format="JPEG", quality=85)
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                return f"data:image/jpeg;base64,{img_base64}"
            
            return None
        
        except Exception as e:
            logger.error(f"❌ 获取缩略图失败: {str(e)}")
            return None
    
    def cleanup_old_videos(self, days: int = 7):
        """
        清理旧的视频文件
        Args:
            days: 保留天数
        """
        try:
            import time
            current_time = time.time()
            removed_count = 0
            
            for filename in os.listdir(self.upload_folder):
                filepath = os.path.join(self.upload_folder, filename)
                
                if os.path.isfile(filepath):
                    file_age_days = (current_time - os.path.getmtime(filepath)) / 86400
                    
                    if file_age_days > days:
                        os.remove(filepath)
                        removed_count += 1
                        logger.info(f"🗑️  删除旧视频: {filename} (已存在 {file_age_days:.1f} 天)")
            
            if removed_count > 0:
                logger.info(f"✅ 清理完成: 删除 {removed_count} 个旧视频文件")
        
        except Exception as e:
            logger.error(f"❌ 清理旧视频失败: {str(e)}")


def create_emotion_timeline(analysis_results: List[Dict]) -> Dict:
    """
    创建情绪时间轴数据
    Args:
        analysis_results: 分析结果列表，每个元素包含 {timestamp, emotion, confidence, ...}
    Returns:
        时间轴数据
    """
    if not analysis_results:
        return {
            'timeline': [],
            'emotion_sequence': [],
            'transitions': []
        }
    
    # 按时间戳排序
    sorted_results = sorted(analysis_results, key=lambda x: x.get('timestamp', 0))
    
    # 创建时间轴
    timeline = []
    emotion_sequence = []
    
    for i, result in enumerate(sorted_results):
        emotion = result.get('emotion_cn', result.get('emotion', 'unknown'))
        # 保留完整的帧数据，包括图片和概率分布
        timeline.append({
            'frame_number': i,
            'frame_index': result.get('frame_index', i),
            'timestamp': result.get('timestamp', 0),
            'time_formatted': result.get('time_formatted', ''),
            'emotion': result.get('emotion', ''),
            'emotion_cn': emotion,
            'confidence': result.get('confidence', 0),
            # 保留图片数据
            'original_frame': result.get('original_frame'),
            'face_image': result.get('face_image'),
            # 保留概率分布
            'probabilities': result.get('probabilities', {}),
            'probabilities_cn': result.get('probabilities_cn', {})
        })
        emotion_sequence.append(emotion)
    
    # 检测情绪转换
    transitions = []
    for i in range(1, len(emotion_sequence)):
        if emotion_sequence[i] != emotion_sequence[i-1]:
            transitions.append({
                'from': emotion_sequence[i-1],
                'to': emotion_sequence[i],
                'timestamp': sorted_results[i].get('timestamp', 0),
                'time_formatted': sorted_results[i].get('time_formatted', '')
            })
    
    return {
        'timeline': timeline,
        'emotion_sequence': emotion_sequence,
        'emotion_flow': ' → '.join(emotion_sequence),
        'transitions': transitions,
        'total_frames': len(timeline),
        'total_transitions': len(transitions)
    }


def calculate_emotion_statistics(analysis_results: List[Dict]) -> Dict:
    """
    计算情绪统计数据
    Args:
        analysis_results: 分析结果列表
    Returns:
        统计数据
    """
    if not analysis_results:
        return {}
    
    emotion_counts_cn = {}  # 中文情绪计数
    emotion_counts_en = {}  # 英文情绪计数
    total_confidence = 0
    
    for result in analysis_results:
        # 统计中文情绪
        emotion_cn = result.get('emotion_cn', 'unknown')
        emotion_counts_cn[emotion_cn] = emotion_counts_cn.get(emotion_cn, 0) + 1
        
        # 统计英文情绪
        emotion_en = result.get('emotion', 'unknown')
        emotion_counts_en[emotion_en] = emotion_counts_en.get(emotion_en, 0) + 1
        
        total_confidence += result.get('confidence', 0)
    
    total_frames = len(analysis_results)
    dominant_emotion_cn = max(emotion_counts_cn, key=emotion_counts_cn.get)
    dominant_emotion_en = max(emotion_counts_en, key=emotion_counts_en.get)
    avg_confidence = total_confidence / total_frames if total_frames > 0 else 0

    # 情绪稳定性：置信度标准差 + 情绪切换频率综合评估（0-100，越高越稳定）
    confidences = [r.get('confidence', 0) for r in analysis_results]
    emotions_seq = [r.get('emotion_cn', 'unknown') for r in analysis_results]
    if total_frames >= 2:
        mean_conf = sum(confidences) / total_frames
        conf_std = (sum((c - mean_conf) ** 2 for c in confidences) / total_frames) ** 0.5
        switches = sum(
            1 for i in range(1, total_frames) if emotions_seq[i] != emotions_seq[i - 1]
        )
        switch_rate = switches / (total_frames - 1)
        stability_score = max(0.0, min(100.0, 100 - conf_std * 120 - switch_rate * 45))
    else:
        stability_score = 100.0
    if stability_score >= 70:
        emotion_stability = '稳定'
    elif stability_score >= 40:
        emotion_stability = '一般'
    else:
        emotion_stability = '波动较大'

    return {
        'total_frames': total_frames,
        'emotion_distribution': emotion_counts_cn,  # 兼容旧代码
        'emotion_counts': emotion_counts_en,  # 英文情绪计数（用于健康数据更新）
        'emotion_counts_cn': emotion_counts_cn,  # 中文情绪计数
        'dominant_emotion': dominant_emotion_en,  # 英文主导情绪
        'dominant_emotion_cn': dominant_emotion_cn,  # 中文主导情绪
        'average_confidence': avg_confidence,  # 兼容旧代码
        'avg_confidence': avg_confidence,  # 新版本使用
        'emotion_stability': emotion_stability,  # 稳定性等级
        'stability_score': round(stability_score, 1),  # 稳定性得分
        'emotion_percentages': {
            emotion: (count / total_frames * 100)
            for emotion, count in emotion_counts_cn.items()
        }
    }
