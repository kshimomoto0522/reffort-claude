# 2026-04-28：Chrome MCP既知バグ回避 + clasp導入による仕入管理表移行

> 単一セッションで3つの大きな出来事が連鎖的に発生。それぞれが独立した教材になる素材。

## サマリー

| 項目 | 概要 |
|------|------|
| きっかけ | Chatwork APIトークン更新 → 関連スケジュールタスクの稼働確認 → Campersメンバー削除タスクで permission_required エラー発生 |
| 大きな発見 | Anthropic 側の Chrome MCP / scheduled-task の既知バグ（Issue #30356, #47180）がReffortでも顕在化していた |
| 構造的な解決 | ① Playwright + Windowsタスクスケジューラ直接起動（Chrome操作必須タスク用）／② clasp による GAS全体管理（Apps Scriptコード更新用） |
| 副次成果 | スプレッドシート自動化の3型ルーティング（A=GAS/clasp、B=外部Python/Sheets API、C=UI操作/Playwright）を memory に確定 |

## 物語仕立てのタイムライン（教材化用）

### 起点：トークン更新で既存タスクの不整合発覚（午前）
- Chatwork APIトークンを社長が新規発行＆.env 更新
- ところがClaudeが調べると、新トークンは `commerce/ebay/analytics/.env` にしか反映されておらず、`management/x-digest/.env` と `~/.claude.json` MCP設定2箇所は **古い無効トークンのまま**
- → 3箇所同期＋疎通テスト（/me API）でアカウント名「+REFFORT AI+」確認

### 第1の壁：eBay週次レポート4/27月曜分が未配信
- 月曜 PCが落ちていたためタスクが空打ち、Excel未生成
- 手動で `create_weekly_report_v3.py` 実行（72ページ・14,247件取得）→ Excel + Google Sheets 12シート生成 → Chatwork【AI】eBay運営に遅延配信
- ✅ 解決

