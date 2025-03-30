import os
import re
import hashlib
import difflib
from collections import defaultdict
import argparse
from mutagen import File
import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import shutil
import logging
import sys
# from hanziconv import HanziConv  # 导入繁简体转换库 (V0.1版本暂不支持繁简体转换)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入现有的函数
from py import (
    get_audio_files, get_metadata,
    calculate_audio_fingerprint, handle_duplicates
)

# 定义find_duplicates函数
def find_duplicates(audio_files, similarity_threshold=0.8):
    """查找重复文件 (V0.1版本暂不支持繁简体转换)"""
    # 按文件大小分组（相同大小的文件可能是完全相同的）
    size_groups = defaultdict(list)
    for file_path in audio_files:
        file_size = os.path.getsize(file_path)
        size_groups[file_size].append(file_path)
    
    # 存储已确认的重复文件组
    duplicate_groups = []
    processed_files = set()
    
    # 首先检查完全相同大小的文件
    for size, files in size_groups.items():
        if len(files) > 1:
            # 计算文件哈希以确认它们是否真的相同
            hash_dict = defaultdict(list)
            for file_path in files:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                hash_dict[file_hash].append(file_path)
            
            # 添加哈希相同的文件组
            for hash_val, duplicate_files in hash_dict.items():
                if len(duplicate_files) > 1:
                    duplicate_groups.append(duplicate_files)
                    processed_files.update(duplicate_files)
    
    # 对于未处理的文件，使用文件名和音频指纹进行比较
    remaining_files = [f for f in audio_files if f not in processed_files]
    
    # 提取文件信息
    file_info = {}
    for file_path in remaining_files:
        normalized_name = normalize_filename(file_path)
        possible_artist_title = extract_artist_title(file_path)
        metadata_artist, metadata_title, has_cover, has_lyrics = get_metadata(file_path)
        fingerprint = calculate_audio_fingerprint(file_path)
        
        file_info[file_path] = {
            'normalized_name': normalized_name,
            'possible_artist_title': possible_artist_title,
            'metadata_artist': metadata_artist,
            'metadata_title': metadata_title,
            'fingerprint': fingerprint,
            'has_cover': has_cover,
            'has_lyrics': has_lyrics
        }
    
    # 比较文件
    potential_duplicates = defaultdict(list)
    
    for i, file1 in enumerate(remaining_files):
        for file2 in remaining_files[i+1:]:
            if file1 == file2 or file1 in processed_files or file2 in processed_files:
                continue
            
            info1 = file_info[file1]
            info2 = file_info[file2]
            
            # 计算文件名相似度
            name_similarity = difflib.SequenceMatcher(None, 
                                                     info1['normalized_name'], 
                                                     info2['normalized_name']).ratio()
            
            # V0.1版本暂不支持繁简体转换
            # 特别检查：如果文件名完全相同，则设置相似度为1.0
            if info1['normalized_name'] == info2['normalized_name']:
                name_similarity = 1.0
            
            # 检查艺术家和标题是否匹配
            metadata_match = False
            
            # 检查元数据
            if (info1['metadata_artist'] and info1['metadata_title'] and 
                info2['metadata_artist'] and info2['metadata_title']):
                if (info1['metadata_artist'].lower() == info2['metadata_artist'].lower() and 
                    info1['metadata_title'].lower() == info2['metadata_title'].lower()):
                    metadata_match = True
            
            # 检查从文件名提取的艺术家和标题
            artist_title_match = False
            for at1 in info1['possible_artist_title']:
                for at2 in info2['possible_artist_title']:
                    # 检查是否有艺术家和标题的交换匹配
                    if ((at1[0].lower() == at2[0].lower() and at1[1].lower() == at2[1].lower()) or
                        (at1[0].lower() == at2[1].lower() and at1[1].lower() == at2[0].lower())):
                        artist_title_match = True
                        break
            
            # 检查音频指纹
            fingerprint_match = False
            if info1['fingerprint'] and info2['fingerprint']:
                fp1 = np.array(info1['fingerprint'])
                fp2 = np.array(info2['fingerprint'])
                
                # 确保长度相同
                min_len = min(len(fp1), len(fp2))
                if min_len > 0:
                    fp1 = fp1[:min_len]
                    fp2 = fp2[:min_len]
                    
                    # 计算相似度
                    try:
                        correlation = np.corrcoef(fp1, fp2)[0, 1]
                        if not np.isnan(correlation) and correlation > 0.8:
                            fingerprint_match = True
                    except:
                        pass
            
            # 如果文件名相似度高或元数据/艺术家标题匹配，则认为可能是重复的
            if (name_similarity > similarity_threshold or 
                metadata_match or artist_title_match or fingerprint_match):
                
                # 使用文件1作为组标识
                group_key = file1
                potential_duplicates[group_key].append(file2)
                processed_files.add(file2)
    
    # 将潜在重复文件添加到结果中
    for file1, duplicates in potential_duplicates.items():
        if duplicates:  # 确保有重复文件
            group = [file1] + duplicates
            duplicate_groups.append(group)
    
    return duplicate_groups

