"""client.py 的單元測試"""

import json

import pytest
import requests as requests_lib
import responses

from bilibili_subtitle.client import BilibiliAPIError, BilibiliClient, DownloadResult


@pytest.fixture
def client(tmp_path):
    """建立測試用客戶端，輸出到暫存目錄。"""
    c = BilibiliClient(output_dir=tmp_path, convert_to_traditional=False)
    c._cookie_loaded = True
    return c


# === DownloadResult ===

class TestDownloadResult:
    def test_summary_no_failures(self):
        result = DownloadResult(total_parts=3, success=6, failed=0, skipped=0)
        summary = result.summary()
        assert '成功：6 個字幕' in summary
        assert '失敗：0 個字幕' in summary

    def test_summary_with_failures(self):
        result = DownloadResult(
            total_parts=3, success=4, failed=2, skipped=0,
            failed_details=['P2：網路逾時', 'P3：無權限'],
        )
        summary = result.summary()
        assert '失敗：2 個字幕' in summary
        assert 'P2：網路逾時' in summary


# === get_video_list ===

class TestGetVideoList:
    @responses.activate
    def test_success(self, client):
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/player/pagelist',
            json={'code': 0, 'data': [
                {'cid': 123, 'part': '第一集'},
                {'cid': 456, 'part': '第二集'},
            ]},
        )
        result = client.get_video_list('BV13f4y1G7sA')
        assert len(result) == 2
        assert result[0]['cid'] == 123

    @responses.activate
    def test_invalid_bv(self, client):
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/player/pagelist',
            json={'code': -400, 'message': '請求錯誤'},
        )
        with pytest.raises(BilibiliAPIError, match='取得影片列表失敗'):
            client.get_video_list('BVinvalid')

    @responses.activate
    def test_network_error_retries(self, client):
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/player/pagelist',
            body=requests_lib.ConnectionError('timeout'),
        )
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/player/pagelist',
            json={'code': 0, 'data': [{'cid': 1, 'part': 'test'}]},
        )
        result = client.get_video_list('BV13f4y1G7sA')
        assert len(result) == 1


# === download_all_subtitles ===

class TestDownloadAllSubtitles:
    @responses.activate
    def test_full_download_flow(self, client, tmp_path):
        # Mock pagelist API
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/player/pagelist',
            json={'code': 0, 'data': [
                {'cid': 100, 'part': '測試影片'},
            ]},
        )
        # Mock player API
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/player/wbi/v2',
            json={'data': {'subtitle': {'subtitles': [
                {'lan': 'zh-CN', 'subtitle_url': '//example.com/sub.json'},
            ]}}},
        )
        # Mock subtitle JSON
        subtitle_json = json.dumps({'body': [
            {'from': 0.0, 'to': 2.0, 'content': '测试字幕'},
        ]})
        responses.add(
            responses.GET,
            'https://example.com/sub.json',
            body=subtitle_json.encode('utf-8'),
        )

        result = client.download_all_subtitles('BV13f4y1G7sA')
        assert result.success == 1
        assert result.failed == 0

        # 確認 SRT 檔案已建立
        srt_files = list(tmp_path.glob('*.srt'))
        assert len(srt_files) >= 1
        content = srt_files[0].read_text(encoding='utf-8')
        assert '测试字幕' in content

    @responses.activate
    def test_skip_failed_parts(self, client):
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/player/pagelist',
            json={'code': 0, 'data': [
                {'cid': 100, 'part': 'P1'},
                {'cid': 200, 'part': 'P2'},
            ]},
        )
        # P1 成功
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/player/wbi/v2',
            json={'data': {'subtitle': {'subtitles': []}}},
        )
        # P2 API 失敗
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/player/wbi/v2',
            json={'error': 'server error'},
            status=500,
        )

        result = client.download_all_subtitles('BV13f4y1G7sA')
        # P1 沒字幕，被跳過；P2 失敗
        assert result.skipped == 1
        assert result.failed == 1

    @responses.activate
    def test_bv_from_url(self, client):
        responses.add(
            responses.GET,
            'https://api.bilibili.com/x/player/pagelist',
            json={'code': 0, 'data': []},
        )
        result = client.download_all_subtitles('https://bilibili.com/video/BV13f4y1G7sA?p=1')
        assert result.total_parts == 0


# === set_cookie ===

class TestSetCookie:
    def test_set_cookie_dict(self):
        client = BilibiliClient()
        client.set_cookie({'SESSDATA': 'abc123'})
        assert client._cookie_loaded is True
        assert client.session.cookies.get('SESSDATA') == 'abc123'
