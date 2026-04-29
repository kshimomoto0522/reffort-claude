---
name: .envファイルの作成・入力方法
description: APIキーや機密情報を扱うとき、Claudeがファイルを作成して社長が直接入力する手順を徹底する
type: feedback
originSessionId: 10516301-ff99-4e21-9ab6-27ba1ebade1e
---
APIキー・トークン等の機密情報を扱うときは、Claudeがテンプレートの.envファイルを作成し、社長がそのファイルを直接開いて入力する方式を徹底する。チャット上で「ここに入力してください」と案内するのではなく、ファイルを作って開かせる。

**Why:** 社長が「メモを開かせてわたしが保存するやり方を徹底してほしい」と明示的に指示した。

**How to apply:** .envや設定ファイルが必要なときは必ずWriteツールでテンプレートファイルを作成し、「このファイルを開いて入力してください」と案内する。チャット上での入力案内は禁止。

**機械化実装（2026-04-25）:** `.claude/hooks/file_auto_open.py`（PostToolUse / Write・Edit）で `.env` および `.env.*` を自動オープン。手動 `start ""` 不要。会話文脈から対象.envを特定するのはClaudeの責任（曖昧でないのに社長に聞くのは違反）。詳細 `.claude/rules/honesty_and_self_completion.md`。
