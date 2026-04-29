---
name: スケジュールタスク運用ルール（実行厳守・プロンプト同期・承認キャッシュ・チェックポイント）
description: スケジュールタスクの4本柱を統合。スキップ禁止・スクリプト変更時のプロンプト同期・Run nowで承認焼き込み・チェックポイント先行更新で無限停止防止
type: feedback
originSessionId: bf4ef38c-6c1e-4833-837a-9742e689af01
---
# スケジュールタスク運用ルール

関連: `feedback_task_activation.md`（アクティベートテストの厳守）

---

## ルール1: スケジュールタスク実行の厳守（スキップ禁止）

Campersメンバー削除タスクで重大なミスが発生。権限チェック（Chrome操作）がAPIでできなかったため「スキップ」して削除を実行した。結果、メンバーに「削除されました」通知が表示され、社長が最も避けたかった事態を招いた。

**Why:**
社長は「権限チェックをOFFにする → 削除 → ONに戻す」という手順を明示し、その理由（通知非表示のため）も説明していた。「イレギュラーが発生した場合は中断・報告」も明確に指示していた。にもかかわらずタスクはスキップして続行し、報告もしなかった。

**How to apply:**
- スケジュールタスクのプロンプトには「できない場合は中断」を各ステップに明記する
- 「APIでできないからスキップ」は絶対に許可しない
- 手順に必須条件がある場合（例: Chrome操作）はその条件が満たせない場合の中断フローを必ずプロンプトに書く
- タスクに「成功・中断どちらでも社長に報告する」を必ず含める
- スケジュールタスクは「その場にいる別のClaude」として動くため、口頭で伝えた指示はプロンプトに転記しなければ伝わらない

---

## ルール2: スクリプト変更時のプロンプト同期

スクリプトを変更したら、そのスクリプトを呼び出すスケジュールタスクのプロンプトも必ず確認・更新する。

**Why:** 2026-03-31にsend_weekly_report.pyとwrite_gsheets.pyを大幅更新したが、monday-ebay-report-deliveryのプロンプトは古いまま放置していた。社長に「更新されていたの？」と指摘されて初めて気づいた。

**How to apply:** セッション終了チェックリストの一環として、変更したスクリプトがスケジュールタスクから呼ばれていないか `list_scheduled_tasks` で確認し、該当があればプロンプトを最新化する。社長に聞かれる前に自発的にやること。

---

## ルール3: タスク単位の承認キャッシュ（Run now で焼き込み必須）

スケジュールタスク（scheduled-tasks MCP）は、`settings.local.json` の allow list とは**別に、タスク単位で承認キャッシュを持つ**。

**Why:**
- 社長の「なぜか毎回再起動するたびに承認を煽られる」問題の真犯人。プロジェクト全体のallow listにあっても、自動起動したタスクはタスク独自の承認キャッシュを読む
- 2026-04-20 のスケジュールタスク大整理で判明。`update_scheduled_task` 実行時にシステムから "Tool approvals granted during a run are stored on the task and auto-applied to future runs. Recommend the user click 'Run now' first to pre-approve the tools it needs." と明示された

**How to apply:**
- 新規タスク作成・プロンプト大幅改修時は必ず「今すぐ実行(Run now)」ボタンを社長に1回押してもらい、そのとき承認したツールをタスクに焼き込む
- 特にMCP系（Chatwork・Slack・Claude_in_Chrome）を使うタスクは承認焼き込みが必須。これを怠ると無人実行時にタイムアウト→無限停止の原因になる
- allow list 追加だけで「承認問題は解決した」と宣言しない。タスクUIでの実行テストとセットで報告する

---

## ルール3.5: Run now の「常に許可」が出ない現象（2026-04-24 観測）

Claude Code UI で Scheduled タスクの `Run now` ボタンを押した際、新規権限ダイアログでは **「一度だけ許可」のみ表示され、「Always allow（常に許可）」オプションが提供されない** ことがある（社長観測・他タスクでも同現象）。

**Why:**
- 2026-04-24 `biweekly-claude-maintenance` 初回 Run now 実施時に社長から報告
- 「常に許可」がUIに出ない結果、Run now 承認焼き込み（キャッシュ保存）ができない可能性
- システム全体の挙動で、Reffort側から直接は変更不可（Anthropic側UIの制約）

**How to apply:**
- 新規タスク作成時は、**タスク内で使う全コマンドを `settings.local.json` の allow にワイルドカードで事前登録**する（例: `Bash(py :*)` / `mcp__chatwork__*` / `Read(//c/Users/...)`）
- これにより初回自動実行時に権限プロンプトそのものが出ない状態を作る
- それでも万一プロンプトが出た場合は「一度だけ許可」を都度押す運用（タイムアウト・無人実行停止のリスクあり）
- 「Run nowで承認焼き込み済み＝安心」と決めつけない。**実運用の初回自動実行時に挙動確認**をセットで行う
- Anthropic側UI改善が進んだら本項は改訂

---

## ルール4: チェックポイント先行更新（差分検出タスクの無限停止防止）

ts・カーソル・cursor_token等で「前回の続き」から処理する定期タスクは、**差分検出ポイントを処理の前に先行更新する**こと。

