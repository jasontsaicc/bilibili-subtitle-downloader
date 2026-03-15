# Bilibili 字幕下載器

> 下載 Bilibili 影片字幕並轉換為 SRT 格式，支援繁體轉換、雙語合併、CLI 與 GUI 雙模式
>
> Download Bilibili video subtitles as SRT files with CHS→CHT conversion, bilingual merge, CLI & GUI

## 功能

- 輸入 BV 號碼或完整 URL，自動下載所有分集字幕
- 簡體中文自動轉換為繁體中文（可關閉）
- 支援多語言字幕（中文、日文、英文等）
- 自動合併雙語字幕（中文 + 其他語言），適合語言學習
- CLI 命令列 + GUI 圖形介面雙模式
- UTF-8 / UTF-16 編碼選擇
- 失敗自動重試、跳過失敗繼續下載
- 下載完成 macOS 通知

## 安裝

```bash
git clone https://github.com/jasontsai1256/bilibili-subtitle.git
cd bilibili-subtitle
pip install -e .
```

## 使用方式

### CLI 命令列

```bash
# 基本用法
bilibili-subtitle BV13f4y1G7sA

# 指定輸出目錄和編碼
bilibili-subtitle BV13f4y1G7sA -o ./subtitles -e utf-16

# 貼上完整 URL 也可以
bilibili-subtitle "https://www.bilibili.com/video/BV13f4y1G7sA"

# 顯示字幕預覽
bilibili-subtitle BV13f4y1G7sA --preview

# 不轉換繁體
bilibili-subtitle BV13f4y1G7sA --no-traditional

# 詳細日誌
bilibili-subtitle BV13f4y1G7sA -v
```

### GUI 圖形介面

```bash
python -m bilibili_subtitle.gui
```

1. 在 Firefox 登入 Bilibili
2. 點擊「載入 Firefox Cookie」
3. 輸入 BV 號碼或貼上完整 URL
4. 選擇輸出目錄和編碼
5. 點擊「下載字幕」

## 輸出範例

```
=== 下載完成 ===
成功：48 個字幕
失敗：2 個字幕
跳過（無字幕）：0 集
總共：25 集
失敗詳情：
  - P12（第十二集）：網路逾時
  - P18（第十八集）：無字幕
```

字幕檔案命名格式：
```
BV13f4y1G7sA - P1：第一集 - zh-CN.srt        # 單語字幕
BV13f4y1G7sA - P1：第一集 - zh+ja.srt         # 雙語合併字幕
```

## 開發

```bash
# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest

# 執行測試（詳細模式）
pytest -v
```

## 專案結構

```
src/bilibili_subtitle/
├── client.py      # BilibiliClient — API 呼叫、Cookie 管理、下載流程
├── converter.py   # 純函數 — JSON→SRT 轉換、檔名清理、BV 解析、雙語合併
├── cli.py         # argparse CLI 入口
└── gui.py         # Tkinter GUI 入口
```

## 需求

- Python >= 3.9
- Firefox 瀏覽器（用於載入 Bilibili Cookie）

## 授權

MIT License
