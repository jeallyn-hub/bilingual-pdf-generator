# 文件解析模块
from src.config.settings import DEFAULT_SEPARATOR, SUPPORTED_EXTENSIONS
import os
import re

# 常见分隔符列表
COMMON_SEPARATORS = [
    '|||',      # 三竖线（默认）
    '\\\\N',    # ASS字幕中日双语分隔符（双反斜杠+N）
    '\\N',      # ASS字幕换行符
    '|',        # 单竖线
    '//',       # 双斜杠
    '/',        # 单斜杠
    '@@@',      # 三@
    '@@',       # 双@
    '@',        # 单@
    '---',      # 三横线
    '--',       # 双横线
    '+++',      # 三加号
    ':::',      # 三冒号
    '>>>',      # 三大于号
    '<<<',      # 三小于号
    '##',       # 双#
    '#',        # 单#
    '\t',       # 制表符
]

# 元数据过滤关键字（统一管理）
METADATA_KEYWORDS = [
    '字幕', '翻译', '校对', '特效', '后期', '总监', 
    '压制', '时间轴', '轴', '双语合并', 'WEB版', '外挂字幕',
    'staff', 'STAFF', 'Staff'
]

def detect_separator(content):
    """
    自动检测文件内容中的分隔符
    
    参数:
        content: 文件内容字符串
    
    返回:
        检测到的分隔符，如果无法确定则返回默认分隔符
    """
    if not content:
        return DEFAULT_SEPARATOR
    
    lines = content.strip().split('\n')
    # 只取前20行进行分析，避免性能问题
    sample_lines = lines[:20]
    
    separator_scores = {}
    
    for sep in COMMON_SEPARATORS:
        score = 0
        for line in sample_lines:
            line = line.strip()
            if sep in line:
                parts = line.split(sep, 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    # 分隔符两边都有内容，加分
                    score += 1
                    # 如果两边内容看起来像是双语对（中英文混合），再加一分
                    left_has_chinese = contains_chinese(parts[0])
                    right_has_chinese = contains_chinese(parts[1])
                    if left_has_chinese != right_has_chinese:
                        score += 1
        separator_scores[sep] = score
    
    # 找到得分最高的分隔符
    if separator_scores:
        best_separator = max(separator_scores, key=separator_scores.get)
        # 如果最高分大于0，返回该分隔符；否则返回默认分隔符
        if separator_scores[best_separator] > 0:
            return best_separator
    
    return DEFAULT_SEPARATOR

def parse_srt_to_text(srt_content):
    """解析SRT字幕文件，提取纯文本内容
    支持双语字幕格式：每个字幕块包含两行（中文在上，英文在下）"""
    lines = srt_content.split('\n')
    result = []
    current_subtitle = []
    
    for line in lines:
        line = line.strip()
        # 跳过空行、纯数字行（序号）、时间码行
        if not line or line.isdigit() or ' --> ' in line or re.match(r'^\d{2}:\d{2}:\d{2}', line):
            # 如果当前字幕块有内容，处理它
            if current_subtitle:
                # 检查是否是双语字幕（两行内容）
                if len(current_subtitle) >= 2:
                    # 第一行是中文，第二行是英文，用分隔符连接
                    chinese = current_subtitle[0]
                    english = current_subtitle[1]
                    # 确保中文在右边（译文位置）
                    if contains_chinese(chinese) and not contains_chinese(english):
                        result.append(f"{english}{DEFAULT_SEPARATOR}{chinese}")
                    else:
                        result.append('\n'.join(current_subtitle))
                else:
                    result.append('\n'.join(current_subtitle))
                current_subtitle = []
            continue
        
        current_subtitle.append(line)
    
    # 处理最后一个字幕块
    if current_subtitle:
        if len(current_subtitle) >= 2:
            chinese = current_subtitle[0]
            english = current_subtitle[1]
            if contains_chinese(chinese) and not contains_chinese(english):
                result.append(f"{english}{DEFAULT_SEPARATOR}{chinese}")
            else:
                result.append('\n'.join(current_subtitle))
        else:
            result.append('\n'.join(current_subtitle))
    
    return '\n'.join(result)

def parse_ass_to_text(ass_content):
    """解析ASS字幕文件，提取纯文本内容"""
    lines = ass_content.split('\n')
    result = []
    in_events_section = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # 检查是否进入[Events]部分
        if line.startswith('[Events]'):
            in_events_section = True
            continue
        
        # 如果遇到其他[开头的部分，说明Events部分结束
        if in_events_section and line.startswith('['):
            break
        
        # 在Events部分中查找Dialogue行
        if in_events_section and line.startswith('Dialogue:'):
            # Dialogue格式: Dialogue: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
            parts = line.split(',', 9)
            if len(parts) >= 10:
                text = re.sub(r'{[^}]*}', '', parts[9]).strip()
                # 先保护中日双语分隔符 \\N，再处理其他转义字符
                text = text.replace(r'\\N', '\x00').replace(r'\n', '\n').replace(r'\h', '').replace(r'\t', '\t').replace(r'\r', '').replace('\x00', r'\\N')
                
                # 过滤元数据内容
                if text:
                    starts_with_keyword = any(text.startswith(keyword) for keyword in METADATA_KEYWORDS)
                    if starts_with_keyword:
                        continue
                    
                    contains_keyword = any(keyword in text for keyword in METADATA_KEYWORDS)
                    if contains_keyword and text.count(' ') >= 3:
                        continue
                    
                    result.append(text)
    
    return '\n'.join(result)

def read_file(file_path):
    """读取文件内容，支持多种编码格式"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {ext}。支持的格式: {SUPPORTED_EXTENSIONS}")
    
    # 尝试多种编码格式读取文件
    encodings = ['utf-8', 'utf-16', 'gbk', 'gb2312', 'big5', 'utf-8-sig']
    
    content = None
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, LookupError):
            continue
    
    if content is None:
        raise ValueError(f"无法读取文件 {file_path}，尝试了以下编码: {encodings}")
    
    # 如果是SRT文件，进行预处理提取纯文本
    if ext.lower() == '.srt':
        content = parse_srt_to_text(content)
    
    # 如果是ASS文件，进行预处理提取纯文本
    if ext.lower() == '.ass':
        content = parse_ass_to_text(content)
    
    return content

def contains_chinese(text):
    """检测文本是否包含中文字符"""
    return any('\u4e00' <= c <= '\u9fff' for c in text)

def is_metadata_line(line):
    """判断是否是元数据行（需要过滤）"""
    if not line or not line.strip():
        return True
    
    line = line.strip()
    
    # 时间戳格式：(1983年11月12日)
    if line.startswith('(') and line.endswith(')') and len(line) <= 20:
        return True
    
    # 章节标题：第 1 章:xxx
    if line.startswith('第') and '章' in line:
        return True
    
    # 字幕制作信息
    if any(keyword in line for keyword in METADATA_KEYWORDS):
        return True
    
    return False

def _collect_consecutive_lines(lines, start_idx, target_has_chinese):
    """
    从指定索引开始收集连续的同语言行
    
    参数:
        lines: 所有行的列表
        start_idx: 开始索引
        target_has_chinese: 目标语言类型（True表示收集中文行，False表示收集非中文行）
    
    返回:
        (收集到的行列表, 下一个未处理的索引)
    """
    collected = []
    i = start_idx
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 跳过元数据行
        if is_metadata_line(line):
            i += 1
            continue
        
        # 检查是否符合目标语言类型
        if line and contains_chinese(line) == target_has_chinese:
            collected.append(line)
            i += 1
        else:
            break
    
    return collected, i

def parse_single_file(file_content, separator=DEFAULT_SEPARATOR):
    """解析单文件模式（包含双语内容），支持两种格式：
    1. 同一行内用分隔符分隔：原文|||译文
    2. 上下两行格式：中文在上，英文在下（支持多行合并）
    
    确保中文始终在右边（译文位置）"""
    bilingual_pairs = []
    lines = file_content.strip().split('\n')
    
    # 模式1：尝试使用分隔符解析
    for line in lines:
        line = line.strip()
        if not line or separator not in line:
            continue
        
        parts = line.split(separator, 1)
        if len(parts) == 2:
            left, right = parts[0].strip(), parts[1].strip()
            left_has_chinese, right_has_chinese = contains_chinese(left), contains_chinese(right)
            
            # 确保中文在右边（译文位置）
            if left_has_chinese and not right_has_chinese:
                bilingual_pairs.append((right, left))
            elif not left_has_chinese and right_has_chinese:
                bilingual_pairs.append((left, right))
            elif not left_has_chinese and not right_has_chinese:
                bilingual_pairs.append((left, right))
    
    # 如果模式1没有解析到任何内容，尝试模式2：上下两行格式
    if not bilingual_pairs:
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过元数据行
            if is_metadata_line(line):
                i += 1
                continue
            
            # 检测当前行语言
            current_has_chinese = contains_chinese(line)
            
            # 收集连续的同语言行作为第一部分
            first_lines, i = _collect_consecutive_lines(lines, i, current_has_chinese)
            
            # 收集连续的不同语言行作为第二部分
            second_lines, i = _collect_consecutive_lines(lines, i, not current_has_chinese)
            
            # 如果两边都有内容，配对
            if first_lines and second_lines:
                # 根据语言类型确定原文和译文
                if current_has_chinese:
                    # 先收集到的是中文（译文），后收集到的是英文（原文）
                    original = ' '.join(second_lines)
                    translation = ' '.join(first_lines)
                else:
                    # 先收集到的是英文（原文），后收集到的是中文（译文）
                    original = ' '.join(first_lines)
                    translation = ' '.join(second_lines)
                
                bilingual_pairs.append((original, translation))
    
    return bilingual_pairs

def parse_double_files(source_content, target_content):
    """解析双文件模式（分别包含原文和译文）"""
    source_lines = [line.strip() for line in source_content.strip().split('\n') if line.strip()]
    target_lines = [line.strip() for line in target_content.strip().split('\n') if line.strip()]
    
    # 对齐行数（取较小值）
    min_lines = min(len(source_lines), len(target_lines))
    bilingual_pairs = [(source_lines[i], target_lines[i]) for i in range(min_lines)]
    
    # 如果行数不一致，给出警告
    if len(source_lines) != len(target_lines):
        print(f"警告：原文文件有 {len(source_lines)} 行，译文文件有 {len(target_lines)} 行")
        print(f"已合并前 {min_lines} 行")
    
    return bilingual_pairs

def parse_files(source_file, target_file=None, separator=DEFAULT_SEPARATOR):
    """统一的文件解析接口"""
    if target_file:
        # 双文件模式
        source_content = read_file(source_file)
        target_content = read_file(target_file)
        return parse_double_files(source_content, target_content)
    else:
        # 单文件模式
        content = read_file(source_file)
        return parse_single_file(content, separator)

def validate_file_path(file_path):
    """验证文件路径"""
    if not file_path:
        return False
    
    if not os.path.isfile(file_path):
        return False
    
    _, ext = os.path.splitext(file_path)
    return ext.lower() in SUPPORTED_EXTENSIONS