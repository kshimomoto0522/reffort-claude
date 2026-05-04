# 株式会社Reffort - Claude Code コアルール

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
| `WeeklyEbayReport` | eBay週次レポート配信（旧 `monday-ebay-report-delivery`・2026-05-04 移管） | 毎週月曜 10:05 | **Windowsタスクスケジューラ直接** |
| `biweekly-claude-maintenance` | Claude Code運用の肥大化監視＋最新情報取込＋改善提案 | 第1・第3月曜 10:00 | Claude scheduled-task |
| `monday-report-requests-review` | 先週のレポート改善要望を社長DMへ報告 | 毎週月曜 9:50 | Claude scheduled-task |
| `CampersMemberRemoval` | Campersメンバー削除（Playwright版） | 毎日 5:00 | **Windowsタスクスケジューラ直接** |
| `DailyGithubBackup` | reffort＋memoryフォルダをGitHubにバックアップ（旧 `daily-github-backup`） | 毎日 0:05 | **Windowsタスクスケジューラ直接** |
| `DailyXDigest` | X情報ダイジェスト配信（旧 `daily-x-digest`） | 毎日 9:40 | **Windowsタスクスケジューラ直接** |
| `ChatworkAIReply` | 【AI】eBay運営Gメンション自動応答（旧 `chatwork-ai-reply`・頻度10分→1日に変更） | 毎日 10:00 | **Windowsタスクスケジューラ直接** |
| `BayChatSlackCheck` ⏸ | BayChat Slack監視（旧 `baychat-slack-hourly-check`・頻度1時間→30分に変更） | 30分ごと | **Windowsタスクスケジューラ直接**（SLACK_BOT_TOKEN設定後に有効化） |

新タスク追加時: ①作成 ②この表に追記 ③GitHubバックアップ。**API/Bash/Pythonだけで完結する無人タスクは原則 Windowsタスクスケジューラ直接起動**（Claude scheduled-task の承認キャッシュ減衰によるサイレント停止問題回避・2026-04-29 daily-x-digest で実害確認）。MCP（chatwork/slack 等）が必須のタスクのみ Claude scheduled-task に残す。

---

## 🚨 次セッション冒頭で必ず読むファイル（2026-05-01更新）

- **🔥 BayChat AI Reply cat02 完成・cat03 引継ぎ**: `services/baychat/ai/handoff_20260501_evening_cat02_complete.md`（iter1〜8自走改善で品質100%クリーン・GPT-5-Mini本番除外決定・補足情報UI/再生成APIサーバー実装済・cat03で APOLOGY トーン込みテスト着手予定）
- **🔥 eBay リサーチツール Ver.1.5 完成（社長厳指摘で全面刷新）**: `commerce/ebay/tools/research/handoff_20260501_v15.md`（Ver.1の中古混入・スニーカー偏重・赤字混入・売れる根拠ゼロを是正・5サイト並列+12カテゴリ+evidence score 7シグナル+赤字除外ゲート・社長判断待ちAPI 3件）
- **🔥 コンテンツ基盤整備 完了引継ぎ**: `.claude/handoff_20260429_content_infrastructure_complete.md`（業務縦軸構造に根本刷新完了・5/31ウェビナー骨子v0.1＋AIコースカリキュラムv0.1完成・残タスクは社長コミット4点＋判断待ち5点）
- **配信ダッシュボード**: `education/campers/content-projects/INDEX.md`（全体の取り出し窓口・最初に開く）
- **2軸戦略コンテンツ前提**: `memory/project_consulting.md` + `memory/feedback_content_audience_framing.md`（**BayChat は Campers のみ・Note/X 完全禁止**）
- **直近イベント**: 2026-05-31（日）Campersウェビナー（`memory/project_campers_webinar.md`）
- **竹案リファクタ T1-T15 全完了**（梅案`eef37ab`→竹案 `ea044c9`）。各部門 `index.md` → `.claude/rules/project-structure.md` の順で把握
- **新機能（4/24以降稼働中）**:
  - 隔週自動メンテ: `biweekly-claude-maintenance`（第1・第3月曜10時・肥大化監視＋Chatwork個人DM通知）
  - 半自動改善: `/隔週メンテナンス` スラッシュコマンド
  - memory3層統合: `memory/` → `.claude/memory_backup/` → GitHub（daily-github-backup 0:00自動同期）
  - Campers削除: Windowsタスク `CampersMemberRemoval`（Playwright版・毎日5:00・Chrome MCP不要）
  - 仕入管理表GAS: `commerce/ebay/tools/gas/shiire/` clasp管理（Monaco貼付け廃止）
- **BayChat AI Reply作業時**: `services/baychat/ai/handoff_20260423_cowatech_prd_sync.md` + `memory/feedback_baychat_ai_reply_stance.md`

---

*最終更新: 2026-05-01（BayChat AI Reply cat02 完成・iter1〜8自走改善で 100%クリーン・GPT-5-Mini本番除外決定・admin_prompt v2.3_baseline_natural3 確定・補足情報UI+再生成APIサーバー実装・cat03 引継ぎ済）*
