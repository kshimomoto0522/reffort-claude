# Claude Code メンテナンスケーススタディ

> **本プロジェクトの目的**: 2026-04-23〜24に実施した「Claude Code運用の根本リファクタ（梅案＋竹案）」の全過程を、**Campers受講生向けコンテンツ素材として蓄積**する骨組みプロジェクト。
>
> ⚠️ **配信計画・記事公開・動画制作・チャネル別タイミング等は社長判断で別途実施**。本プロジェクトは「素材蓄積のみ」を目的とし、勝手に公開・配信しない（`memory/feedback_hp_publish_rule.md` / `memory/feedback_slack_rules.md` の精神準拠）。

---

## 本プロジェクトの構造

```
claude-code-maintenance-case-study/
  README.md                            ← 本ファイル（目的・方針）
  outline.md                           ← 7章構成の執筆骨子テンプレート
  session-logs/                        ← 各メンテサイクルのセッションログ
    2026-04-23_initial-diagnosis.md    ← 梅案セッション（3エージェント診断・8項目解毒）
    2026-04-24_take-plan-execution.md  ← 竹案セッション（Progressive Disclosure構造改善＋4点セット導入）
  assets/                              ← スクリーンショット・before/after図表
```

## 蓄積方針

1. **メンテサイクルの全記録を蓄積**:
   - 隔週メンテ(`biweekly-claude-maintenance`) + `/隔週メンテナンス` コマンド実行の全過程を `session-logs/YYYY-MM-DD.md` に保存
   - 調査結果（情報源URL）・松竹梅提案・社長判断・実装過程・学びを記録
2. **失敗も隠さない**:
   - エラー・指摘・軌道修正も生コンテンツとして残す
   - 受講生に「AIで運営する時にこういう課題が出る」を実地で伝えるため
3. **素材 ≠ 配信物**:
   - ここに溜まったものを**そのまま公開**することはない
   - 社長が記事・動画・スクール教材に落とし込む際に「ネタ帳」として活用

## 想定されるコンテンツ化シナリオ（社長判断で選択）

- **Note記事**: 「AIを使いこなすeBayセラーの現実 — Claude Codeが"バカ"になる問題と復活法」
- **YouTube動画**: 「AI運営の罠：コンテキスト肥大化とProgressive Disclosure」
- **X スレッド**: 診断プロセスの技術詳細
- **Campersスクール教材**: 「あなたのAI運営フォルダが肥大化していないかチェック」
- **書籍**: 「AIパートナー運営の実践書」（将来）

## 運用ルール

- 隔週メンテ実行後、`session-logs/YYYY-MM-DD.md` に追記（`/隔週メンテナンス` コマンド内で自動）
- 大きな判断（松竹梅の選択・逆提案）は必ず記録
- 失敗・エラー・指摘も生のまま残す
- 公開判断は社長のみ。Claude Codeからの「記事にしますか？」提案は禁止（本人負担増）

## 関連

- 持続可能性4点セット: `memory/feedback_claude_code_operation.md`
- 隔週メンテサイクル: `management/md-audit/biweekly_maintenance.py` + `.claude/commands/隔週メンテナンス.md`
- Campers全体: `education/campers/CLAUDE.md`
- コンテンツ記録原則: `memory/feedback_content_recording.md`
