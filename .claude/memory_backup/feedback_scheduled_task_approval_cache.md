---
name: スケジュールタスクはタスク単位の承認キャッシュを持つ
description: 新規/改修したスケジュールタスクは必ず「今すぐ実行(Run now)」で承認を焼き込んでから本番稼働させる
type: feedback
originSessionId: 21353565-1553-40c9-8bea-1310703a7bcb
---
スケジュールタスク（scheduled-tasks MCP）は、`settings.local.json` の allow list とは**別に、タスク単位で承認キャッシュを持つ**。

**Why:**
- 社長の「なぜか毎回再起動するたびに承認を煽られる」問題の真犯人。プロジェクト全体のallow list にあっても、自動起動したタスクはタスク独自の承認キャッシュを読む
- 2026-04-20 のスケジュールタスク大整理で判明。`update_scheduled_task` 実行時にシステムから "Tool approvals granted during a run are stored on the task and auto-applied to future runs. Recommend the user click 'Run now' first to pre-approve the tools it needs." と明示された

**How to apply:**
- 新規タスク作成・プロンプト大幅改修時は必ず「今すぐ実行(Run now)」ボタンを社長に1回押してもらい、そのとき承認したツールをタスクに焼き込む
- 特にMCP系（Chatwork・Slack・Claude_in_Chrome）を使うタスクは承認焼き込みが必須。これを怠ると無人実行時にタイムアウト→無限停止の原因になる
- allow list 追加だけで「承認問題は解決した」と宣言しない。タスクUIでの実行テストとセットで報告する
- 関連ドキュメント: feedback_task_activation.md（アクティベートテストの厳守）と同じ文脈だが、こちらは「承認キャッシュ」の存在を明示する点が追加情報
