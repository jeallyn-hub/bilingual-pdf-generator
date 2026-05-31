#!/usr/bin/env python3
# 测试脚本 - 自动生成双语PDF

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_single_file_mode():
    """测试单文件模式"""
    print("=== 测试单文件模式 ===")
    
    from file_parser import read_file, parse_single_file
    from pdf_generator import create_bilingual_pdf
    
    # 读取示例文件
    example_file = "example/single_file.txt"
    content = read_file(example_file)
    
    # 解析内容
    bilingual_pairs = parse_single_file(content)
    print(f"解析到 {len(bilingual_pairs)} 条双语内容")
    
    # 生成PDF
    output_path = create_bilingual_pdf(bilingual_pairs, "single_file_output.pdf")
    print(f"单文件模式测试完成！输出: {output_path}")
    print()

def test_double_file_mode():
    """测试双文件模式"""
    print("=== 测试双文件模式 ===")
    
    from file_parser import read_file, parse_double_files
    from pdf_generator import create_bilingual_pdf
    
    # 读取示例文件
    source_content = read_file("example/english.txt")
    target_content = read_file("example/chinese.txt")
    
    # 解析内容
    bilingual_pairs = parse_double_files(source_content, target_content)
    print(f"解析到 {len(bilingual_pairs)} 条双语内容")
    
    # 生成PDF
    output_path = create_bilingual_pdf(bilingual_pairs, "double_file_output.pdf")
    print(f"双文件模式测试完成！输出: {output_path}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("    双语PDF生成工具 - 测试脚本")
    print("=" * 60)
    print()
    
    try:
        test_single_file_mode()
        test_double_file_mode()
        print("✅ 所有测试通过！")
        print("PDF文件已生成在 output/ 目录下")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()