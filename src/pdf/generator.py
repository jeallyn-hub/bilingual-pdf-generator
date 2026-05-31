# PDF生成模块
from fpdf import FPDF
from src.config.settings import *
import os

class BilingualPDF(FPDF):
    def __init__(self, title="双语对照文档"):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=MARGIN_BOTTOM)
        self.title = title
        self._setup_font()
    
    def _setup_font(self):
        """设置字体 - 尝试加载中文字体"""
        self.chinese_font_available = False
        try:
            font_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'simhei.ttf')
            if os.path.exists(font_path):
                self.add_font('SimHei', '', font_path, uni=True)
                self.chinese_font_available = True
            else:
                self.add_font('SimHei', '', 'simhei.ttf', uni=True)
                self.chinese_font_available = True
        except Exception:
            pass  # 使用默认字体
    
    def _set_font(self, size=FONT_SIZE_NORMAL, style=''):
        """统一设置字体，优先使用中文字体"""
        if self.chinese_font_available:
            # 中文字体不支持样式参数，只设置字体和大小
            self.set_font('SimHei', '', size)
        else:
            self.set_font(PDF_FONT, style, size)
    
    def header(self):
        """页头设计"""
        # 标题
        self._set_font(FONT_SIZE_TITLE, 'B')
        self.set_text_color(*COLOR_BLACK)
        self.cell(0, 10, self.title, 0, 1, 'C')
        self.ln(5)
        
        # 分隔线
        self.set_draw_color(*COLOR_GRAY)
        self.line(MARGIN_LEFT, self.get_y(), PDF_PAGE_WIDTH - MARGIN_RIGHT, self.get_y())
        self.ln(10)
    
    def footer(self):
        """页脚设计"""
        self.set_y(-15)
        self._set_font(FONT_SIZE_SMALL, 'I')
        self.set_text_color(*COLOR_GRAY)
        self.cell(0, 10, f'第 {self.page_no()} 页', 0, 0, 'C')
    
    def add_bilingual_line(self, left_text, right_text):
        """添加一行双语内容 - 左右并排显示，支持自动换行"""
        # 计算文本高度（每行大约6单位高度）
        # 使用 get_string_width 计算宽度，然后估算行数
        self._set_font(FONT_SIZE_NORMAL)
        
        # 计算左右文本的宽度
        left_width = self.get_string_width(left_text)
        right_width = self.get_string_width(right_text)
        
        # 计算需要的行数（向上取整）
        left_lines = max(1, int(left_width / COLUMN_WIDTH) + 1)
        right_lines = max(1, int(right_width / COLUMN_WIDTH) + 1)
        
        # 使用较大的行数作为单元格高度
        line_height = 6  # 每行高度
        cell_height = max(left_lines, right_lines) * line_height
        
        # 左栏（原文）
        self.set_x(MARGIN_LEFT)
        self.multi_cell(COLUMN_WIDTH, line_height, left_text, 0, 'L', False)
        
        # 计算左栏结束后的Y位置
        left_end_y = self.get_y()
        
        # 右栏（译文）- 需要回到同一行开始位置
        # 计算右栏起始位置确保左右对称
        right_col_x = PDF_PAGE_WIDTH - MARGIN_RIGHT - COLUMN_WIDTH
        self.set_y(self.get_y() - cell_height)
        self.set_x(right_col_x)
        self.multi_cell(COLUMN_WIDTH, line_height, right_text, 0, 'L', False)
        
        # 确保两栏结束后Y位置一致
        right_end_y = self.get_y()
        if left_end_y > right_end_y:
            self.set_y(left_end_y)
        
        self.ln(4)
    
    def generate_pdf(self, bilingual_pairs, output_filename=None):
        """生成双语PDF"""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        output_path = os.path.join(OUTPUT_DIR, output_filename or DEFAULT_OUTPUT_FILENAME)
        
        self.add_page()
        
        for idx, (left_text, right_text) in enumerate(bilingual_pairs, 1):
            if self.get_y() > PDF_PAGE_HEIGHT - MARGIN_BOTTOM - 20:
                self.add_page()
            
            self.add_bilingual_line(left_text, right_text)
        
        self.output(output_path)
        return output_path

def create_bilingual_pdf(bilingual_pairs, output_filename=None, title=None):
    """创建双语PDF的便捷函数"""
    pdf_title = title if title else PDF_TITLE
    pdf = BilingualPDF(title=pdf_title)
    return pdf.generate_pdf(bilingual_pairs, output_filename)