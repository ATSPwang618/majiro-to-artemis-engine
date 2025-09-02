#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGM文件名替换脚本
将AST文件中的BGM文件名替换为对应的BGM编号
"""

import os
import re
from typing import Dict, List, Tuple

def load_bgm_mapping(bgm_list_file: str) -> Dict[str, str]:
    """
    从bgm列表文件中加载文件名到BGM编号的映射
    
    Args:
        bgm_list_file: BGM列表文件路径
        
    Returns:
        文件名到BGM编号的映射字典
    """
    bgm_mapping = {}
    
    try:
        with open(bgm_list_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ' -> ' in line:
                    # 解析格式: bgm48  -> 03pi
                    parts = line.split(' -> ')
                    if len(parts) == 2:
                        bgm_num = parts[0].strip()
                        filename = parts[1].strip()
                        
                        # 添加原始文件名（小写）
                        bgm_mapping[filename.lower()] = bgm_num
                        # 添加带.ogg扩展名的版本（小写）
                        bgm_mapping[f"{filename.lower()}.ogg"] = bgm_num
                        # 添加原始大小写版本
                        bgm_mapping[filename] = bgm_num
                        bgm_mapping[f"{filename}.ogg"] = bgm_num
                        
        print(f"成功加载 {len(bgm_mapping)} 个BGM映射")
        return bgm_mapping
        
    except Exception as e:
        print(f"加载BGM映射失败: {e}")
        return {}

def replace_bgm_in_content(content: str, bgm_mapping: Dict[str, str]) -> Tuple[str, List[str]]:
    """
    在内容中替换BGM文件名
    
    Args:
        content: 文件内容
        bgm_mapping: BGM映射字典
        
    Returns:
        (替换后的内容, 未找到映射的文件名列表)
    """
    # 匹配BGM命令的正则表达式
    # 匹配类似: {"bgm",id=0,file="n04",loop=1, time=500, vol=200}
    bgm_pattern = r'(\{"bgm"[^}]*file=")([^"]+)(".*?\})'
    
    not_found = []
    
    def replace_func(match):
        prefix = match.group(1)  # {"bgm",id=0,file="
        filename = match.group(2)  # n04
        suffix = match.group(3)   # ",loop=1, time=500, vol=200}
        
        # 尝试多种匹配方式
        # 1. 原始文件名
        if filename in bgm_mapping:
            bgm_num = bgm_mapping[filename]
            return f'{prefix}{bgm_num}{suffix}'
        
        # 2. 小写文件名
        filename_lower = filename.lower()
        if filename_lower in bgm_mapping:
            bgm_num = bgm_mapping[filename_lower]
            return f'{prefix}{bgm_num}{suffix}'
        
        # 3. 带.ogg扩展名的版本
        if f"{filename}.ogg" in bgm_mapping:
            bgm_num = bgm_mapping[f"{filename}.ogg"]
            return f'{prefix}{bgm_num}{suffix}'
        
        # 4. 小写带.ogg扩展名的版本
        if f"{filename_lower}.ogg" in bgm_mapping:
            bgm_num = bgm_mapping[f"{filename_lower}.ogg"]
            return f'{prefix}{bgm_num}{suffix}'
        
        # 如果都没找到，记录并保持原样
        not_found.append(filename)
        return match.group(0)  # 保持原样
    
    new_content = re.sub(bgm_pattern, replace_func, content)
    return new_content, not_found

def process_ast_file(file_path: str, bgm_mapping: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    处理单个AST文件
    
    Args:
        file_path: AST文件路径
        bgm_mapping: BGM映射字典
        
    Returns:
        (是否成功, 未找到映射的文件名列表)
    """
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换BGM
        new_content, not_found = replace_bgm_in_content(content, bgm_mapping)
        
        # 如果有替换，写回文件
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"已更新: {file_path}")
            return True, not_found
        else:
            print(f"无需更新: {file_path}")
            return True, not_found
            
    except Exception as e:
        print(f"处理文件失败 {file_path}: {e}")
        return False, []

def find_ast_files(root_dir: str) -> List[str]:
    """
    递归查找所有AST文件
    
    Args:
        root_dir: 根目录
        
    Returns:
        AST文件路径列表
    """
    ast_files = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.ast'):
                ast_files.append(os.path.join(root, file))
    
    return ast_files

def main():
    """主函数"""
    # 配置路径
    base_dir = r"c:\Users\26241\Desktop\其他Artemis项目\水仙\水仙+Artemis\附加补充脚本"
    bgm_list_file = os.path.join(base_dir, "other-list.txt")
    ast_script_dir = os.path.join(base_dir, "转录的Artemis引擎脚本")
    
    # 检查文件和目录是否存在
    if not os.path.exists(bgm_list_file):
        print(f"BGM列表文件不存在: {bgm_list_file}")
        return
    
    if not os.path.exists(ast_script_dir):
        print(f"AST脚本目录不存在: {ast_script_dir}")
        return
    
    # 加载BGM映射
    bgm_mapping = load_bgm_mapping(bgm_list_file)
    if not bgm_mapping:
        print("无法加载BGM映射，退出")
        return
    
    # 查找所有AST文件
    ast_files = find_ast_files(ast_script_dir)
    print(f"找到 {len(ast_files)} 个AST文件")
    
    if not ast_files:
        print("未找到AST文件")
        return
    
    # 处理所有文件
    processed_count = 0
    failed_files = []
    all_not_found = set()
    
    for ast_file in ast_files:
        success, not_found = process_ast_file(ast_file, bgm_mapping)
        if success:
            processed_count += 1
            all_not_found.update(not_found)
        else:
            failed_files.append(ast_file)
    
    # 生成报告
    print(f"\n处理完成!")
    print(f"成功处理: {processed_count}/{len(ast_files)} 个文件")
    
    if failed_files:
        print(f"失败文件数: {len(failed_files)}")
        
    if all_not_found:
        print(f"未找到映射的文件名数: {len(all_not_found)}")
        
        # 输出未找到映射的文件名到TXT文件
        not_found_file = os.path.join(base_dir, "bgm_not_found.txt")
        try:
            with open(not_found_file, 'w', encoding='utf-8') as f:
                f.write("未找到BGM映射的文件名:\n")
                f.write("=" * 50 + "\n")
                for filename in sorted(all_not_found):
                    f.write(f"{filename}\n")
                f.write(f"\n总计: {len(all_not_found)} 个文件名")
            
            print(f"未找到映射的文件名已保存到: {not_found_file}")
            
        except Exception as e:
            print(f"保存未找到文件列表失败: {e}")
    
    if failed_files:
        # 输出失败文件列表
        failed_file = os.path.join(base_dir, "bgm_failed_files.txt")
        try:
            with open(failed_file, 'w', encoding='utf-8') as f:
                f.write("处理失败的文件:\n")
                f.write("=" * 50 + "\n")
                for filepath in failed_files:
                    f.write(f"{filepath}\n")
                f.write(f"\n总计: {len(failed_files)} 个文件")
            
            print(f"失败文件列表已保存到: {failed_file}")
            
        except Exception as e:
            print(f"保存失败文件列表失败: {e}")

if __name__ == "__main__":
    main()
