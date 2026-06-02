#!/usr/bin/env python3
# 打包脚本 - 将双语PDF生成工具打包成exe

import os
import subprocess
import sys

def build_exe():
    """打包程序为exe文件"""
    # 定义命令
    cmd = [
        'pyinstaller',
        '--onefile',           # 单文件模式
        '--windowed',          # 窗口模式，不显示控制台
        '--name=双语PDF生成器',  # 输出文件名
        '--add-data=src;src',   # 包含src目录
        '--add-data=example;example',  # 包含示例文件
        '--add-data=output;output',    # 包含输出目录
        '--hidden-import=fpdf',       # 隐藏导入fpdf2
        '--hidden-import=tkinter',    # 隐藏导入tkinter
        'main.py'              # 入口文件
    ]
    
    print("🚀 开始打包...")
    print(f"命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功!")
        print(f"输出目录: dist/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败!")
        print(f"错误信息: {e.stderr}")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    build_exe()