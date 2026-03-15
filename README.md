# Bilibili 字幕下載器 | Bilibili Subtitle Downloader

> 下載 Bilibili 影片字幕並轉換為 SRT 格式，支援繁體轉換、雙語合併、CLI 與 GUI 雙模式
>
> Download Bilibili video subtitles as SRT files with CHS→CHT conversion, bilingual merge, CLI & GUI

## 功能 | Features

- 輸入 BV 號碼或完整 URL，自動下載所有分集字幕 | Auto-download all episode subtitles by BV number or full URL
- 簡體中文自動轉換為繁體中文（可關閉）| Auto CHS→CHT conversion (optional)
- 支援多語言字幕（中文、日文、英文等）| Multi-language subtitle support (ZH, JA, EN, etc.)
- 自動合併雙語字幕（中文 + 其他語言），適合語言學習 | Auto bilingual subtitle merge, great for language learning
- CLI 命令列 + GUI 圖形介面雙模式 | CLI + GUI dual mode
- 多瀏覽器 Cookie 支援（Chrome、Firefox、Edge、Brave）| Multi-browser cookie support
- 手動 SESSDATA Cookie 輸入 | Manual SESSDATA cookie input
- UTF-8 / UTF-16 編碼選擇 | Encoding selection
- 失敗自動重試、跳過失敗繼續下載 | Auto-retry on failure, skip and continue
- 下載完成 macOS 通知 | macOS notification on completion

## 安裝 | Installation

```bash
git clone https://github.com/jasontsai1256/bilibili-subtitle.git
cd bilibili-subtitle
pip install -e .
```

## 使用方式 | Usage

### CLI 命令列 | Command Line

```bash
# 基本用法 | Basic usage
bilibili-subtitle BV13f4y1G7sA

# 指定輸出目錄和編碼 | Specify output directory and encoding
bilibili-subtitle BV13f4y1G7sA -o ./subtitles -e utf-16

# 貼上完整 URL 也可以 | Full URL also works
bilibili-subtitle "https://www.bilibili.com/video/BV13f4y1G7sA"

# 指定瀏覽器（預設 chrome）| Specify browser (default: chrome)
bilibili-subtitle BV13f4y1G7sA -b edge

# 手動提供 SESSDATA Cookie | Manual SESSDATA cookie
bilibili-subtitle BV13f4y1G7sA -s "your_sessdata_value"

# 顯示字幕預覽 | Show subtitle preview
bilibili-subtitle BV13f4y1G7sA --preview

# 不轉換繁體 | Disable CHT conversion
bilibili-subtitle BV13f4y1G7sA --no-traditional

# 詳細日誌 | Verbose logging
bilibili-subtitle BV13f4y1G7sA -v
```

### GUI 圖形介面 | Graphical Interface

```bash
python -m bilibili_subtitle.gui
```

1. 在瀏覽器登入 Bilibili | Log in to Bilibili in your browser
2. 點擊「載入 Cookie」| Click "Load Cookie"
3. 輸入 BV 號碼或貼上完整 URL | Enter BV number or paste full URL
4. 選擇輸出目錄和編碼 | Choose output directory and encoding
5. 點擊「下載字幕」| Click "Download"

### Cookie 說明 | Cookie Notes

由於 Chrome 127+ 使用新的加密方式，`browser_cookie3` 可能無法讀取 Chrome Cookie。建議方案：

Due to Chrome 127+ App-Bound Encryption, `browser_cookie3` may fail to read Chrome cookies. Recommended solutions:

| 方案 Solution | 說明 Description |
|---|---|
| 使用 Edge | `bilibili-subtitle BV... -b edge` — Edge Cookie 可正常讀取 |
| 使用 Firefox | `bilibili-subtitle BV... -b firefox` |
| 手動 SESSDATA | `bilibili-subtitle BV... -s "your_sessdata"` — 從 DevTools > Application > Cookies 複製 |

## 輸出範例 | Output Example

```
=== 下載完成 ===
成功：35 個字幕
失敗：0 個字幕
跳過（無字幕）：0 集
總共：35 集
```

字幕檔案命名格式 | File naming format:
```
BV13f4y1G7sA - P1：第一集 - ai-zh.srt        # AI 生成字幕 | AI-generated subtitle
BV13f4y1G7sA - P1：第一集 - zh-CN.srt         # 單語字幕 | Single language
BV13f4y1G7sA - P1：第一集 - zh+ja.srt         # 雙語合併 | Bilingual merge
```

## 開發 | Development

```bash
# 安裝開發依賴 | Install dev dependencies
pip install -e ".[dev]"

# 執行測試 | Run tests
pytest

# 執行測試（詳細模式）| Run tests (verbose)
pytest -v
```

## 專案結構 | Project Structure

```
src/bilibili_subtitle/
├── client.py      # BilibiliClient — API calls, cookie management, download flow
├── converter.py   # Pure functions — JSON→SRT, filename sanitization, BV parsing, bilingual merge
├── cli.py         # argparse CLI entry point
└── gui.py         # Tkinter GUI entry point
```

## 需求 | Requirements

- Python >= 3.9
- 瀏覽器（Edge / Firefox / Chrome / Brave）用於載入 Bilibili Cookie
- Browser (Edge / Firefox / Chrome / Brave) for loading Bilibili cookies

## 授權 | License

MIT License
