# 配置文件
import os

# PDF配置
PDF_TITLE = "双语对照文档"
PDF_AUTHOR = "Bilingual PDF Generator"
PDF_FONT = "Helvetica"
PDF_FONT_SIZE = 10
PDF_PAGE_WIDTH = 210  # A4宽度（毫米）
PDF_PAGE_HEIGHT = 297  # A4高度（毫米）

# 页面布局配置
MARGIN_LEFT = 15
MARGIN_RIGHT = 15
MARGIN_TOP = 20
MARGIN_BOTTOM = 20
COLUMN_WIDTH = 80  # 每栏宽度
COLUMN_SPACING = 10  # 栏间距

# 字体配置
FONT_SIZE_SMALL = 8
FONT_SIZE_NORMAL = 10
FONT_SIZE_LARGE = 12
FONT_SIZE_TITLE = 16

# 颜色配置
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (240, 240, 240)

# 输出配置
OUTPUT_DIR = "output"
DEFAULT_OUTPUT_FILENAME = "bilingual_output.pdf"

# 输入文件配置
SUPPORTED_EXTENSIONS = [".txt", ".md", ".src", ".srt", ".ass"]

# 分隔符配置（单文件模式使用）
DEFAULT_SEPARATOR = "|||"  # 用于分隔原文和翻译的标记
LINE_SEPARATOR = "\n"  # 行分隔符