"""Bilibili 字幕下載客戶端"""

import gzip
import logging
import platform
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

from bilibili_subtitle.converter import (
    json_to_srt,
    merge_bilingual,
    parse_bv,
    preview_srt,
    sanitize_filename,
    save_srt,
)

logger = logging.getLogger(__name__)

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) '
    'Gecko/20100101 Firefox/120.0'
)


class BilibiliAPIError(Exception):
    """Bilibili API 回傳錯誤"""


@dataclass
class DownloadResult:
    """下載結果統計"""
    total_parts: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0
    failed_details: list = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            '=== 下載完成 ===',
            f'成功：{self.success} 個字幕',
            f'失敗：{self.failed} 個字幕',
            f'跳過（無字幕）：{self.skipped} 集',
            f'總共：{self.total_parts} 集',
        ]
        if self.failed_details:
            lines.append('失敗詳情：')
            for detail in self.failed_details:
                lines.append(f'  - {detail}')
        return '\n'.join(lines)


class BilibiliClient:
    """Bilibili 字幕下載客戶端

    封裝所有 API 呼叫、Cookie 管理、下載邏輯。

    使用方式：
        client = BilibiliClient(output_dir='./subtitles')
        client.load_firefox_cookie()
        result = client.download_all_subtitles('BV13f4y1G7sA')
        print(result.summary())
    """

    BASE_API = 'https://api.bilibili.com'

    def __init__(
        self,
        encoding: str = 'utf-8',
        output_dir: str | Path = '.',
        convert_to_traditional: bool = True,
        show_preview: bool = False,
    ):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.encoding = encoding
        self.output_dir = Path(output_dir)
        self.convert_to_traditional = convert_to_traditional
        self.show_preview = show_preview
        self._cookie_loaded = False

    def set_cookie(self, cookie: dict) -> None:
        """設定 Cookie（dict 格式）。"""
        self.session.cookies.update(cookie)
        self._cookie_loaded = True
        logger.info('Cookie 已設定')

    def load_browser_cookie(self, browser: str = 'chrome') -> None:
        """從瀏覽器載入 Cookie。

        Args:
            browser: 瀏覽器名稱（'chrome', 'firefox', 'edge', 'brave'）
        """
        import browser_cookie3
        loaders = {
            'chrome': browser_cookie3.chrome,
            'firefox': browser_cookie3.firefox,
            'edge': browser_cookie3.edge,
            'brave': browser_cookie3.brave,
        }
        loader = loaders.get(browser)
        if not loader:
            raise ValueError(f'不支援的瀏覽器：{browser}（支援：{", ".join(loaders)}）')
        self.session.cookies = loader(domain_name='.bilibili.com')
        self._cookie_loaded = True
        logger.info(f'{browser} Cookie 載入完成')

    def load_firefox_cookie(self) -> None:
        """從 Firefox 載入 Cookie（向後相容）。"""
        self.load_browser_cookie('firefox')

    def download_all_subtitles(self, bv_input: str) -> DownloadResult:
        """下載指定 BV 影片的所有字幕。

        Args:
            bv_input: BV 號碼或包含 BV 號碼的 URL

        Returns:
            DownloadResult 下載結果統計
        """
        bv = parse_bv(bv_input)
        logger.info(f'開始下載：{bv}')

        video_list = self.get_video_list(bv)
        result = DownloadResult(total_parts=len(video_list))

        for i, video in enumerate(video_list, 1):
            cid = video['cid']
            part_name = video['part']
            try:
                count = self._download_part_subtitles(cid, bv, i, part_name)
                if count == 0:
                    result.skipped += 1
                else:
                    result.success += count
            except Exception as e:
                result.failed += 1
                detail = f'P{i}（{part_name}）：{e}'
                result.failed_details.append(detail)
                logger.warning(f'P{i} 下載失敗：{e}')

            logger.info(f'【總進度：{i}/{len(video_list)} 集】')

        self._notify_completion(result)
        return result

    def get_video_list(self, bv: str) -> list[dict]:
        """取得影片的分集列表。"""
        resp = self._request_with_retry(
            f'{self.BASE_API}/x/player/pagelist',
            params={'bvid': bv},
        )
        data = resp.json()

        if data.get('code') != 0:
            msg = data.get('message', '未知錯誤')
            raise BilibiliAPIError(f'取得影片列表失敗：{msg}（BV={bv}）')

        video_list = data['data']
        logger.info(f'影片目錄取得成功，共 {len(video_list)} 集')
        return video_list

    def _download_part_subtitles(
        self, cid: int, bv: str, part_number: int, part_name: str
    ) -> int:
        """下載單集的所有語言字幕，回傳成功數量。"""
        resp = self._request_with_retry(
            f'{self.BASE_API}/x/player/wbi/v2',
            params={'bvid': bv, 'cid': cid},
        )
        data = resp.json()

        subtitle_list = data['data']['subtitle']['subtitles']
        if not subtitle_list:
            logger.warning(f'【警告】P{part_number} 無字幕')
            return 0

        # 收集所有語言的字幕內容（用於雙語合併）
        subtitle_contents = {}
        count = 0

        for subtitle in subtitle_list:
            lang = subtitle['lan']
            try:
                json_content = self._fetch_subtitle_json(subtitle['subtitle_url'])
                subtitle_contents[lang] = json_content

                # 儲存單語字幕
                filename = self._build_filename(bv, part_number, part_name, lang)
                srt_content = json_to_srt(json_content, self.convert_to_traditional)
                save_srt(srt_content, self.output_dir / f'{filename}.srt', self.encoding)

                if self.show_preview:
                    logger.info(f'--- 預覽 {filename} ---\n{preview_srt(srt_content)}')

                logger.info(f'{filename} OK.')
                count += 1
            except Exception as e:
                logger.warning(f'P{part_number} {lang} 下載失敗：{e}')

            time.sleep(0.2)  # 限速

        # 嘗試雙語合併（中文 + 其他語言）
        self._try_bilingual_merge(subtitle_contents, bv, part_number, part_name)

        return count

    def _fetch_subtitle_json(self, subtitle_url: str) -> bytes:
        """下載字幕 JSON 內容。"""
        url = 'https:' + subtitle_url
        resp = self._request_with_retry(url)
        # requests 自動處理 gzip 解壓，直接回傳內容
        return resp.content

    def _try_bilingual_merge(
        self,
        subtitle_contents: dict[str, bytes],
        bv: str,
        part_number: int,
        part_name: str,
    ) -> None:
        """嘗試合併雙語字幕。如果有中文和其他語言，自動合併。"""
        zh_content = subtitle_contents.get('zh-CN') or subtitle_contents.get('ai-zh')
        if not zh_content or len(subtitle_contents) < 2:
            return

        for lang, content in subtitle_contents.items():
            if lang in ('zh-CN', 'ai-zh'):
                continue
            try:
                merged = merge_bilingual(zh_content, content, self.convert_to_traditional)
                filename = self._build_filename(bv, part_number, part_name, f'zh+{lang}')
                save_srt(merged, self.output_dir / f'{filename}.srt', self.encoding)
                logger.info(f'{filename}（雙語合併）OK.')
            except Exception as e:
                logger.debug(f'雙語合併失敗（zh+{lang}）：{e}')

    def _build_filename(
        self, bv: str, part_number: int, part_name: str, lang: str
    ) -> str:
        """建構字幕檔名。"""
        clean_name = sanitize_filename(part_name)
        return f'{bv} - P{part_number}：{clean_name} - {lang}'

    def _request_with_retry(
        self, url: str, params: dict | None = None, max_retries: int = 2
    ) -> requests.Response:
        """發送 HTTP 請求，失敗時自動重試。"""
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                resp = self.session.get(url, params=params, timeout=30)
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                last_error = e
                if attempt < max_retries:
                    wait = (attempt + 1) * 1
                    logger.warning(f'請求失敗，{wait} 秒後重試 ({attempt + 1}/{max_retries})：{e}')
                    time.sleep(wait)
        raise last_error

    @staticmethod
    def _notify_completion(result: DownloadResult) -> None:
        """下載完成後發送系統通知（僅 macOS）。"""
        if platform.system() != 'Darwin':
            return
        try:
            msg = f'成功 {result.success} 個字幕，失敗 {result.failed} 個'
            subprocess.run(
                ['osascript', '-e', f'display notification "{msg}" with title "Bilibili 字幕下載器"'],
                capture_output=True,
                timeout=5,
            )
        except Exception:
            pass  # 通知失敗不影響功能
