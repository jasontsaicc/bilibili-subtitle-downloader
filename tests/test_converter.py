"""converter.py 的單元測試"""

import json

import pytest

from bilibili_subtitle.converter import (
    format_timestamp,
    json_to_srt,
    merge_bilingual,
    parse_bv,
    preview_srt,
    sanitize_filename,
)


# === parse_bv ===

class TestParseBv:
    def test_plain_bv(self):
        assert parse_bv('BV13f4y1G7sA') == 'BV13f4y1G7sA'

    def test_bv_with_whitespace(self):
        assert parse_bv('  BV13f4y1G7sA  ') == 'BV13f4y1G7sA'

    def test_full_url(self):
        assert parse_bv('https://www.bilibili.com/video/BV13f4y1G7sA') == 'BV13f4y1G7sA'

    def test_url_with_params(self):
        assert parse_bv('https://www.bilibili.com/video/BV13f4y1G7sA?p=3&spm=123') == 'BV13f4y1G7sA'

    def test_mobile_url(self):
        assert parse_bv('https://m.bilibili.com/video/BV13f4y1G7sA') == 'BV13f4y1G7sA'

    def test_invalid_input(self):
        with pytest.raises(ValueError, match='無法從輸入中解析 BV 號碼'):
            parse_bv('this is not a valid input')

    def test_empty_input(self):
        with pytest.raises(ValueError):
            parse_bv('')

    def test_av_number(self):
        with pytest.raises(ValueError):
            parse_bv('av12345')


# === sanitize_filename ===

class TestSanitizeFilename:
    def test_clean_filename(self):
        assert sanitize_filename('normal_name') == 'normal_name'

    def test_replace_slash(self):
        assert sanitize_filename('a/b') == 'a、b'

    def test_replace_backslash(self):
        assert sanitize_filename('a\\b') == 'a、b'

    def test_replace_colon(self):
        assert sanitize_filename('a:b') == 'a：b'

    def test_replace_question_mark(self):
        assert sanitize_filename('what?') == 'what？'

    def test_replace_multiple(self):
        assert sanitize_filename('a/b:c?d') == 'a、b：c？d'

    def test_path_traversal_dots(self):
        assert '..' not in sanitize_filename('../../etc/passwd')

    def test_path_traversal_leading_slash(self):
        result = sanitize_filename('/etc/passwd')
        assert not result.startswith('/')

    def test_empty_input(self):
        assert sanitize_filename('') == ''


# === format_timestamp ===

class TestFormatTimestamp:
    def test_zero(self):
        assert format_timestamp(0) == '00:00:00,000'

    def test_simple_seconds(self):
        assert format_timestamp(5.0) == '00:00:05,000'

    def test_with_milliseconds(self):
        assert format_timestamp(5.123) == '00:00:05,123'

    def test_minutes(self):
        assert format_timestamp(65.5) == '00:01:05,500'

    def test_hours(self):
        assert format_timestamp(3661.1) == '01:01:01,100'

    def test_integer_input(self):
        assert format_timestamp(10) == '00:00:10,000'

    def test_two_decimal_places(self):
        assert format_timestamp(1.12) == '00:00:01,120'

    def test_one_decimal_place(self):
        assert format_timestamp(1.1) == '00:00:01,100'


# === json_to_srt ===

def _make_subtitle_json(subtitles: list[dict]) -> bytes:
    """建構 Bilibili 字幕 JSON 測試資料。"""
    return json.dumps({'body': subtitles}).encode('utf-8')


class TestJsonToSrt:
    def test_single_subtitle(self):
        json_data = _make_subtitle_json([
            {'from': 0.0, 'to': 2.5, 'content': '你好世界'},
        ])
        srt = json_to_srt(json_data, convert_to_traditional=False)
        assert '1\n' in srt
        assert '00:00:00,000 --> 00:00:02,500' in srt
        assert '你好世界' in srt

    def test_multiple_subtitles(self):
        json_data = _make_subtitle_json([
            {'from': 0.0, 'to': 2.0, 'content': '第一句'},
            {'from': 2.5, 'to': 5.0, 'content': '第二句'},
        ])
        srt = json_to_srt(json_data, convert_to_traditional=False)
        assert '1\n' in srt
        assert '2\n' in srt
        assert '第一句' in srt
        assert '第二句' in srt

    def test_traditional_conversion(self):
        json_data = _make_subtitle_json([
            {'from': 0.0, 'to': 1.0, 'content': '简体中文'},
        ])
        srt = json_to_srt(json_data, convert_to_traditional=True)
        assert '簡體中文' in srt

    def test_no_traditional_conversion(self):
        json_data = _make_subtitle_json([
            {'from': 0.0, 'to': 1.0, 'content': '简体中文'},
        ])
        srt = json_to_srt(json_data, convert_to_traditional=False)
        assert '简体中文' in srt

    def test_string_input(self):
        json_str = json.dumps({'body': [
            {'from': 0.0, 'to': 1.0, 'content': 'test'},
        ]})
        srt = json_to_srt(json_str, convert_to_traditional=False)
        assert 'test' in srt

    def test_empty_body(self):
        json_data = _make_subtitle_json([])
        srt = json_to_srt(json_data, convert_to_traditional=False)
        assert srt == ''


# === merge_bilingual ===

class TestMergeBilingual:
    def test_basic_merge(self):
        zh = _make_subtitle_json([
            {'from': 0.0, 'to': 2.0, 'content': '你好'},
        ])
        ja = _make_subtitle_json([
            {'from': 0.0, 'to': 2.0, 'content': 'こんにちは'},
        ])
        merged = merge_bilingual(zh, ja, convert_to_traditional=False)
        assert '你好' in merged
        assert 'こんにちは' in merged

    def test_merge_preserves_primary_timeline(self):
        zh = _make_subtitle_json([
            {'from': 0.0, 'to': 2.0, 'content': '第一句'},
            {'from': 3.0, 'to': 5.0, 'content': '第二句'},
        ])
        en = _make_subtitle_json([
            {'from': 0.0, 'to': 2.0, 'content': 'First'},
            {'from': 3.0, 'to': 5.0, 'content': 'Second'},
        ])
        merged = merge_bilingual(zh, en, convert_to_traditional=False)
        assert '第一句\nFirst' in merged
        assert '第二句\nSecond' in merged

    def test_merge_unmatched_secondary(self):
        zh = _make_subtitle_json([
            {'from': 0.0, 'to': 2.0, 'content': '你好'},
        ])
        en = _make_subtitle_json([
            {'from': 5.0, 'to': 7.0, 'content': 'Hello'},
        ])
        merged = merge_bilingual(zh, en, convert_to_traditional=False)
        assert '你好' in merged
        # 時間不匹配，不會合併
        assert 'Hello' not in merged


# === preview_srt ===

class TestPreviewSrt:
    def test_preview_limits_entries(self):
        json_data = _make_subtitle_json([
            {'from': float(i), 'to': float(i + 1), 'content': f'Line {i}'}
            for i in range(10)
        ])
        srt = json_to_srt(json_data, convert_to_traditional=False)
        preview = preview_srt(srt, lines=3)
        assert 'Line 0' in preview
        assert 'Line 2' in preview
        assert 'Line 3' not in preview

    def test_preview_with_fewer_entries(self):
        json_data = _make_subtitle_json([
            {'from': 0.0, 'to': 1.0, 'content': 'Only one'},
        ])
        srt = json_to_srt(json_data, convert_to_traditional=False)
        preview = preview_srt(srt, lines=5)
        assert 'Only one' in preview