# 定义normalize_filename函数 (V0.1版本暂不支持繁简体转换)
def normalize_filename(filename):
    """标准化文件名，移除扩展名和特殊字符"""
    base_name = os.path.splitext(os.path.basename(filename))[0]
    # 移除特殊字符，保留字母、数字和中文
    normalized = re.sub(r'[^\w\u4e00-\u9fff]', '', base_name.lower())
    return normalized

# 定义extract_artist_title函数 (V0.1版本暂不支持繁简体转换)
def extract_artist_title(filename):
    """尝试从文件名中提取艺术家和标题"""
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # 尝试常见的分隔模式: "艺术家 - 标题" 或 "标题 - 艺术家"
    patterns = [
        r'^(.*?)\s*[\-_]\s*(.*?)$',  # 艺术家 - 标题 或 标题 - 艺术家
        r'^(.*?)\s*[_\s]\s*(.*?)$',  # 艺术家_标题 或 艺术家 标题
    ]
    
    for pattern in patterns:
        match = re.match(pattern, base_name)
        if match:
            part1, part2 = match.groups()
            # 返回两种可能的组合，让后续比较决定哪个更可能是正确的
            return [(part1.strip(), part2.strip()), (part2.strip(), part1.strip())]
    
    # 如果无法匹配，返回整个文件名作为标题，艺术家为空
    return [(base_name, ""), ("", base_name)]

def get_user_preferences():
    """获取用户的优先级选择"""
    print("\n欢迎使用音乐文件去重系统!")
    print("在处理重复文件时，我们需要知道您的优先级选择。\n")
    
    # 获取用户对封面的偏好
    prefer_cover = input("是否优先保留有封面的文件? (y/n): ").lower().startswith('y')
    
    # 获取用户对歌词的偏好
    prefer_lyrics = input("是否优先保留有歌词的文件? (y/n): ").lower().startswith('y')
    
    # 获取用户对音质的偏好
    prefer_quality = input("是否优先保留质量高的文件(通常是比特率更高的文件)? (y/n): ").lower().startswith('y')
    
    # 获取用户对操作的选择
    print("\n请选择对重复文件的操作:")
    print("1. 仅报告重复文件")
    print("2. 移动重复文件到指定目录")
    print("3. 删除重复文件")
    
    action_choice = input("请输入选项编号 (1/2/3): ")
    
    if action_choice == '1':
        action = 'report'
    elif action_choice == '2':
        action = 'move'
    elif action_choice == '3':
        action = 'delete'
    else:
        print("无效选择，默认为仅报告模式")
        action = 'report'
    
    # 如果选择移动，获取输出目录
    output_dir = 'duplicates'
    if action == 'move':
        output_dir = input("请输入重复文件的输出目录 (默认为'duplicates'): ") or 'duplicates'
    
    # 获取相似度阈值
    threshold_str = input("请输入文件名相似度阈值 (0-1, 默认为0.8): ") or '0.8'
    try:
        threshold = float(threshold_str)
        if threshold < 0 or threshold > 1:
            print("阈值必须在0-1之间，使用默认值0.8")
            threshold = 0.8
    except ValueError:
        print("无效的阈值，使用默认值0.8")
        threshold = 0.8
    
    return {
        'prefer_cover': prefer_cover,
        'prefer_lyrics': prefer_lyrics,
        'prefer_quality': prefer_quality,
        'action': action,
        'output_dir': output_dir,
        'threshold': threshold
    }

def calculate_bitrate(file_path):
    """计算音频文件的比特率"""
    try:
        file_size = os.path.getsize(file_path)  # 文件大小（字节）
        audio = AudioSegment.from_file(file_path)
        duration_seconds = len(audio) / 1000.0  # 持续时间（秒）
        
        # 比特率 = 文件大小(位) / 持续时间(秒)
        bitrate = (file_size * 8) / duration_seconds
        return bitrate / 1000  # 转换为kbps
    except Exception as e:
        logger.debug(f"无法计算 {file_path} 的比特率: {e}")
        return 0

