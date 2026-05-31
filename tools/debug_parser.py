#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试工具：分析文件内容和分隔符"""

from file_parser import read_file, detect_separator, parse_single_file, contains_chinese
import sys

def analyze_file(file_path):
    """分析文件内容"""
    print(f"正在分析文件: {file_path}")
    print("=" * 60)
    
    # 读取文件内容
    try:
        content = read_file(file_path)
        print(f"文件读取成功，共 {len(content)} 字符")
        print()
        
        # 显示前500字符预览
        print("【文件内容预览】")
        print("-" * 40)
        preview = content[:500] if len(content) > 500 else content
        print(preview)
        if len(content) > 500:
            print("...（内容已截断）")
        print()
        
        # 检测分隔符
        detected_sep = detect_separator(content)
        print(f"【自动检测到的分隔符】: {repr(detected_sep)}")
        print()
        
        # 解析内容
        print("【解析结果】")
        print("-" * 40)
        pairs = parse_single_file(content, detected_sep)
        print(f"共解析到 {len(pairs)} 条双语内容")
        
        if pairs:
            print("\n前5条解析结果：")
            for i, (original, translation) in enumerate(pairs[:5], 1):
                print(f"\n【{i}】")
                print(f"原文: {original}")
                print(f"译文: {translation}")
                print(f"原文含中文: {contains_chinese(original)}")
                print(f"译文含中文: {contains_chinese(translation)}")
        else:
            print("\n未解析到任何双语内容！")
            print("\n【可能的原因】")
            print("1. 文件中没有使用检测到的分隔符")
            print("2. 文件是单语言字幕（只有中文或只有外语）")
            print("3. 双语内容格式不符合预期")
            
            # 显示所有行，帮助用户理解
            print("\n【所有行内容】")
            lines = content.strip().split('\n')
            for i, line in enumerate(lines[:10], 1):
                print(f"{i}: {repr(line)}")
            if len(lines) > 10:
                print(f"... 还有 {len(lines) - 10} 行")
                
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python debug_parser.py <文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyze_file(file_path)