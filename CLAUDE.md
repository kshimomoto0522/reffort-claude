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
- **.env作業時3原則**：①会話文脈から対象.envを自動特定（曖昧でないのに社長に聞くのは違反・真に不明な時のみ確認）②Write/Edit直後にhookが自動オープン（`.claude/hooks/env_auto_open.py`）③「開きました」を必ず先に宣言してから次の作業へ

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

| タスクID | 内容 | スケジュール |
|----------|------|------------|
| `daily-github-backup` | reffort＋memoryフォルダをGitHubにバックアップ | 毎日深夜0時 |
| `monday-ebay-report-delivery` | eBay週次レポート配信 | 毎週月曜 10:00 |
| `daily-x-digest` | X情報ダイジェスト配信 | 毎日 9:40 |
| `biweekly-claude-maintenance` | Claude Code運用の肥大化監視＋最新情報取込＋改善提案 | 第1・第3月曜 10:00 |

新タスク追加時: ①作成 ②この表に追記 ③GitHubバックアップ。

---

## 🚨 次セッション冒頭で必ず読むファイル（2026-04-24 竹案完了）

- **竹案リファクタ T1-T15 全完了**（梅案`eef37ab`→竹案 `ea044c9`）。各部門 `index.md` → `.claude/rules/project-structure.md` の順で把握
- **新機能**:
  - 隔週自動メンテ: `biweekly-claude-maintenance`（第1・第3月曜10時・肥大化監視＋Chatwork個人DM通知）
  - 半自動改善: `/隔週メンテナンス` スラッシュコマンド（5層調査＋松竹梅＋社長判断→実行→結果再送信）
  - memory3層統合: `memory/` → `.claude/memory_backup/` → GitHub（daily-github-backup 0:00自動同期・スマホアプリ参照可）
  - 全作業蓄積: `education/campers/content-projects/claude-code-maintenance-case-study/session-logs/` にコンテンツ素材として蓄積（配信は社長判断）
- **BayChat AI Reply作業時**: `services/baychat/ai/handoff_20260423_cowatech_prd_sync.md` + `memory/feedback_baychat_ai_reply_stance.md`（社長判断待ち：進め方・共有方法・お礼Slack返信）

---

*最終更新: 2026-04-24（竹案T1-T15 全完了・Progressive Disclosure実装完成＋持続可能性4点セット完成）*
