"""
视频操作业务逻辑
"""
import cv2
import numpy as np
import os
import json
from pathlib import Path
from typing import Dict, List, Optional


def analyze_image_frames(frames_folder: str, sample_interval: int = 30) -> str:
    """
    分析图像帧序列的亮度、对比度、清晰度和噪声水平
    
    Args:
        frames_folder: 存储图像帧的文件夹路径
        sample_interval: 采样间隔，每隔多少帧分析一帧，默认为30帧
    
    Returns:
        JSON格式的分析结果字符串
    """
    
    # 检查文件夹是否存在
    if not os.path.exists(frames_folder):
        return json.dumps({"error": f"文件夹不存在: {frames_folder}"})
    
    # 获取所有图像文件
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}
    image_files = []
    
    for file in os.listdir(frames_folder):
        file_path = os.path.join(frames_folder, file)
        if os.path.isfile(file_path) and Path(file).suffix.lower() in image_extensions:
            image_files.append(file_path)
    
    # 按文件名排序，确保顺序正确
    image_files.sort()
    
    if not image_files:
        return json.dumps({"error": "文件夹中没有找到图像文件"})
    
    print(f"找到 {len(image_files)} 个图像文件")
    
    # 分析结果存储
    frame_analyses = []
    analyzed_count = 0
    
    def calculate_brightness(image: np.ndarray) -> float:
        """计算图像亮度 - 转换为灰度图后的平均值"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return float(np.mean(gray))
    
    def calculate_contrast(image: np.ndarray) -> float:
        """计算图像对比度 - 使用标准差"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return float(np.std(gray))
    
    def calculate_sharpness(image: np.ndarray) -> float:
        """计算图像清晰度 - 使用拉普拉斯方差法"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())
    
    def calculate_noise_level(image: np.ndarray) -> float:
        """
        估算噪声水平 - 使用小波变换或局部方差法
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 使用中值滤波获取平滑版本
        smoothed = cv2.medianBlur(gray, 5)
        
        # 计算原图与平滑图的差异（近似噪声）
        diff = cv2.absdiff(gray, smoothed)
        
        # 返回差异的标准差作为噪声水平估计
        return float(np.std(diff))
    
    try:
        # 读取第一张图片获取分辨率信息
        first_image = cv2.imread(image_files[0])
        if first_image is None:
            return json.dumps({"error": f"无法读取第一张图片: {image_files[0]}"})
        
        height, width = first_image.shape[:2]
        
        for i, image_path in enumerate(image_files):
            # 按采样间隔进行分析
            if i % sample_interval == 0:
                # 读取图像
                image = cv2.imread(image_path)
                if image is None:
                    print(f"警告: 无法读取图片 {image_path}，跳过")
                    continue
                
                # 计算各项指标
                brightness = calculate_brightness(image)
                contrast = calculate_contrast(image)
                sharpness = calculate_sharpness(image)
                noise_level = calculate_noise_level(image)
                
                frame_analysis = {
                    "frame_index": i,
                    "frame_file": os.path.basename(image_path),
                    "brightness": round(brightness, 2),
                    "contrast": round(contrast, 2),
                    "sharpness": round(sharpness, 2),
                    "noise_level": round(noise_level, 2)
                }
                
                frame_analyses.append(frame_analysis)
                analyzed_count += 1
            
            # 进度显示
            if i % 100 == 0:
                print(f"已处理 {i}/{len(image_files)} 帧...")
                
    except Exception as e:
        return json.dumps({"error": f"分析过程中出错: {str(e)}"})
    
    # 计算整体统计信息
    if frame_analyses:
        brightness_values = [f["brightness"] for f in frame_analyses]
        contrast_values = [f["contrast"] for f in frame_analyses]
        sharpness_values = [f["sharpness"] for f in frame_analyses]
        noise_values = [f["noise_level"] for f in frame_analyses]
        
        summary = {
            "frames_info": {
                "folder_path": frames_folder,
                "total_frames": len(image_files),
                "analyzed_frames": analyzed_count,
                "sample_interval": sample_interval,
                "resolution": f"{width}x{height}",
                "file_format": Path(image_files[0]).suffix
            },
            "quality_metrics": {
                "brightness": {
                    "mean": round(np.mean(brightness_values), 2),
                    "std": round(np.std(brightness_values), 2),
                    "min": round(np.min(brightness_values), 2),
                    "max": round(np.max(brightness_values), 2),
                    "interpretation": interpret_brightness(np.mean(brightness_values))
                },
                "contrast": {
                    "mean": round(np.mean(contrast_values), 2),
                    "std": round(np.std(contrast_values), 2),
                    "min": round(np.min(contrast_values), 2),
                    "max": round(np.max(contrast_values), 2),
                    "interpretation": interpret_contrast(np.mean(contrast_values))
                },
                "sharpness": {
                    "mean": round(np.mean(sharpness_values), 2),
                    "std": round(np.std(sharpness_values), 2),
                    "min": round(np.min(sharpness_values), 2),
                    "max": round(np.max(sharpness_values), 2),
                    "interpretation": interpret_sharpness(np.mean(sharpness_values))
                },
                "noise_level": {
                    "mean": round(np.mean(noise_values), 2),
                    "std": round(np.std(noise_values), 2),
                    "min": round(np.min(noise_values), 2),
                    "max": round(np.max(noise_values), 2),
                    "interpretation": interpret_noise(np.mean(noise_values))
                }
            },
            "frame_analyses": frame_analyses,
            "enhancement_recommendations": generate_recommendations(
                np.mean(brightness_values),
                np.mean(contrast_values),
                np.mean(sharpness_values),
                np.mean(noise_values)
            )
        }
    else:
        summary = {"error": "未分析到任何有效图像帧"}
    
    return json.dumps(summary, ensure_ascii=False, indent=2)

