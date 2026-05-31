# 双语PDF生成工具

一个用于将双语内容合并成对照PDF的Python工具。支持单文件和双文件两种模式，输出左右两栏布局的PDF文档。

## 🎯 功能特点

- **单文件模式**: 处理包含原文和译文的单个文件（用分隔符分隔）
- **双文件模式**: 分别读取原文文件和译文文件，自动对齐合并
- **PDF输出**: 生成左右两栏对照格式的PDF文档
- **中文支持**: 完美支持中文字体显示
- **灵活配置**: 支持自定义输出文件名和布局参数

## 📁 项目结构

```
BilingualPDF/
├── main.py              # 主启动文件
├── pdf_generator.py     # PDF生成模块
├── file_parser.py       # 文件解析模块
├── config.py            # 配置文件
├── requirements.txt     # 依赖列表
├── README.md           # 说明文档
├── example/            # 示例文件目录
│   ├── single_file.txt   # 单文件模式示例
│   ├── english.txt      # 原文示例
│   └── chinese.txt      # 译文示例
└── output/             # 输出目录
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install fpdf2
```

### 2. 运行程序
```bash
cd "d:\如月\Code\Trae\VibeLearning\BilingualPDF"
python main.py
```

### 3. 选择模式
- **模式1（单文件）**: 文件中每行格式为 `原文|||译文`
- **模式2（双文件）**: 分别选择原文文件和译文文件

## 📖 使用示例

### 单文件模式

输入文件格式（每行一条双语内容）：
```
Hello|||你好
How are you?|||你好吗？
Goodbye|||再见
```

### 双文件模式

原文文件（english.txt）：
```
Hello
How are you?
Goodbye
```

译文文件（chinese.txt）：
```
你好
你好吗？
再见
```

## ⚙️ 配置说明

在 `config.py` 中可以自定义以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| PDF_TITLE | PDF标题 | 双语对照文档 |
| PDF_FONT_SIZE | 字体大小 | 10 |
| COLUMN_WIDTH | 栏宽度 | 80 |
| COLUMN_SPACING | 栏间距 | 10 |
| MARGIN_* | 页边距 | 15-20 |

## 📝 支持的文件格式

- `.txt` - 纯文本文件
- `.md` - Markdown文件

## 🎨 输出效果

生成的PDF文档特点：
- 左侧：英语/日语原文
- 右侧：中文翻译
- 自动分页
- 包含页眉和页脚
- 页码自动生成

## 📦 依赖

- **fpdf2**: PDF生成库
- **Python**: 3.8+

## 📄 许可证

MIT License

---

**注意**: 使用前请确保系统中安装了支持中文的字体。