**Why:**
- 2026-04-20に `baychat-slack-hourly-check` が2日間停止した直接原因
- 元の設計：履歴取得→処理→最後にtsファイル更新。処理中クラッシュでtsが未更新 → 次回起動時も同じメッセージで詰まる → 無限停止ループ
- 実装バグではなく、設計上の欠陥。どのts-based定期タスクでも再発し得る

**How to apply:**
- 履歴取得後、**差分処理より前に**最新tsをファイルに保存する
- 順序：①前回ts読込 → ②履歴取得 → ③最新tsを即ファイル保存 → ④差分処理 → ⑤異常終了時も社長DMに報告
- 処理が途中で失敗しても、次回起動時は新しいチェックポイントから進めるのでループ停止しない
- 1件の処理失敗で他の処理を巻き込まないよう、メッセージごとにtry/except的に扱う
- 異常終了時も必ず社長個人DM（room_id: 426170119）に箱型カードで失敗報告する（沈黙停止を防ぐ）
- 適用範囲：Slackの slack_last_checked.txt 型タスク、メール監視、API polling、RSSフィード監視など、すべての「前回から今回までの差分」を扱うタスク

---

## ルール5: API/Bash/Python完結タスクは Windows タスクスケジューラ直接起動を原則とする（2026-04-29 確立）

ルール3.5 の「常に許可」UI欠落＋per-task承認キャッシュ減衰の組み合わせにより、API完結タスクであっても Claude scheduled-task 経由は**ある日突然サイレント停止**する。`daily-x-digest` が4/25〜4/29の5日間連続で配信途絶した実害発生（lastRunAt は更新されていたが Chatwork DM への送信もエラー報告も来ない状態）。

**Why:**
- 旧 memory `feedback_chrome_mcp_unattended.md` は「Chrome操作はWindows、API完結はClaude scheduled-task」というルーティングを定義していたが、後者の信頼性が崩れた
- 真の分岐軸は「Chrome操作の有無」ではなく「Claudeセッション固有のMCP（chatwork/slack 等）が必須か」
- pure Python/Bash で完結するタスク（urllib + tweepy + anthropic SDK 等で外部API直接叩き）は Claude セッションを介在させる必然性がない
- Claude を介在させると承認キャッシュ・UI制約・セッションlock の3点で詰まる

**How to apply:**
- 新規タスク設計時の二択（**2026-04-29 さらに見直し**）：
  - **Claudeセッション固有のMCP（chatwork/slack/Claude判断）が必須 → Claude scheduled-task**（biweekly-claude-maintenance / 週1の monday-* 系）
  - **APIで完結（Claudeへの判断は anthropic SDK 経由でPythonから直接呼ぶ）→ Windows タスクスケジューラ直接起動**
- 4/29時点でWindows化済み: DailyXDigest / CampersMemberRemoval / **ChatworkAIReply（新）** / **BayChatSlackCheck（新・SLACK_BOT_TOKEN待ち）**
- スクリプト側に必ず try/except + Chatwork失敗DM を仕込む（サイレント停止を python 層で防ぐ）
- bat ラッパーは `logs/<task>_<timestamp>.log` 形式で全出力を保存
- 残候補（Windows化検討）: `daily-github-backup`, `monday-ebay-report-delivery`（週1なので延命中）
- Windows タスク登録方法：
  - 単一発火/日次の Daily Trigger は `Register-ScheduledTask -Trigger (New-ScheduledTaskTrigger -Daily -At ...)` でOK
  - **30分間隔等の繰り返しは PowerShell の RepetitionDuration バグを避けるため CIM で直接Repetitionプロパティを上書きする**：
    ```powershell
    $trigger = New-ScheduledTaskTrigger -Once -At <初回時刻>
    $trigger.Repetition = New-CimInstance -ClientOnly -Namespace 'Root/Microsoft/Windows/TaskScheduler' -ClassName 'MSFT_TaskRepetitionPattern' -Property @{ Interval = 'PT30M' }
    ```
- 共通設定：`StartWhenAvailable=True / DontStopIfGoingOnBatteries=True / MultipleInstances=IgnoreNew / AllowStartIfOnBatteries=True`（CampersMemberRemoval / DailyXDigest / ChatworkAIReply / BayChatSlackCheck 共通）
- Slack を直接 API 叩く場合は MCP の OAuth トークンは取れないため、**Slack App を別途作成してBot Token (xoxb-...)を発行**する必要あり（社長作業・10分・SLACK_BOT_SETUP.md にガイド完備）

---

## ルール6: 高頻度タスクほど Claude scheduled-task で詰まりやすい（2026-04-29 観測）

`chatwork-ai-reply`（10分ごと・平日10〜20時）と `baychat-slack-hourly-check`（毎時05分）は4/28夜にサイレント停止していた一方、週1の `monday-*` 系や `biweekly-claude-maintenance` は生存。**起動回数が多いほど承認キャッシュ消耗→詰まる**規則性を確認。

**How to apply:**
- 新規タスクで頻度が「1日1回より多い」場合は最初から Windows タスクスケジューラを選ぶ
- 既存タスクで頻度が高いものを延命させる必要があれば、Run nowで承認焼き直しを月1回以上ルーティン化（ただしUIに「常に許可」が出ないので根本解決にならない）
