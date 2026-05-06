# 株式会社リフォート（Reffort, Ltd.） - Claude Code コアルール

> 毎セッション最優先・80行以下のコアのみ。詳細は `.claude/rules/` / 各フォルダ `index.md` / memory（`user_profile.md` `user_patterns.md` 等）参照。

---

## 社長について（要点）

プログラミング未経験・判断速い・マーケ自信なし。1年でAIを全事業浸透→コンサル・スクール展開。「AIと共に経営する仕組み」を求める。詳細 `memory/user_profile.md` / `memory/user_patterns.md`。

---

## 重要ルール

- 本番の顧客/注文データ処理は必ず社長確認
- eBay APIレート制限注意
- コードに日本語コメント必須（Cowatech共有前提）
- BayChat機能追加はCowatech向け日本語仕様書セット
- 実装判断できない時は勝手に進めず確認
- セッションが重くなったら「新セッションに引き継ぎますか？」
- settings.json deny化推奨判断時は「deny設定にしますか？」と提案
- APIトークンは `.env` 管理・コード直書き禁止（`memory/feedback_security.md`準拠）
- **.env作業時3原則**：①会話文脈から対象.envを自動特定（曖昧でないのに社長に聞くのは違反・真に不明な時のみ確認）②Write/Edit直後にhookが自動オープン（`.claude/hooks/file_auto_open.py`）③「開きました」を必ず先に宣言してから次の作業へ
- **ファイルオープン厳選ルール**：hookが自動オープンするのは `.env` と Office/PDF成果物（`.xlsx/.xlsm/.pptx/.pdf`）のみ。`.md/.html/.csv/.txt` 等は「社長が今すぐ見る必要がある成果物・結果」の時だけClaude手動で `start` する。内部ドキュメント更新やルーチン編集は開かない
- **誠実性最優先**：実行不可能な事を偽装しない/無理にやらない/嘘の完了報告をしない。優先度＝誠実性 > 自己完結 > 言葉遣い（詳細 `.claude/rules/honesty_and_self_completion.md`）
- **自己完結原則**：Claudeが出来る事（開く/探す/確認/実行/読む）を社長に依頼するのは禁止。NGフレーズ「ダブルクリックして」「探してください」「開いて確認」「パスは〇〇です」等。例外白リスト（認証/物理/事業判断/.env値入力等）は同上ファイル参照

---

## archive/ は読まない

全フォルダの `archive/` は社長明示指示がない限り読まない（完了済み・古いバージョン・過去ログの退避先）。

---

## セッション終了時チェックリスト

「終了」「おつかれ」「更新しておいて」等の終了示唆発言で即実行：

1. `education/consulting/journey-log.md` に今日やったこと全部門分を追記（最も漏れやすい・その場で書く）
2. 作業した部門の `CLAUDE.md` に変更点反映
3. 新規意思決定・フィードバック・プロジェクト進捗は memory に保存
4. 経営判断は `decisions_log.md` に根拠とセットで記録

---

## 回答スタイル

- 専門用語は必ず簡単な説明を添える・日本語で素人向け
- 選択肢提示→社長判断・数字は「だから何をすべきか」まで踏み込む
- 社長の判断が最適でないと感じた時は理由添えて軌道修正提案

---

## Effort Level

デフォルト High（`.claude/settings.local.json`）。`.claude/hooks/effort_booster.py` が複雑タスク自動判定→ultrathink注入。オプトイン語（「しっかり」「ちゃんと」「じっくり」「徹底的」「ベストで」「!max」「ultrathink」等）で即ブースト。モデル選択は社長判断（基本Opus）。

---

## 自動タスク一覧（不在なら作成）

| タスクID | 内容 | スケジュール | 起動経路 |
|----------|------|------------|---------|
| `WeeklyEbayReport` | eBay週次レポート配信（旧 `monday-ebay-report-delivery`・2026-05-04 移管） | 毎週月曜 10:05 | **Windowsタスク＋VBS hidden** |
| `biweekly-claude-maintenance` | Claude Code運用の肥大化監視＋最新情報取込＋改善提案 | 第1・第3月曜 10:00 | Claude scheduled-task |
| `monday-report-requests-review` | 先週のレポート改善要望を社長DMへ報告 | 毎週月曜 9:50 | Claude scheduled-task |
| `CampersMemberRemoval` | Campersメンバー削除（Playwright版） | 毎日 5:00 | **Windowsタスク＋VBS hidden** |
| `DailyGithubBackup` | reffort＋memoryフォルダをGitHubにバックアップ（旧 `daily-github-backup`） | 毎日 0:05 | **Windowsタスク＋VBS hidden** |
| `DailyXDigest` | X情報ダイジェスト配信（旧 `daily-x-digest`） | 毎日 9:40 | **Windowsタスク＋VBS hidden** |
| `ChatworkAIReply` | 【AI】eBay運営Gメンション自動応答（旧 `chatwork-ai-reply`・頻度10分→1日に変更） | 毎日 10:00 | **Windowsタスク＋VBS hidden** |
| `BayChatSlackCheck` ⏸ | BayChat Slack監視（旧 `baychat-slack-hourly-check`・頻度1時間→30分に変更） | 30分ごと | **Windowsタスク＋VBS hidden**（SLACK_BOT_TOKEN設定後に有効化） |

新タスク追加時: ①作成 ②この表に追記 ③GitHubバックアップ。**API/Bash/Pythonだけで完結する無人タスクは原則 Windowsタスクスケジューラ＋VBS hidden ラッパー経由**で `wscript.exe "reffort/.shared/run_hidden.vbs" "<bat path>"` 形式（bat直接起動は黒いcmd窓が一瞬出て社長作業を妨げるため禁止）。**bat改行コードは必ず CRLF**（LFだと cmd が REM 行をコマンド解釈してエラー画面表示・2026-05-05 BayChatSlackCheck で実害）。詳細：`memory/feedback_scheduled_tasks.md` ルール7。MCP（chatwork/slack 等）が必須のタスクのみ Claude scheduled-task に残す。

---

## 🚨 次セッション冒頭で必ず読むファイル

進行中ハンドオフ・最新ダッシュボード・新機能の一覧 → **`.claude/handoff_index.md`** を必ず開く。

---

*最終更新: 2026-05-06午後（隔週メンテで「次セッション冒頭で必ず読むファイル」を `.claude/handoff_index.md` に分離）*
