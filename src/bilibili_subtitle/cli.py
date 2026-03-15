"""命令列介面"""

import argparse
import logging
import sys

from bilibili_subtitle.client import BilibiliClient


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='bilibili-subtitle',
        description='Bilibili 字幕下載器 — 下載影片字幕並轉換為 SRT 格式',
    )
    parser.add_argument(
        'bv',
        help='BV 號碼或 Bilibili 影片 URL（如 BV13f4y1G7sA）',
    )
    parser.add_argument(
        '-o', '--output',
        default='.',
        help='字幕輸出目錄（預設為當前目錄）',
    )
    parser.add_argument(
        '-e', '--encoding',
        choices=['utf-8', 'utf-16'],
        default='utf-8',
        help='輸出編碼（預設 utf-8）',
    )
    parser.add_argument(
        '--no-traditional',
        action='store_true',
        help='不轉換為繁體中文',
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='下載後顯示字幕預覽',
    )
    parser.add_argument(
        '-b', '--browser',
        choices=['chrome', 'firefox', 'edge', 'brave'],
        default='chrome',
        help='Cookie 來源瀏覽器（預設 chrome）',
    )
    parser.add_argument(
        '-s', '--sessdata',
        help='手動提供 SESSDATA cookie（從瀏覽器 DevTools 複製）',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='顯示詳細日誌',
    )

    args = parser.parse_args(argv)

    # 設定日誌
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s',
    )

    client = BilibiliClient(
        encoding=args.encoding,
        output_dir=args.output,
        convert_to_traditional=not args.no_traditional,
        show_preview=args.preview,
    )

    # 載入 Cookie
    if args.sessdata:
        client.set_cookie({'SESSDATA': args.sessdata})
    else:
        try:
            client.load_browser_cookie(args.browser)
        except Exception as e:
            logging.error(f'Cookie 載入失敗：{e}')
            logging.error(f'請確認 {args.browser} 已安裝且已登入 Bilibili')
            logging.error('或使用 -s SESSDATA 手動提供 Cookie（從 DevTools > Application > Cookies 複製）')
            return 1

    # 下載字幕
    try:
        result = client.download_all_subtitles(args.bv)
        print(result.summary())
        return 0 if result.failed == 0 else 1
    except Exception as e:
        logging.error(f'下載失敗：{e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
