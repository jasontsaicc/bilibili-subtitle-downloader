"""Tkinter GUI 介面"""

import logging
import threading
import tkinter as tk
from tkinter import filedialog

from bilibili_subtitle.client import BilibiliClient

logger = logging.getLogger(__name__)


class TextHandler(logging.Handler):
    """將 log 輸出導向 Tkinter Text widget。"""

    def __init__(self, text_widget: tk.Text):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record) + '\n'
        self.text_widget.after(0, self._append, msg)

    def _append(self, msg: str):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')


class BilibiliSubtitleGUI:
    """Bilibili 字幕下載器 GUI"""

    def __init__(self):
        self.client = BilibiliClient()
        self._downloading = False
        self._build_ui()
        self._setup_logging()

    def _build_ui(self):
        self.window = tk.Tk()
        self.window.title('Bilibili 字幕下載器 V6')
        self.window.geometry('600x500')
        self.window.minsize(500, 400)

        # === 標題 ===
        tk.Label(
            self.window,
            text='Bilibili 字幕下載器 V6',
            font=('Helvetica', 20, 'bold'),
            pady=10,
        ).pack()

        # === BV 輸入區 ===
        frame_input = tk.Frame(self.window)
        frame_input.pack(fill='x', padx=20, pady=5)

        tk.Label(frame_input, text='BV 號碼或 URL：', font=('Helvetica', 13)).pack(side='left')
        self.bv_entry = tk.Entry(frame_input, font=('Helvetica', 13))
        self.bv_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))

        # === 設定區 ===
        frame_settings = tk.Frame(self.window)
        frame_settings.pack(fill='x', padx=20, pady=5)

        # 編碼選擇
        tk.Label(frame_settings, text='編碼：', font=('Helvetica', 12)).pack(side='left')
        self.encoding_var = tk.StringVar(value='utf-8')
        tk.Radiobutton(
            frame_settings, text='UTF-8', variable=self.encoding_var,
            value='utf-8', font=('Helvetica', 12),
        ).pack(side='left')
        tk.Radiobutton(
            frame_settings, text='UTF-16', variable=self.encoding_var,
            value='utf-16', font=('Helvetica', 12),
        ).pack(side='left')

        # 輸出目錄
        frame_output = tk.Frame(self.window)
        frame_output.pack(fill='x', padx=20, pady=5)

        tk.Label(frame_output, text='輸出目錄：', font=('Helvetica', 12)).pack(side='left')
        self.output_var = tk.StringVar(value='.')
        tk.Entry(
            frame_output, textvariable=self.output_var, font=('Helvetica', 12),
        ).pack(side='left', fill='x', expand=True, padx=(5, 5))
        tk.Button(
            frame_output, text='選擇', command=self._choose_output_dir,
            font=('Helvetica', 12),
        ).pack(side='left')

        # === 按鈕區 ===
        frame_buttons = tk.Frame(self.window)
        frame_buttons.pack(fill='x', padx=20, pady=10)

        self.cookie_btn = tk.Button(
            frame_buttons, text='載入 Firefox Cookie',
            command=self._load_cookie, font=('Helvetica', 13),
        )
        self.cookie_btn.pack(side='left', padx=(0, 10))

        self.download_btn = tk.Button(
            frame_buttons, text='下載字幕',
            command=self._start_download, font=('Helvetica', 13, 'bold'),
        )
        self.download_btn.pack(side='left')

        # === 日誌輸出區 ===
        self.log_text = tk.Text(
            self.window, height=12, state='disabled',
            font=('Menlo', 11), bg='#1e1e1e', fg='#d4d4d4',
        )
        self.log_text.pack(fill='both', expand=True, padx=20, pady=(5, 20))

        # 捲軸
        scrollbar = tk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _setup_logging(self):
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

        logger.info('歡迎使用 Bilibili 字幕下載器 V6')
        logger.info('1. 請先在 Firefox 登入 Bilibili，然後點擊「載入 Firefox Cookie」')
        logger.info('2. 輸入 BV 號碼（或貼上完整 URL），點擊「下載字幕」')
        logger.info('3. 預設編碼為 UTF-8，如字幕亂碼可改選 UTF-16')

    def _choose_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_var.set(directory)

    def _load_cookie(self):
        try:
            self.client.load_firefox_cookie()
        except Exception as e:
            logger.error(f'Cookie 載入失敗：{e}')
            logger.error('請確認 Firefox 已安裝且已登入 Bilibili')

    def _start_download(self):
        bv = self.bv_entry.get().strip()
        if not bv:
            logger.error('請輸入 BV 號碼或 Bilibili 影片 URL')
            return

        if not self.client._cookie_loaded:
            logger.error('請先載入 Cookie')
            return

        if self._downloading:
            return

        # 更新客戶端設定
        self.client.encoding = self.encoding_var.get()
        self.client.output_dir = self.output_var.get()

        # 停用按鈕，防止重複點擊
        self._downloading = True
        self.download_btn.configure(state='disabled', text='下載中...')
        self.cookie_btn.configure(state='disabled')

        thread = threading.Thread(target=self._download_worker, args=(bv,), daemon=True)
        thread.start()

    def _download_worker(self, bv: str):
        try:
            result = self.client.download_all_subtitles(bv)
            logger.info(result.summary())
        except Exception as e:
            logger.error(f'下載失敗：{e}')
        finally:
            self.window.after(0, self._download_finished)

    def _download_finished(self):
        self._downloading = False
        self.download_btn.configure(state='normal', text='下載字幕')
        self.cookie_btn.configure(state='normal')

    def run(self):
        self.window.mainloop()


def main():
    app = BilibiliSubtitleGUI()
    app.run()


if __name__ == '__main__':
    main()