### 第2の壁：Campersメンバー削除タスクが連続失敗
- 4/25削除予定の井上慶成さん、3部屋全てに在籍したまま（タスクは毎朝5:00で動いているはず）
- Claude scheduled-task `campers-member-removal-goto` を再fire → 権限OFF前のChrome navigate で `permission_required` エラー
- 既知バグ調査：[#30356](https://github.com/anthropics/claude-code/issues/30356) / [#47180](https://github.com/anthropics/claude-code/issues/47180) — Cowork(scheduled-task)からのbridge requestは `permissionMode="ask"` 固定、拡張側の `permissionStorage`（"Always allow on this site"）を参照しない
- → **このバグはAnthropic側の問題でReffortからは直せない**

### 中継案の挫折：Playwright移行 + Claude scheduled-task経由
- Chrome MCPを使わず Python + Playwright で直接Chatwork UIを操作する設計
- セレクタ調査（`room-header_room-settings-button` → `room-settings-menu` → `button:has-text("権限")` → トグル2つのlabel）
- DRY-RUN（権限OFF→ON のみ）成功
- 本番実行（井上慶成削除）成功（68→67、72→71、68→67、queue更新、権限verified=True）✅
- だが、その後 Claude scheduled-task 経由で Python script を呼ぶ構成は**プロンプト変更で per-task 承認キャッシュが無効化されfire しない**現象が再発
- → Claude Code を中継させる構成自体を捨てる決断

### 第2の壁の最終解決：Windowsタスクスケジューラ直接起動
- `register-removal-task.ps1` で Windowsタスク `CampersMemberRemoval` を登録（毎朝5:00・バッテリー対応・スリープ復帰時実行）
- bat ラッパー → python → DM 報告のシンプル構造、Claude Code 中継ゼロ
- 旧タスク `CampersChromeRestart` 削除、Claude scheduled-task 無効化
- 即時起動テストで exit_code=0 / DM配信 / ログ生成 全て確認 ✅

### 第3の壁：仕入管理表のコード更新の手作業（Monaco貼付け）
- 社長が「Chrome開いて編集できない問題」を再認識して質問
- 調査で **clasp（Google公式CLI）が既にインストール済み（v3.3.0）** と判明（npm install -g clasp済・未使用）
- `clasp login` → `clasp clone` で本番GASをローカル展開 → 既存マスター `gas_shiire_tool.js` と **完全一致**（1780行・61,496文字）
- `clasp push` 動作確認 → 「Script is already up to date」
- 旧Monaco貼付け補助ファイル6個（gas_shiire_tool.js / gas_copy.html / gas_shiire_b64.txt / gas_shiire_content.json / serve_gas.py / update_gas_copy.py）を削除
- 構造を `commerce/ebay/tools/gas/shiire/コード.js` に集約

## 数値Before/After

| 項目 | Before | After |
|------|--------|-------|
| 仕入管理表コード更新の所要時間 | 数分（PowerShellクリップボード→Chrome→Monaco→手動Ctrl+V→8秒wait→Ctrl+S） | 数秒（`clasp push` 一発） |
| 仕入管理表コード更新の失敗率 | 度々（Monaco大規模ペースト遅延・Chrome保護でCtrl+V失敗） | ほぼゼロ（Google公式API経由） |
| Campers削除の依存関係 | Chrome起動＋ログイン状態＋Claude in Chrome MCP＋per-task承認キャッシュ | Playwright cookie のみ（cookieは数週〜数ヶ月有効） |
| 起動経路の中継数 | scheduled-task → fresh Claudeセッション → Bash → MCP → Chrome拡張 → Chatwork | Windowsタスク → bat → python → Chatwork API |
| 関連obsoleteファイル数 | 6個（合計約210KB） | 0個（削除済み） |

## 判断ポイント（受講生向け）

### 判断1：Playwrightへの全面移行は妥当か
- ✅ 妥当
- 理由：Anthropic 側の修正タイミングが見えない・無人実行で詰まると社長業務に直撃する。Reffortで自前完結する道を選んだ。
- 副次効果：今後 Chatwork UI が変わってもセレクタ修正で追従可能、Claude Code バージョンアップに依存しない。

### 判断2：Claude scheduled-task ではなく Windowsタスクで直接起動
- ✅ 妥当
- 理由：Claude scheduled-task の per-task 承認キャッシュ問題は再現性が低くデバッグ困難。中継層を排除すれば原因切り分けが容易。
- トレードオフ：ログがClaude Code側のtrace UIから見えなくなる。代わりに `scripts/logs/removal_*.log` で確認する運用に変更。

### 判断3：clasp 移行で旧ファイル6個を即削除
- ✅ 妥当
- 理由：git履歴に残るので必要時は復元可能。両方残すと「どっちが正？」になり混乱の元。
- リスクヘッジ：spec MDの「設計変遷」に旧手順を残し、なぜ廃止したかを将来読者に伝わるようにした。

## 学び（教材化エッセンス）

### 学び1：「ツール側の既知バグ」を疑う癖
- Reffortのコードに問題があるとは限らない。Anthropic側のIssueトラッカー検索は重要なデバッグ手段。
- 知らないとずっと自分のせいにして時間を溶かす。

### 学び2：「公式CLI」がある領域は迷わずそれを使う
- Apps Script 編集は Monaco editor で頑張る前に `clasp` を確認する。
- Google Sheets 操作は service account + API。Drive操作は `gdrive` CLI / Google Drive API。
- 公式CLIがあるのに自前でブラウザ操作を組むのは負け筋。

### 学び3：自動化レイヤーの中継数は最小化する
- 「Claude scheduled-task → fresh Claude session → Bash → MCP → Chrome拡張」のような長い中継は壊れやすい。
- 「Windowsタスク → python」の2層なら原因切り分けが即できる。

### 学び4：認証は1回・サイト全体が原則
- `clasp login` 1回で全Apps Script。
- service account JSON 1個で全シート（共有さえすれば）。
- Playwright cookie 1個で1サイト全体。
- 案件ごとに認証スキームをバラバラに作るのは将来の負債。

## 残課題・次セッション申し送り

1. ✅ 4/30 朝5:00 の Kento さん削除が **本番運用での初検証**（PCがスリープでもバッテリー対応設定済み）
2. ⏭️ 他の GASプロジェクトを clasp化する候補があるか棚卸し（社長判断）
3. ⏭️ 受講生向けに「自社のスプレッドシート3型棚卸しシート」を作成（コンサル教材化時）
4. ⏭️ Anthropic Issue #30356/#47180 のステータスを定期チェック（修正されたら scheduled-task 経由でも安心して動かせるようになる）

## 関連ファイル / コードへの直リンク

- 仕入管理表マスター: [commerce/ebay/tools/gas/shiire/コード.js](commerce/ebay/tools/gas/shiire/コード.js)
- 仕入管理表 spec: [commerce/ebay/tools/gas-shiire-tool-spec.md](commerce/ebay/tools/gas-shiire-tool-spec.md)
- Campers削除スクリプト: [education/campers/scripts/campers_member_removal.py](education/campers/scripts/campers_member_removal.py)
- Campers削除batラッパー: [education/campers/scripts/run_campers_removal.bat](education/campers/scripts/run_campers_removal.bat)
- Windows タスク登録 ps1: [education/campers/scripts/register-removal-task.ps1](education/campers/scripts/register-removal-task.ps1)
- 3型ルーティング memory: `feedback_spreadsheet_automation_patterns.md`
- Chrome無人タスク方針 memory: `feedback_chrome_mcp_unattended.md`
