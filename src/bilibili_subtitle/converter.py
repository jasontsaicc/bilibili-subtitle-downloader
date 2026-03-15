"""字幕格式轉換與工具函數"""

import json
import re
import time
from pathlib import Path

import opencc

# 重用同一個轉換器實例，避免重複初始化
_converter = opencc.OpenCC('s2t')

INVALID_FILENAME_CHARS = {
    '/': '、',
    '\\': '、',
    '|': '、',
    '*': 'X',
    ':': '：',
    '?': '？',
    '<': '《',
    '>': '》',
    '"': '\u201c',
}


def parse_bv(input_string: str) -> str:
    """從使用者輸入中擷取 BV 號碼。

    支援：
    - 純 BV 號碼：BV13f4y1G7sA
    - 完整 URL：https://www.bilibili.com/video/BV13f4y1G7sA
    - 帶參數 URL：https://www.bilibili.com/video/BV13f4y1G7sA?p=1
    """
    input_string = input_string.strip()
    match = re.search(r'(BV[a-zA-Z0-9]+)', input_string)
    if match:
        return match.group(1)
    raise ValueError(f'無法從輸入中解析 BV 號碼：{input_string}')


def sanitize_filename(filename: str) -> str:
    """清理檔名中不允許的特殊字元。"""
    for char, replacement in INVALID_FILENAME_CHARS.items():
        filename = filename.replace(char, replacement)
    # 防止路徑穿越
    filename = filename.replace('..', '')
    # 移除開頭的路徑分隔符
    filename = filename.lstrip('/')
    return filename


def format_timestamp(seconds: float) -> str:
    """將秒數格式化為 SRT 時間戳格式 (HH:MM:SS,mmm)。"""
    seconds = round(seconds, 3)
    time_part = time.strftime("%H:%M:%S", time.gmtime(seconds))
    # 取得毫秒部分
    ms_str = str(seconds).partition('.')[2]
    ms_str = ms_str[:3].ljust(3, '0')
    return f"{time_part},{ms_str}"


def json_to_srt(json_content: bytes | str, convert_to_traditional: bool = True) -> str:
    """將 Bilibili JSON 字幕轉換為 SRT 格式字串。

    Args:
        json_content: JSON 字幕內容（bytes 或 str）
        convert_to_traditional: 是否轉換為繁體中文

    Returns:
        SRT 格式字串
    """
    if isinstance(json_content, bytes):
        json_content = json_content.decode('utf-8')

    data = json.loads(json_content)['body']
    lines = []

    for index, subtitle in enumerate(data, 1):
        start_time = format_timestamp(subtitle['from'])
        end_time = format_timestamp(subtitle['to'])
        content = subtitle['content']
        if convert_to_traditional:
            content = _converter.convert(content)

        lines.append(f"{index}\n{start_time} --> {end_time}\n{content}\n")

    return '\n'.join(lines)


def save_srt(srt_content: str, output_path: Path, encoding: str = 'utf-8') -> None:
    """將 SRT 內容儲存到檔案。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding=encoding) as f:
        f.write(srt_content)


def merge_bilingual(
    json_content_primary: bytes | str,
    json_content_secondary: bytes | str,
    convert_to_traditional: bool = True,
) -> str:
    """合併兩種語言的字幕為雙語 SRT。

    主要語言在上方，次要語言在下方。以主要語言的時間軸為準。

    Args:
        json_content_primary: 主要語言 JSON 字幕
        json_content_secondary: 次要語言 JSON 字幕
        convert_to_traditional: 是否對中文字幕做繁體轉換

    Returns:
        雙語 SRT 格式字串
    """
    if isinstance(json_content_primary, bytes):
        json_content_primary = json_content_primary.decode('utf-8')
    if isinstance(json_content_secondary, bytes):
        json_content_secondary = json_content_secondary.decode('utf-8')

    primary_subs = json.loads(json_content_primary)['body']
    secondary_subs = json.loads(json_content_secondary)['body']

    # 建立次要字幕的時間索引，用於匹配
    secondary_by_time = {}
    for sub in secondary_subs:
        key = round(sub['from'], 1)
        secondary_by_time[key] = sub['content']

    lines = []
    for index, sub in enumerate(primary_subs, 1):
        start_time = format_timestamp(sub['from'])
        end_time = format_timestamp(sub['to'])

        primary_text = sub['content']
        if convert_to_traditional:
            primary_text = _converter.convert(primary_text)

        # 尋找時間最接近的次要字幕
        primary_key = round(sub['from'], 1)
        secondary_text = secondary_by_time.get(primary_key, '')

        if secondary_text:
            content = f"{primary_text}\n{secondary_text}"
        else:
            content = primary_text

        lines.append(f"{index}\n{start_time} --> {end_time}\n{content}\n")

    return '\n'.join(lines)


def preview_srt(srt_content: str, lines: int = 5) -> str:
    """預覽 SRT 字幕前幾個條目。"""
    entries = srt_content.strip().split('\n\n')
    preview_entries = entries[:lines]
    return '\n\n'.join(preview_entries)
