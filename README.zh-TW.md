# Eagle Organizer

[English](README.md) · **繁體中文**

一個 [Claude Code](https://claude.com/claude-code) skill，幫你整理 [Eagle 4.0](https://eagle.cool)
素材庫。它會用視覺分析你的圖片與影片，提出一套一致的**命名／標籤／資料夾**方案，再透過安全、
預設「先試跑」的 Python 腳本把變更套用上去。

最初是為了馴服一個龐大的 UI 參考素材庫而做，只要你在 `config.json` 填入自己的分類規則，
它適用於任何 Eagle 4.0 素材庫。

## Demo

![Eagle Organizer demo](docs/demo.zh-TW.gif)

*(Claude 為你的素材庫提出一套命名／標籤／資料夾方案 —— 你檢查後再套用。)*

## 什麼時候用這個 —— 什麼時候該用 Eagle 官方 AI

從 **Eagle 4.0 Build 12（2025 年 9 月）** 起，Eagle 內建了官方的
**[Eagle MCP／Eagle Skill](https://en.eagle.cool/support/article/eagle-mcp-server)**，讓 AI agent
透過受支援的安全 API 整理你的素材庫 —— 不動檔案、也不必先關掉 Eagle。
**如果你用的是較新的 Eagle 版本，對大多數人來說那才是建議的做法**，而且 Eagle Skill
本身就直接支援 Claude Code。

這個專案在以下這些情況特別有用：

- **Eagle 4.0 檔案層級的控制**：在沒有 MCP 外掛的版本上，或想完全離線／本機腳本、
  不跑任何 MCP server。
- **一套為產品／UI 設計參考庫量身打造、有主張的整理「系統」** —— 這些命名模板、標籤分類法，
  以及「一段流程影片歸檔在它的起始畫面底下」這類判斷邏輯 —— 而不只是通用的「幫我整理一下」。
- 想搞懂 **Eagle 4.0 在磁碟上怎麼儲存資料**（見
  [`docs/eagle-4.0-internals.md`](docs/eagle-4.0-internals.md)）。

若想用 Eagle 官方 MCP、而非內建的檔案層級腳本來跑這套方法論，
請見 [`docs/path-a-eagle-mcp-methodology.md`](docs/path-a-eagle-mcp-methodology.md)。

## ⚠️ 請先讀這段

這些腳本會**改寫 Eagle 的內部快取與 metadata 檔** —— 這正是 Eagle 儲存名稱、標籤與
資料夾歸屬的方式。威力伴隨著真實的風險：

- **套用前 Eagle 必須完全關閉（Cmd+Q）。** Eagle 會即時改寫 metadata；若它開著時腳本正在寫入，
  你的變更會遺失、或快取被弄壞。每個套用路徑都會檢查這點，Eagle 開著時會拒絕執行。
- **每個腳本預設都是試跑（dry-run）。** 它只會印出「將會」變更什麼。加上 `--apply` 才會寫入。
- **每次寫入前會自動備份**快取＋素材庫 metadata（存到 `backups/`）。項目的圖片檔名變更
  *不會*被快照，所以**第一次正式執行前，請先自行備份整個 `.library`。**
- 這個整合是從 Eagle 4.0 的磁碟格式**逆向工程**而來，在 **macOS + Eagle 4.0** 上測試過。
  未來 Eagle 更新可能改變格式，讓這些腳本失效。
- **不提供任何擔保。** 使用風險自負。見 [`LICENSE`](LICENSE)。

## 它能做什麼

- **重新命名（Rename）**：用一致的模板重新命名項目，並同步更新 Eagle 各處讀取的名稱＋資料夾＋標籤。
- **標籤（Tag）**：用你自訂的 `group-value` 詞彙為項目上標籤。
- **分類（Sort）**：依視覺分析把項目歸入資料夾。
- **拆分（Split）**：把過大的資料夾（超過 20 個項目）拆成有主題的子資料夾。

## 安裝

1. Clone 進你的 Claude Code skills 目錄：
   ```bash
   git clone https://github.com/wuning/eagle-organizer.git \
     ~/.claude/skills/eagle-organizer
   ```
   （或你專案的 `.claude/skills/` 資料夾）
2. 設定：
   ```bash
   cd ~/.claude/skills/eagle-organizer
   cp config.example.json config.json
   ```
3. 把 `config.json` 裡的 `library_path` 設成你的 `.library` 資料夾。
4. 產生你的資料夾 ID 對照表：
   ```bash
   python3 scripts/discover_folders.py
   ```
   把印出來的 `folders` 區塊貼進 `config.json`。
5. 編輯 `tags` 與 `naming` 區塊，改成你自己的系統。

`config.json` 與 `backups/` 都在 gitignore 裡，所以你真實的路徑與資料夾 ID 永遠不會被 commit。

## 使用方式

在 Claude Code 裡叫出這個 skill，然後：把圖片丟進對話、指名一個要整理的資料夾、
或問哪些資料夾需要開子資料夾。Claude 會提出一張表；你確認、並關掉 Eagle 之後，腳本才會套用。

手動執行腳本：

```bash
python3 scripts/discover_folders.py             # 唯讀：列出你的資料夾 ID
python3 scripts/rename_items.py updates.json    # 試跑預覽
python3 scripts/rename_items.py updates.json --apply
python3 scripts/subfolder_split.py split.json --apply
```

輸入檔的格式見 `examples/`。

## 需求

- macOS，且安裝 Eagle 4.0
- Python 3.8+
- 影片分析需要 `ffmpeg` + `ffprobe`：`brew install ffmpeg`

## 運作原理

Eagle 4.0 啟動時會從 `library-caches` 讀取，並把每個項目的 `metadata.json` 當作備份。
一次重新命名必須寫到五個地方才能保持一致。完整的逆向工程模型記錄在
[`docs/eagle-4.0-internals.md`](docs/eagle-4.0-internals.md)。

## 授權

MIT —— 但不提供任何擔保。見 [`LICENSE`](LICENSE)。
