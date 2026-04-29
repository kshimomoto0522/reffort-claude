---
name: Chrome操作の無人タスクはClaude経由を捨てる
description: Claude in Chrome MCP / Claude scheduled-task は無人実行で permission_required や per-task承認キャッシュ問題で失敗する。Chrome操作が必要なタスクはPlaywright + Windowsタスクスケジューラ直接起動の構成に固定する
type: feedback
originSessionId: 723d0162-a26f-4a70-85ec-18691aeb1a1d
---
# Chrome操作の無人タスクはClaude経由を捨てる

無人スケジュール実行で Chrome を必要とするタスクは、Claude Code を中継させない。Playwright を Python で直接叩き、起動は Windowsタスクスケジューラから直接行う。

**Why:**
- Claude in Chrome MCP は scheduled-task 内で `permissionMode="ask"` で動作し、`permissionStorage`（Always allowリスト）を参照しない仕様（Anthropic既知バグ Issue #30356, #47180）。「Always allow on this site」を登録しても無人実行では毎回 permission_required で落ちる。
- Claude scheduled-task 自体にも per-task 承認キャッシュがあり、プロンプト変更時にキャッシュが無効化されると再発火しなくなる事象が確認された（2026-04-28 Campers削除タスクで再現）。
- Run now で承認焼き込みも UI 側に「常に許可」が出ないことがあり完全には信頼できない（feedback_scheduled_tasks.md ルール3.5）。
- 結果：Chrome操作系タスクをClaude scheduled-task経由で動かすと、ある日突然動かなくなり、社長への通知すら来ないサイレント停止が起きる。

**How to apply:**
- Chrome操作（Chatwork UI操作・GAS Editor操作・WordPress管理画面操作 等）が必要な無人タスクは：
  1. **Playwright**（Python）で直接スクリプト化（Chrome MCP / Claude in Chrome は使わない）
  2. 認証は `storage_state` ベースのcookie永続化（初回だけ手動ログイン）
  3. 起動は **Windowsタスクスケジューラ → bat → python** の直接ルート
  4. Claude Code は中継しない
- 既存事例：`CampersMemberRemoval`（毎日5:00・`education/campers/scripts/run_campers_removal.bat`）
- 起動失敗時はbatラッパー側でフォールバックDM通知を仕込み、サイレント停止を防ぐ
- Claude scheduled-taskは「APIだけで完結する処理」「Bash/Python だけで完結する処理」に限定する

**派生指針:**
- 既存の Claude scheduled-task が permission_required や承認待ちで止まったら、まず「Chrome操作が必要か」を疑い、必要ならWindowsタスク化を検討する
- ~~新規タスク設計時は「Chrome操作が要るならWindowsタスク」「APIで完結するならClaude scheduled-task」の二択でルーティングする~~ ← **2026-04-29 改訂**：API完結タスクでもサイレント停止が発生（daily-x-digest 5日間途絶）。新ルーティングは `feedback_scheduled_tasks.md` ルール5 を参照（MCP必須＝Claude / API完結＝Windows）
