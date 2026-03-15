# TODOS.md

## P1 — 必要改進

### ~~TODO 1: 專案架構重構~~ ✅ 已完成
- BilibiliClient class in `src/bilibili_subtitle/client.py`
- 純函數模組 `converter.py`、`requests.Session` 統一 HTTP、`pyproject.toml`

### ~~TODO 2: 全面錯誤處理~~ ✅ 已完成
- `_request_with_retry()` 自動重試 2 次
- 逐個字幕 try/except，失敗跳過繼續
- `DownloadResult` 結構化報告成功/失敗/跳過數量

### ~~TODO 3: 加入 pytest 測試~~ ✅ 已完成
- 45 個測試全部通過
- `test_converter.py`: parse_bv、sanitize_filename、format_timestamp、json_to_srt、merge_bilingual、preview_srt
- `test_client.py`: API mock、完整下載流程、重試邏輯、錯誤處理

### ~~TODO 5: 安全修復~~ ✅ 已完成
- 字幕 URL 改用 HTTPS（`client.py:_fetch_subtitle_json`）
- 日誌中不記錄 Cookie 內容（使用 logging 模組取代 print）
- `sanitize_filename` 過濾 `..` 和開頭 `/`

## P2 — 功能增強

### ~~TODO 4: CLI 模式~~ ✅ 已完成
- `bilibili-subtitle BV13f4y1G7sA -o ./subs -e utf-8 --preview -v`
- pyproject.toml entry point: `bilibili-subtitle`

### ~~TODO 6: README 更新~~ ✅ 已完成
- 修正安裝步驟（pip install -e .）
- 加入 CLI 和 GUI 使用範例
- 移除不存在的 requirements.txt 引用

## 願景項目（Delight Opportunities）

### ~~TODO 7: BV 號碼自動解析~~ ✅ 已完成
- `converter.py:parse_bv()` 支援完整 URL、手機版 URL、帶參數 URL

### ~~TODO 8: 輸出目錄選擇~~ ✅ 已完成
- CLI: `--output` 參數
- GUI: filedialog 目錄選擇器

### ~~TODO 9: 下載完成 macOS 通知~~ ✅ 已完成
- `client.py:_notify_completion()` 使用 osascript

### ~~TODO 10: 雙語字幕合併~~ ✅ 已完成
- `converter.py:merge_bilingual()` 以主要語言時間軸為準合併
- `client.py:_try_bilingual_merge()` 自動偵測中文 + 其他語言

### ~~TODO 11: 字幕預覽~~ ✅ 已完成
- `converter.py:preview_srt()` 顯示前 N 個字幕條目
- CLI: `--preview` 參數