def interpret_brightness(avg_brightness: float) -> str:
    """解释亮度值"""
    if avg_brightness < 50:
        return "偏暗"
    elif avg_brightness < 100:
        return "稍暗"
    elif avg_brightness < 150:
        return "正常"
    elif avg_brightness < 200:
        return "稍亮"
    else:
        return "过亮"

def interpret_contrast(avg_contrast: float) -> str:
    """解释对比度值"""
    if avg_contrast < 30:
        return "低对比度"
    elif avg_contrast < 50:
        return "对比度适中"
    elif avg_contrast < 80:
        return "高对比度"
    else:
        return "对比度过高"

def interpret_sharpness(avg_sharpness: float) -> str:
    """解释清晰度值"""
    if avg_sharpness < 50:
        return "非常模糊"
    elif avg_sharpness < 100:
        return "模糊"
    elif avg_sharpness < 200:
        return "清晰度一般"
    elif avg_sharpness < 500:
        return "清晰"
    else:
        return "非常清晰"

def interpret_noise(avg_noise: float) -> str:
    """解释噪声水平"""
    if avg_noise < 5:
        return "噪声很低"
    elif avg_noise < 10:
        return "噪声较低"
    elif avg_noise < 20:
        return "噪声适中"
    elif avg_noise < 30:
        return "噪声较高"
    else:
        return "噪声很高"

def generate_recommendations(avg_brightness: float, avg_contrast: float, 
                           avg_sharpness: float, avg_noise: float) -> List[str]:
    """根据分析结果生成增强建议"""
    recommendations = []
    
    # 亮度建议
    if avg_brightness < 50:
        recommendations.append("画面整体偏暗，建议进行亮度增强（伽马校正、直方图均衡化）")
    elif avg_brightness > 200:
        recommendations.append("画面整体过亮，建议降低亮度")
    elif 50 <= avg_brightness <= 150:
        recommendations.append("亮度正常，无需大幅调整")
    
    # 对比度建议
    if avg_contrast < 30:
        recommendations.append("对比度较低，建议使用对比度拉伸或CLAHE算法")
    elif avg_contrast > 80:
        recommendations.append("对比度过高，可能丢失细节")
    else:
        recommendations.append("对比度适中")
    
    # 清晰度建议
    if avg_sharpness < 100:
        recommendations.append("清晰度较低，建议使用超分辨率模型或锐化处理")
    elif avg_sharpness < 200:
        recommendations.append("清晰度一般，可考虑轻度锐化")
    else:
        recommendations.append("清晰度良好")
    
    # 噪声建议
    if avg_noise > 10:
        recommendations.append("噪声水平较高，建议进行降噪处理（中值滤波、非局部均值去噪）")
    else:
        recommendations.append("噪声水平正常")
    
    return recommendations

def get_frame_number(url: str) -> str:
    """
    统计文件夹中图片文件的数量
    
    Args:
        url: 本地图片文件夹路径
        
    Returns:
        图片统计信息字符串
    """
    try:
        folder_path = Path(url)
        
        # 检查路径是否存在
        if not folder_path.exists():
            return f"错误：路径 '{url}' 不存在"
        
        if not folder_path.is_dir():
            return f"错误：'{url}' 不是文件夹路径"
        
        # 支持的图片格式
        image_extensions = {
            '.jpg', '.jpeg', '.png'
        }
        
        # 统计图片文件
        image_files = []
        for file_path in folder_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                image_files.append(file_path.name)
        
        # 按格式分类统计
        format_count = {}
        for image_file in image_files:
            ext = Path(image_file).suffix.lower()
            format_count[ext] = format_count.get(ext, 0) + 1
        
        # 构建返回信息
        total_count = len(image_files)
        
        if total_count == 0:
            return "文件夹中没有找到图片文件"
        
        # 格式化统计信息
        result = f"总共 {total_count} 张图片\n"
        
        # 添加各格式的详细统计
        for ext, count in sorted(format_count.items()):
            result += f"{ext.upper()} 格式: {count} 张\n"
        
        return result.strip()
        
    except Exception as e:
        return f"读取文件夹时出错: {str(e)}"



# if __name__ == "__main__":
#     res = analyze_image_frames("/media/amax/xiao_20T1/code/jly/agent/llm-mcp-rag-py/data/GOT10k/GOT-10k_Train_009332",30)
#     print(res)