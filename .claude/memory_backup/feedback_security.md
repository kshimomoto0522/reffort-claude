---
name: APIトークン・機密情報のセキュリティルール
description: コード内にAPIキー・トークンを直書きしない。必ず.envファイルで管理する
type: feedback
originSessionId: cad5d328-fbe2-462e-8502-6ca7c9ebaa09
---
## ルール：APIトークン・機密情報はコードに直書きしない

すべてのAPIキー、トークン、パスワード等の機密情報は`.env`ファイルで管理し、コード内では`os.getenv()`で読み込む。

**Why:** 2026-03-21に発覚。eBay Auth Token、Chatwork Token、Slack Bot Tokenがすべてコード内に直書きされており、GitHubリポジトリ（Private）にpush済みだった。Publicに変わった場合やアカウント乗っ取り時に全トークンが漏洩するリスクがあった。

**How to apply:**
- 新しいスクリプトを作成する際、APIキーやトークンは必ず`.env`ファイルに入れる
- コード内では`from dotenv import load_dotenv` + `os.getenv('KEY_NAME')`で読み込む
- `.gitignore`に`.env`が登録されていることを確認する
- 既存スクリプトでトークン直書きを見つけた場合、即座に.envに移行する
- 社長にトークンの入力を求める場合もチャット欄ではなく.envファイルへの記入を案内する

## 対応済みファイル（2026-03-21）
- `commerce/ebay/analytics/create_weekly_report_v3.py` → .env化完了
- `commerce/ebay/analytics/send_weekly_report.py` → .env化完了
- `slack_helper.py` → .env化完了
- `download_slack_files.py` → .env化完了
- `services/baychat/ai/` → 元から.env管理（対応不要）

---

## ⚠️ .env の中身を絶対にチャットに出力しない（2026-04-15 追加・最重要）

### 絶対ルール
`.env`（および `.env.vps`, `.env.local`, `.env.prod` など派生ファイル全般）の**中身を stdout に出すあらゆる操作を禁止**する。値がチャット履歴・セッションJSONL・GitHubバックアップ対象の領域に残るため、プライベートDMで渡された認証情報でも漏洩リスクを拡大してしまう。

### 背景（ミス事例 2026-04-15）
BayChat STG DB接続のデバッグ中、`.env` を `cat | grep` してパスワード値（`BAYCHAT_STG_DB_PASSWORD`）をチャットに露出させた。クエットさんから個別DMで渡された認証情報をセッションログ領域に広げてしまった重大な判断ミス。社長から「ギリアウト。パスワード等を公開チャットで伝えることは絶対にあってはならない」と指摘。

### 禁止コマンド（`.env` を引数に取る場合）
- `cat` / `type` / `more` / `less` / `head` / `tail`
- `grep` / `rg` / `awk` / `sed` / `cut` / `strings`
- `echo $(cat .env)` のような間接出力
- PowerShellの `Get-Content` / `gc` / `Select-String`
- `printenv` / `env`（load後に実行するとexportされた値が出る）

### 正しい確認方法
```bash
# 1. SET/UNSET のみ確認（値は絶対に表示しない）
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('SET' if os.getenv('KEY_NAME') else 'UNSET')"

# 2. キー名だけ一覧（値なし）
python -c "from dotenv import dotenv_values; print(list(dotenv_values('.env').keys()))"

# 3. ファイル存在チェックのみ
ls .env
```

### 物理ブロック（2026-04-15 実装済み）
- `.claude/settings.local.json` の `deny` に `Read(**/.env)` `Read(**/.env.*)` 系を登録
- `.claude/hooks/block_env_exposure.py`（PreToolUse:Bash）が cat/grep/type 等で `.env` を参照するコマンドを検出して停止

### 適用範囲（徹底事項）
BayChatだけでなく**全部門・全タスク**に適用する。eBay・Campers・BayPack・ダイレクト販売・ツール開発・どのプロジェクトでも例外なし。