def enhanced_handle_duplicates(duplicate_groups, output_dir, action, prefer_cover=False, prefer_lyrics=False, prefer_quality=False):
    """增强版的重复文件处理函数，包含比特率信息"""
    if not duplicate_groups:
        logger.info("未找到重复文件")
        return
    
    logger.info(f"找到 {len(duplicate_groups)} 组重复文件")
    
    # 创建输出目录（如果需要）
    if action == 'move' and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 处理每组重复文件
    for i, group in enumerate(duplicate_groups, 1):
        logger.info(f"\n重复组 {i}:")
        
        # 获取每个文件的信息
        file_details = []
        for file_path in group:
            file_size = os.path.getsize(file_path)
            metadata_artist, metadata_title, has_cover, has_lyrics = get_metadata(file_path)
            bitrate = calculate_bitrate(file_path)
            
            file_details.append({
                'path': file_path,
                'size': file_size,
                'has_cover': has_cover,
                'has_lyrics': has_lyrics,
                'bitrate': bitrate,
                'artist': metadata_artist,
                'title': metadata_title
            })
        
        # 根据用户偏好对文件进行排序
        def sort_key(file_detail):
            # 创建一个排序键，优先级按照用户设置
            score = 0
            
            # 如果优先保留有封面的文件
            if prefer_cover and file_detail['has_cover']:
                score += 1000  # 给予较高权重
            
            # 如果优先保留有歌词的文件
            if prefer_lyrics and file_detail['has_lyrics']:
                score += 500  # 给予较高权重
            
            # 如果优先保留质量高的文件
            if prefer_quality:
                # 使用比特率作为质量指标
                score += file_detail['bitrate'] * 2  # 给比特率更高的权重
            else:
                # 默认使用文件大小作为基础分数
                score += file_detail['size'] / 1024
            
            return score
        
        # 按照排序键对文件进行排序
        sorted_files = sorted(file_details, key=sort_key, reverse=True)
        
        # 显示文件信息
        for j, file_detail in enumerate(sorted_files):
            file_path = file_detail['path']
            file_size = file_detail['size']
            has_cover = "有" if file_detail['has_cover'] else "无"
            has_lyrics = "有" if file_detail['has_lyrics'] else "无"
            bitrate = file_detail['bitrate']
            artist = file_detail['artist'] or "未知艺术家"
            title = file_detail['title'] or "未知标题"
            
            keep_flag = " [保留]" if j == 0 else ""
            logger.info(f"  {j+1}. {file_path} ({file_size/1024/1024:.2f} MB, {bitrate:.0f} kbps) [封面:{has_cover}, 歌词:{has_lyrics}] - {artist} - {title}{keep_flag}")
        
        # 处理重复文件（保留第一个，处理其余的）
        if action != 'report' and len(sorted_files) > 1:
            for file_detail in sorted_files[1:]:
                file_path = file_detail['path']
                if action == 'delete':
                    try:
                        os.remove(file_path)
                        logger.info(f"  已删除: {file_path}")
                    except Exception as e:
                        logger.error(f"  删除失败 {file_path}: {e}")
                elif action == 'move':
                    try:
                        dest_path = os.path.join(output_dir, os.path.basename(file_path))
                        # 如果目标文件已存在，添加数字后缀
                        if os.path.exists(dest_path):
                            base, ext = os.path.splitext(dest_path)
                            counter = 1
                            while os.path.exists(f"{base}_{counter}{ext}"):
                                counter += 1
                            dest_path = f"{base}_{counter}{ext}"
                        
                        shutil.move(file_path, dest_path)
                        logger.info(f"  已移动: {file_path} -> {dest_path}")
                    except Exception as e:
                        logger.error(f"  移动失败 {file_path}: {e}")

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("用法: python search.py [目录路径]")
        print("如果不提供目录路径，将会提示输入")
        sys.exit(0)
    
    # 获取目录路径
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = input("请输入要扫描的目录路径: ")
    
    if not os.path.isdir(directory):
        print(f"错误: '{directory}' 不是有效的目录路径")
        sys.exit(1)
    
    # 获取用户偏好
    preferences = get_user_preferences()
    
    logger.info(f"开始扫描目录: {directory}")
    audio_files = get_audio_files(directory)
    
    if not audio_files:
        logger.info("未找到音频文件")
        return
    
    logger.info("查找重复文件中...")
    duplicate_groups = find_duplicates(audio_files, preferences['threshold'])
    
    logger.info(f"处理重复文件 (操作: {preferences['action']})...")
    enhanced_handle_duplicates(
        duplicate_groups, 
        preferences['output_dir'], 
        preferences['action'],
        prefer_cover=preferences['prefer_cover'],
        prefer_lyrics=preferences['prefer_lyrics'],
        prefer_quality=preferences['prefer_quality']
    )
    
    logger.info("处理完成")

if __name__ == "__main__":
    main()