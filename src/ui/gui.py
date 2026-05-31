# 图形界面模块
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from src.parser.file_parser import detect_separator, parse_single_file, parse_double_files, read_file, validate_file_path
from src.pdf.generator import create_bilingual_pdf
from src.config.settings import SUPPORTED_EXTENSIONS, DEFAULT_SEPARATOR, OUTPUT_DIR

class BilingualPDFGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("双语PDF生成工具")
        self.root.geometry("900x600")
        
        # 初始化状态
        self.mode = tk.StringVar(value="single")  # single 或 double
        self.source_file = tk.StringVar()
        self.target_file = tk.StringVar()
        self.separator = tk.StringVar(value=DEFAULT_SEPARATOR)
        self.detected_separator = tk.StringVar()  # 新增：存储检测到的分隔符
        self.preview_text_var = tk.StringVar()  # 修改变量名，避免与方法名冲突
        self.parsed_pairs = []
        
        # 新增：文档标题和输出文件名
        self.document_title = tk.StringVar(value="双语对照文档")
        self.output_filename = tk.StringVar()
        
        # 创建UI
        self.create_widgets()
    
    def _browse_file(self, var):
        """通用文件浏览方法"""
        filename = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[("所有支持的文件", "*.srt *.ass *.txt"), ("SRT字幕", "*.srt"), ("ASS字幕", "*.ass"), ("文本文件", "*.txt")]
        )
        if filename:
            var.set(filename)
            # 如果是单文件模式，自动检测分隔符
            if self.mode.get() == "single" and var == self.source_file:
                try:
                    content = read_file(filename)
                    detected = detect_separator(content)
                    self.separator.set(detected)
                except Exception as e:
                    messagebox.showwarning("警告", f"检测分隔符失败: {str(e)}")
            
            # 自动填充输出文件名（使用源文件的基本名）
            if var == self.source_file:
                base_name = os.path.splitext(os.path.basename(filename))[0]
                self.output_filename.set(f"{base_name}_双语对照")
    
    def browse_single_file(self):
        """浏览单文件"""
        self._browse_file(self.source_file)
    
    def browse_source_file(self):
        """浏览原文文件"""
        self._browse_file(self.source_file)
    
    def browse_target_file(self):
        """浏览译文文件"""
        self._browse_file(self.target_file)
    
    def open_output_dir(self):
        """打开输出目录"""
        if os.path.exists(OUTPUT_DIR):
            os.startfile(OUTPUT_DIR)
        else:
            messagebox.showwarning("警告", "输出目录不存在")
    
    def switch_mode(self):
        """切换单文件/双文件模式"""
        mode = self.mode.get()
        if mode == "single":
            # 单文件模式：显示分隔符设置，隐藏译文文件选择
            self.separator_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky="we")
            self.target_label.grid_remove()
            self.target_entry.grid_remove()
            self.browse_target_button.grid_remove()
        else:
            # 双文件模式：隐藏分隔符设置，显示译文文件选择
            self.separator_frame.grid_remove()
            self.target_label.grid(row=2, column=0, sticky="w")
            self.target_entry.grid(row=2, column=1, pady=5, sticky="we")
            self.browse_target_button.grid(row=2, column=2, pady=5)
    
    def preview_content(self):
        """预览内容（统一入口）"""
        if self.mode.get() == "single":
            self._preview_single_file()
        else:
            self._preview_double_files()
    
    def _preview_single_file(self):
        """单文件模式预览处理"""
        try:
            file_path = self.source_file.get()
            if not file_path:
                messagebox.showwarning("警告", "请选择文件")
                return
            
            content = read_file(file_path)
            
            # 检测分隔符
            detected_sep = detect_separator(content)
            self.detected_separator.set(f"检测到分隔符: {detected_sep}")
            
            # 使用检测到的分隔符或用户自定义的分隔符
            separator = self.separator.get().strip() or detected_sep
            
            # 单文件模式解析
            self.parsed_pairs = parse_single_file(content, separator)
            
            self._display_preview()
            
        except Exception as e:
            messagebox.showerror("错误", f"解析失败: {str(e)}")
    
    def _preview_double_files(self):
        """双文件模式预览处理"""
        try:
            source_path = self.source_file.get()
            target_path = self.target_file.get()
            
            if not source_path or not target_path:
                messagebox.showwarning("警告", "请选择原文和译文文件")
                return
            
            source_content = read_file(source_path)
            target_content = read_file(target_path)
            
            # 双文件模式解析
            self.parsed_pairs = parse_double_files(source_content, target_content)
            
            self._display_preview()
            
        except Exception as e:
            messagebox.showerror("错误", f"解析失败: {str(e)}")
    
    def _display_preview(self):
        """显示预览内容（两个模式共用）"""
        if not self.parsed_pairs:
            self.preview_text_var.set("未解析到任何双语内容")
            self._update_preview_text()
            return
        
        # 显示前10条预览
        preview_lines = []
        for i, (original, translation) in enumerate(self.parsed_pairs[:10], 1):
            preview_lines.append(f"{i}. {original}")
            preview_lines.append(f"   {translation}")
            preview_lines.append("")
        
        preview_lines.append(f"\n共解析到 {len(self.parsed_pairs)} 条双语内容")
        self.preview_text_var.set("\n".join(preview_lines))
        self._update_preview_text()  # 直接调用更新预览文本
    
    def generate_pdf(self):
        """生成PDF"""
        if not self.parsed_pairs:
            messagebox.showwarning("警告", "请先预览内容")
            return
        
        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        try:
            # 获取输出文件名
            output_name = self.output_filename.get().strip()
            if not output_name:
                base_name = os.path.splitext(os.path.basename(self.source_file.get()))[0]
                output_name = f"{base_name}_双语对照"
            
            # 获取文档标题
            doc_title = self.document_title.get().strip()
            
            output_path = create_bilingual_pdf(self.parsed_pairs, output_name + ".pdf", doc_title)
            messagebox.showinfo("成功", f"PDF已生成！\n\n{output_path}")
            
            # 自动打开输出目录
            os.startfile(OUTPUT_DIR)
        except Exception as e:
            messagebox.showerror("错误", f"生成PDF失败: {str(e)}")
    
    def create_widgets(self):
        """创建界面组件"""
        # 模式选择
        self.create_mode_selection()
        
        # 文件选择
        self.create_file_selection()
        
        # 分隔符设置（单文件模式）
        self.create_separator_frame()
        
        # 文档设置
        self.create_document_settings()
        
        # 预览区域
        self.create_preview_area()
        
        # 按钮区域
        self.create_button_area()
    
    def create_mode_selection(self):
        """创建模式选择区域"""
        mode_frame = ttk.LabelFrame(self.root, text="模式选择")
        mode_frame.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="we")
        
        ttk.Radiobutton(mode_frame, text="单文件模式", variable=self.mode, value="single", 
                        command=self.switch_mode).grid(row=0, column=0, padx=20)
        ttk.Radiobutton(mode_frame, text="双文件模式", variable=self.mode, value="double", 
                        command=self.switch_mode).grid(row=0, column=1, padx=20)
    
    def create_file_selection(self):
        """创建文件选择区域"""
        # 原文文件
        self.source_label = ttk.Label(self.root, text="原文文件：")
        self.source_label.grid(row=1, column=0, sticky="w", padx=10)
        
        self.source_entry = ttk.Entry(self.root, textvariable=self.source_file, width=50)
        self.source_entry.grid(row=1, column=1, pady=5, sticky="we", padx=5)
        
        self.browse_source_button = ttk.Button(self.root, text="浏览", command=self.browse_source_file)
        self.browse_source_button.grid(row=1, column=2, pady=5, padx=5)
        
        # 译文文件（默认隐藏，切换到双文件模式时显示）
        self.target_label = ttk.Label(self.root, text="译文文件：")
        self.target_entry = ttk.Entry(self.root, textvariable=self.target_file, width=50)
        self.browse_target_button = ttk.Button(self.root, text="浏览", command=self.browse_target_file)
    
    def create_separator_frame(self):
        """创建分隔符设置区域"""
        self.separator_frame = ttk.LabelFrame(self.root, text="分隔符设置")
        self.separator_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky="we")
        
        ttk.Label(self.separator_frame, text="分隔符：").grid(row=0, column=0, padx=10)
        self.separator_entry = ttk.Entry(self.separator_frame, textvariable=self.separator, width=20)
        self.separator_entry.grid(row=0, column=1, padx=5)
        
        # 快速选择常用分隔符
        common_separators = ['|||', '\\\\N', '\\N', '|', '/', '@@@', '\t']
        for i, sep in enumerate(common_separators):
            ttk.Button(self.separator_frame, text=f"'{sep}'", 
                      command=lambda s=sep: self.separator.set(s)).grid(row=0, column=i+2, padx=5)
    
    def create_document_settings(self):
        """创建文档设置区域"""
        settings_frame = ttk.LabelFrame(self.root, text="文档设置")
        settings_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="we")
        
        # 文档标题
        ttk.Label(settings_frame, text="文档标题：").grid(row=0, column=0, padx=10, sticky="w")
        self.title_entry = ttk.Entry(settings_frame, textvariable=self.document_title, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 输出文件名
        ttk.Label(settings_frame, text="输出文件名：").grid(row=1, column=0, padx=10, sticky="w")
        self.filename_entry = ttk.Entry(settings_frame, textvariable=self.output_filename, width=40)
        self.filename_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(settings_frame, text=".pdf").grid(row=1, column=2, padx=5)
    
    def create_preview_area(self):
        """创建预览区域"""
        preview_frame = ttk.LabelFrame(self.root, text="内容预览")
        preview_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")
        
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        self.preview_text = tk.Text(preview_frame, wrap="word", height=15)
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(preview_frame, command=self.preview_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.preview_text.config(yscrollcommand=scrollbar.set)
        
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定变量更新
        self.preview_text_var.trace("w", lambda *args: self._update_preview_text())
    
    def _update_preview_text(self):
        """更新预览文本框内容"""
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, self.preview_text_var.get())
    
    def create_button_area(self):
        """创建按钮区域"""
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="预览内容", command=self.preview_content).pack(side="left", padx=10)
        ttk.Button(button_frame, text="生成PDF", command=self.generate_pdf).pack(side="left", padx=10)
        ttk.Button(button_frame, text="打开输出目录", command=self.open_output_dir).pack(side="left", padx=10)