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
    # 字幕制作相关
    '字幕', '翻译', '校对', '特效', '后期', '总监', 
    '压制', '时间轴', '轴', '双语合并', 'WEB版', '外挂字幕',
    'staff', 'STAFF', 'Staff',
    
    # 字幕组招募相关
    '招募', '加入', '欢迎', '长期', '招募翻译', '招募时间轴', 
    '招募片源', '招募校对', '听译', '片源', '时间轴',
    
    # 字幕组名称
    'YYeTs', '人人影视', '破烂熊', '诸神字幕组', 'TLF', 'FRDS',
    'CMCT', 'WiKi', 'HDChina', 'CHD', 'HDStar', 'HDSky',
    '字幕组', '工作组', '制作组',
    
    # 版本信息
    'WEB-DL', 'Blu-ray', 'BDRip', 'DVDRip', 'HDTV', '720p', '1080p',
    'x264', 'x265', 'H.264', 'HEVC', 'AAC', 'DTS', 'AC3',
    
    # 版权和声明
    '版权', '禁止', '转载', '仅供学习', '请勿商用', '侵删',
    '本字幕仅供', '严禁用于', '如有侵权'
]

# 语言类型枚举
class LanguageType:
    ENGLISH_CHINESE = 'english_chinese'  # 中英双语
    JAPANESE_CHINESE = 'japanese_chinese'  # 中日双语
    UNKNOWN = 'unknown'  # 未知

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
    sample_lines = lines[:20]
    
    separator_scores = {}
    
    for sep in COMMON_SEPARATORS:
        score = 0
        for line in sample_lines:
            line = line.strip()
            if sep in line:
                parts = line.split(sep, 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    score += 1
                    left_has_chinese = contains_chinese(parts[0])
                    right_has_chinese = contains_chinese(parts[1])
                    if left_has_chinese != right_has_chinese:
                        score += 1
        separator_scores[sep] = score
    
    if separator_scores:
        best_separator = max(separator_scores, key=separator_scores.get)
        if separator_scores[best_separator] > 0:
            return best_separator
    
    return DEFAULT_SEPARATOR

def detect_language_type(content):
    """
    检测内容的语言类型
    
    参数:
        content: 文件内容字符串
    
    返回:
        LanguageType枚举值
    """
    has_japanese_kana = False
    has_chinese = False
    has_english = False
    
    lines = content.strip().split('\n')[:50]  # 只检查前50行
    
    for line in lines:
        if contains_japanese_kana(line):
            has_japanese_kana = True
        if contains_chinese(line):
            has_chinese = True
        if contains_english(line):
            has_english = True
    
    # 判断逻辑
    if has_japanese_kana and has_chinese:
        return LanguageType.JAPANESE_CHINESE
    elif has_english and has_chinese:
        return LanguageType.ENGLISH_CHINESE
    else:
        return LanguageType.UNKNOWN

def contains_chinese(text):
    """检测文本是否包含中文字符（CJK统一表意文字）"""
    return any('\u4e00' <= c <= '\u9fff' for c in text)

def contains_japanese_kana(text):
    """检测文本是否包含日语假名（平假名或片假名）"""
    return any('\u3040' <= c <= '\u30FF' for c in text)

def contains_japanese(text):
    """检测文本是否为日语（包含假名）"""
    return contains_japanese_kana(text)

def contains_english(text):
    """检测文本是否包含英文字母"""
    return any('a' <= c.lower() <= 'z' for c in text)

def parse_srt_to_text(srt_content, language_type=None):
    """解析SRT字幕文件，提取纯文本内容
    根据语言类型选择不同的解析策略"""
    if language_type == LanguageType.JAPANESE_CHINESE:
        return parse_srt_japanese_chinese(srt_content)
    elif language_type == LanguageType.ENGLISH_CHINESE:
        return parse_srt_english_chinese(srt_content)
    else:
        # 未知类型，先检测再解析
        detected_type = detect_language_type(srt_content)
        if detected_type == LanguageType.JAPANESE_CHINESE:
            return parse_srt_japanese_chinese(srt_content)
        else:
            return parse_srt_english_chinese(srt_content)

def parse_srt_english_chinese(srt_content):
    """解析中英双语SRT字幕文件"""
    lines = srt_content.split('\n')
    result = []
    current_subtitle = []
    
    for line in lines:
        line = line.strip()
        if not line or line.isdigit() or ' --> ' in line or re.match(r'^\d{2}:\d{2}:\d{2}', line):
            if current_subtitle:
                if len(current_subtitle) >= 2:
                    first = current_subtitle[0]
                    second = current_subtitle[1]
                    if contains_chinese(first) and contains_english(second):
                        result.append(f"{second}{DEFAULT_SEPARATOR}{first}")
                    elif contains_english(first) and contains_chinese(second):
                        result.append(f"{first}{DEFAULT_SEPARATOR}{second}")
                    else:
                        result.append('\n'.join(current_subtitle))
                else:
                    result.append('\n'.join(current_subtitle))
                current_subtitle = []
            continue
        
        current_subtitle.append(line)
    
    if current_subtitle:
        if len(current_subtitle) >= 2:
            first = current_subtitle[0]
            second = current_subtitle[1]
            if contains_chinese(first) and contains_english(second):
                result.append(f"{second}{DEFAULT_SEPARATOR}{first}")
            elif contains_english(first) and contains_chinese(second):
                result.append(f"{first}{DEFAULT_SEPARATOR}{second}")
            else:
                result.append('\n'.join(current_subtitle))
        else:
            result.append('\n'.join(current_subtitle))
    
    return '\n'.join(result)

def parse_srt_japanese_chinese(srt_content):
    """解析中日双语SRT字幕文件"""
    lines = srt_content.split('\n')
    result = []
    current_subtitle = []
    
    for line in lines:
        line = line.strip()
        if not line or line.isdigit() or ' --> ' in line or re.match(r'^\d{2}:\d{2}:\d{2}', line):
            if current_subtitle:
                if len(current_subtitle) >= 2:
                    first = current_subtitle[0]
                    second = current_subtitle[1]
                    first_has_japanese = contains_japanese(first)
                    second_has_japanese = contains_japanese(second)
                    
                    if first_has_japanese and not second_has_japanese:
                        result.append(f"{first}{DEFAULT_SEPARATOR}{second}")
                    elif second_has_japanese and not first_has_japanese:
                        result.append(f"{second}{DEFAULT_SEPARATOR}{first}")
                    else:
                        # 都没有日语假名（可能都是汉字），默认第一行是日语，第二行是中文
                        if first and second:
                            result.append(f"{first}{DEFAULT_SEPARATOR}{second}")
                        else:
                            result.append('\n'.join(current_subtitle))
                else:
                    result.append('\n'.join(current_subtitle))
                current_subtitle = []
            continue
        
        current_subtitle.append(line)
    
    if current_subtitle:
        if len(current_subtitle) >= 2:
            first = current_subtitle[0]
            second = current_subtitle[1]
            first_has_japanese = contains_japanese(first)
            second_has_japanese = contains_japanese(second)
            
            if first_has_japanese and not second_has_japanese:
                result.append(f"{first}{DEFAULT_SEPARATOR}{second}")
            elif second_has_japanese and not first_has_japanese:
                result.append(f"{second}{DEFAULT_SEPARATOR}{first}")
            else:
                # 都没有日语假名（可能都是汉字），默认第一行是日语，第二行是中文
                if first and second:
                    result.append(f"{first}{DEFAULT_SEPARATOR}{second}")
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
    dialogue_count = 0
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        if line.startswith('[Events]'):
            in_events_section = True
            continue
        
        if in_events_section and line.startswith('['):
            break
        
        if in_events_section and line.startswith('Dialogue:'):
            dialogue_count += 1
            parts = line.split(',', 9)
            if len(parts) >= 10:
                text = parts[9]
                text = re.sub(r'{[^}]*}', '', text).strip()
                text = text.replace(r'\n', '\n').replace(r'\h', ' ').replace(r'\t', '\t').replace(r'\r', '')
                
                if text:
                    # 检查是否以关键字开头
                    starts_with_keyword = any(text.startswith(keyword) for keyword in METADATA_KEYWORDS)
                    if starts_with_keyword:
                        continue
                    
                    # 检查是否包含字幕组名称（直接过滤）
                    group_names = ['YYeTs', '人人影视', '破烂熊', '诸神字幕组', '字幕组', '工作组', '制作组']
                    contains_group = any(group in text for group in group_names)
                    if contains_group:
                        continue
                    
                    # 检查是否包含招募相关关键词
                    recruit_words = ['招募', '加入', '欢迎', '长期']
                    contains_recruit = any(word in text for word in recruit_words)
                    if contains_recruit:
                        continue
                    
                    # 检查包含的关键字数量（包含2个以上关键字则过滤）
                    keyword_count = sum(1 for keyword in METADATA_KEYWORDS if keyword in text)
                    if keyword_count >= 2:
                        continue
                    
                    # 检查是否包含版本信息（通常是技术参数）
                    version_words = ['WEB-DL', 'Blu-ray', 'BDRip', 'DVDRip', 'HDTV', '720p', '1080p', 'x264', 'x265']
                    contains_version = any(v in text for v in version_words)
                    if contains_version:
                        continue
                    
                    result.append(text)
    
    print(f"ASS解析: 共找到 {dialogue_count} 条Dialogue，提取 {len(result)} 条有效内容")
    return '\n'.join(result)

def read_file(file_path):
    """读取文件内容，支持多种编码格式"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {ext}。支持的格式: {SUPPORTED_EXTENSIONS}")
    
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
    
    if ext.lower() == '.srt':
        content = parse_srt_to_text(content)
    
    if ext.lower() == '.ass':
        content = parse_ass_to_text(content)
    
    return content

def is_metadata_line(line):
    """判断是否是元数据行（需要过滤）"""
    if not line or not line.strip():
        return True
    
    line = line.strip()
    
    if line.startswith('(') and line.endswith(')') and len(line) <= 20:
        return True
    
    if line.startswith('第') and '章' in line:
        return True
    
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
        
        if is_metadata_line(line):
            i += 1
            continue
        
        if line and contains_chinese(line) == target_has_chinese:
            collected.append(line)
            i += 1
        else:
            break
    
    return collected, i

def parse_japanese_chinese_file(content, separator=DEFAULT_SEPARATOR):
    """解析中日双语文件（优先使用日语假名检测）"""
    bilingual_pairs = []
    lines = content.strip().split('\n')
    ass_separator = '\\N'
    
    # 模式1：ASS字幕中日双语格式（\N分隔）
    for line in lines:
        line = line.strip()
        if not line or ass_separator not in line:
            continue
        
        parts = line.split(ass_separator, 1)
        if len(parts) == 2:
            left, right = parts[0].strip(), parts[1].strip()
            if left and right:
                left_has_japanese = contains_japanese(left)
                right_has_japanese = contains_japanese(right)
                
                if left_has_japanese and not right_has_japanese:
                    bilingual_pairs.append((left, right))
                elif right_has_japanese and not left_has_japanese:
                    bilingual_pairs.append((right, left))
                else:
                    bilingual_pairs.append((left, right))
    
    # 模式2：使用指定分隔符
    if not bilingual_pairs and separator:
        for line in lines:
            line = line.strip()
            if not line or separator not in line:
                continue
            
            parts = line.split(separator, 1)
            if len(parts) == 2:
                left, right = parts[0].strip(), parts[1].strip()
                if left and right:
                    left_has_japanese = contains_japanese(left)
                    right_has_japanese = contains_japanese(right)
                    
                    if left_has_japanese and not right_has_japanese:
                        bilingual_pairs.append((left, right))
                    elif right_has_japanese and not left_has_japanese:
                        bilingual_pairs.append((right, left))
                    else:
                        bilingual_pairs.append((left, right))
    
    # 模式3：上下两行格式
    if not bilingual_pairs:
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if is_metadata_line(line):
                i += 1
                continue
            
            current_has_japanese = contains_japanese(line)
            
            first_lines, i = _collect_consecutive_lines_jp(lines, i, current_has_japanese)
            second_lines, i = _collect_consecutive_lines_jp(lines, i, not current_has_japanese)
            
            if first_lines and second_lines:
                if current_has_japanese:
                    original = ' '.join(first_lines)
                    translation = ' '.join(second_lines)
                else:
                    translation = ' '.join(first_lines)
                    original = ' '.join(second_lines)
                
                bilingual_pairs.append((original, translation))
    
    print(f"中日双语解析完成: 共提取 {len(bilingual_pairs)} 条双语内容")
    return bilingual_pairs

def _collect_consecutive_lines_jp(lines, start_idx, target_has_japanese):
    """收集连续的日语/非日语行"""
    collected = []
    i = start_idx
    
    while i < len(lines):
        line = lines[i].strip()
        
        if is_metadata_line(line):
            i += 1
            continue
        
        if line and contains_japanese(line) == target_has_japanese:
            collected.append(line)
            i += 1
        else:
            break
    
    return collected, i

def parse_english_chinese_file(content, separator=DEFAULT_SEPARATOR):
    """解析中英双语文件（使用中文字符检测）"""
    bilingual_pairs = []
    lines = content.strip().split('\n')
    ass_separator = '\\N'
    
    # 模式1：ASS字幕中英双语格式（\N分隔）
    for line in lines:
        line = line.strip()
        if not line or ass_separator not in line:
            continue
        
        parts = line.split(ass_separator, 1)
        if len(parts) == 2:
            left, right = parts[0].strip(), parts[1].strip()
            if left and right:
                left_has_chinese = contains_chinese(left)
                right_has_chinese = contains_chinese(right)
                
                if left_has_chinese and not right_has_chinese:
                    bilingual_pairs.append((right, left))
                elif not left_has_chinese and right_has_chinese:
                    bilingual_pairs.append((left, right))
                else:
                    bilingual_pairs.append((left, right))
    
    # 模式2：使用指定分隔符
    if not bilingual_pairs and separator:
        for line in lines:
            line = line.strip()
            if not line or separator not in line:
                continue
            
            parts = line.split(separator, 1)
            if len(parts) == 2:
                left, right = parts[0].strip(), parts[1].strip()
                if left and right:
                    left_has_chinese = contains_chinese(left)
                    right_has_chinese = contains_chinese(right)
                    
                    if left_has_chinese and not right_has_chinese:
                        bilingual_pairs.append((right, left))
                    elif not left_has_chinese and right_has_chinese:
                        bilingual_pairs.append((left, right))
                    else:
                        bilingual_pairs.append((left, right))
    
    # 模式3：上下两行格式
    if not bilingual_pairs:
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if is_metadata_line(line):
                i += 1
                continue
            
            current_has_chinese = contains_chinese(line)
            
            first_lines, i = _collect_consecutive_lines(lines, i, current_has_chinese)
            second_lines, i = _collect_consecutive_lines(lines, i, not current_has_chinese)
            
            if first_lines and second_lines:
                if current_has_chinese:
                    original = ' '.join(second_lines)
                    translation = ' '.join(first_lines)
                else:
                    original = ' '.join(first_lines)
                    translation = ' '.join(second_lines)
                
                bilingual_pairs.append((original, translation))
    
    print(f"中英双语解析完成: 共提取 {len(bilingual_pairs)} 条双语内容")
    return bilingual_pairs

def parse_single_file(file_content, separator=DEFAULT_SEPARATOR):
    """解析单文件模式（自动检测语言类型并调用对应解析器）"""
    language_type = detect_language_type(file_content)
    print(f"检测到语言类型: {language_type}")
    
    if language_type == LanguageType.JAPANESE_CHINESE:
        return parse_japanese_chinese_file(file_content, separator)
    elif language_type == LanguageType.ENGLISH_CHINESE:
        return parse_english_chinese_file(file_content, separator)
    else:
        # 默认使用中英解析器（兼容性更好）
        return parse_english_chinese_file(file_content, separator)

def parse_double_files(source_content, target_content):
    """解析双文件模式（分别包含原文和译文）"""
    source_lines = [line.strip() for line in source_content.strip().split('\n') if line.strip()]
    target_lines = [line.strip() for line in target_content.strip().split('\n') if line.strip()]
    
    min_lines = min(len(source_lines), len(target_lines))
    bilingual_pairs = [(source_lines[i], target_lines[i]) for i in range(min_lines)]
    
    if len(source_lines) != len(target_lines):
        print(f"警告：原文文件有 {len(source_lines)} 行，译文文件有 {len(target_lines)} 行")
        print(f"已合并前 {min_lines} 行")
    
    return bilingual_pairs

def parse_files(source_file, target_file=None, separator=DEFAULT_SEPARATOR):
    """统一的文件解析接口"""
    if target_file:
        source_content = read_file(source_file)
        target_content = read_file(target_file)
        return parse_double_files(source_content, target_content)
    else:
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