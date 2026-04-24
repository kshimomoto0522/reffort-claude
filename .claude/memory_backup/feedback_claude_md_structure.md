---
name: CLAUDE.md構造最適化ルール
description: CLAUDE.mdは100行以下のコアルールのみ。参照情報は.claude/rules/に分離。今後も徹底
type: feedback
---

CLAUDE.mdは毎セッション必読のコアルール（約100行以下）のみに絞る。参照情報は`.claude/rules/`に分離する。

**Why:** CLAUDE.mdが長すぎるとClaudeが指示を読み飛ばすリスクが上がる。短いほど重要ルールの遵守率が高い。情報は捨てるのではなく「引き出しを分ける」。

**How to apply:**
- 新しい情報を追加するとき、CLAUDE.mdに直接書くのではなく、適切な.claude/rules/ファイルまたは部門CLAUDE.mdに配置する
- CLAUDE.mdに残すのは：社長について、重要ルール、セッション終了チェックリスト、回答スタイル、自動タスク管理ルールのみ
- 事業詳細は各部門CLAUDE.mdに、会社概要・用語集・ロードマップ等は.claude/rules/に
- 2026年4月3日に382行→102行に最適化済み。バックアップ: CLAUDE.md.backup_20260403
