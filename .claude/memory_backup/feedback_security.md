---
name: APIトークン・機密情報のセキュリティルール（統合版：トークン管理＋settings.json設定）
description: コード直書き禁止・.env管理必須・.env中身の出力禁止＋deny設定判断基準・トークン管理・.envブロック
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

## 🚨 2026-04-29 重大インシデント発覚：eBay OAuth tokens が GitHub Private repo に commit されていた

DailyGithubBackup の Windows 化作業中、Pythonスクリプト側の機密ファイル混入チェックが `commerce/ebay/analytics/ebay_oauth_tokens.json` と `ebay_seller_cache.json` を検出。`git log` で確認すると、両ファイルは **2026-04-23 の初回大規模push（commit 6761123）から最新まで履歴に含まれていた**。

**漏洩リスク評価：**
- リポジトリは Private（kshimomoto0522/reffort-claude）
- アクセス権は社長（owner）と Claude Code セッションのみ
- 即時の漏洩リスクは低いが、リポジトリが Public 化／アカウント乗っ取り／GitHub側障害があれば全 OAuth トークンが漏洩
- ベストプラクティス的にはトークンrotate＋履歴削除（git filter-repo / BFG）すべき

**実施した応急処置（2026-04-29）：**
1. `.gitignore` に追加：`**/ebay_oauth_tokens.json` `**/ebay_seller_cache.json` `**/oauth_tokens*.json` `**/*_oauth_state.json`
2. `git rm --cached` で tracking 解除
3. commit `21bd3bd` 「security: remove sensitive eBay OAuth token files from tracking」をpush
4. 以後、daily-github-backup の Windows 版（github_backup.py）が自動で「A/M」のみ機密チェックする実装になっており、再混入は構造的にブロック

**残タスク（社長判断）：**
- ⚠️ **eBay OAuth refresh token の rotate**（最も推奨。漏洩していなくても安全側に倒す）
- ⚠️ git history から該当ファイルを完全削除（git filter-repo or BFG・履歴を書き換える破壊的操作）
- 並行：他のjson（`weekly_history.json` `weekly_notes.json` `removal-queue.json`）が機密を含まないかレビュー

**How to apply:**
- 新規Pythonスクリプトでトークンキャッシュを書き出す時は **必ず** その時点で `.gitignore` 追加とセットで実施
- タスク作成・引継ぎ時は「このスクリプトはどこにキャッシュ／状態ファイルを書くか？」を最初に確認
- daily-github-backup（github_backup.py）の機密検出ロジックは「最後の防衛線」として常にON。検出されたら必ず社長報告

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

---

## settings.local.json セキュリティ設定の判断基準（2026-03-26）

### セキュリティは「やり直せるか？」で判断する

- やり直せる操作（ファイル編集・検索・分析）→ Always allowでOK
- やり直せない操作（git push --force、git reset --hard）→ deny設定で禁止
- 外に出る操作（メッセージ送信・API呼び出し）→ 毎回確認

### deny設定済み（2026-03-26・現行）
- `git push --force` / `-f`（全パターン）
- `git reset --hard`（全パターン）
- `Read(**/.env)` / `Read(**/.env.*)`

### トークン管理ルール
- curlでAPIを直接叩く許可を出すと、settings.local.jsonにトークンが丸ごと記録される
- MCP経由（mcp__chatwork__、mcp__slack__）ならトークンが見えないので安全
- 今後APIを叩く必要がある場合は、curlではなくMCPまたはPythonスクリプト（.envから読む）経由で行う

### .envブロックの理由（社長の洞察）
- 社長自身が「読んで」と指示する分には問題ない
- 問題は外部からの指示（プロンプトインジェクション）でClaudeが.envを読まされ、外部に送信させられるリスク
- .envの直接読み取りをブロックすることで、仮に騙されても読めない状態にした

**Why:** settings.local.jsonにAPIトークンが丸出しで記録されていた問題が発覚。.envに隠しても許可設定側に残る落とし穴
**How to apply:** 新しいAPI連携を設定するときは必ずMCPまたは.env経由。curlで直接トークンを渡す許可は出さない
