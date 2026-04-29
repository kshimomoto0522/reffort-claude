# Campersメンバー削除 自動化システム（Playwright版）

## 全体構成（2026-04-28以降）

毎朝5:00に無人でCampersグループメンバーを削除するシステム。
**Chrome MCPやClaude in Chrome MCPは使わず、Playwrightで直接Chatwork UIを操作**する。
これにより Anthropic 側の "permission_required" 問題（GitHub Issue #30356/#47180）を完全回避。

**起動経路は Windowsタスクスケジューラ → bat → python**。Claude Code を中継しないため、per-task承認キャッシュ問題からも自由。

```
┌─────────────────────────────────────────────────────────┐
│ Windowsタスクスケジューラ                                 │
│   CampersMemberRemoval (5:00 AM 毎日)                   │
│   └─ run_campers_removal.bat 実行                        │
│      └─ python campers_member_removal.py                 │
│         ├─ removal-queue.json から本日処理対象を抽出     │
│         ├─ 各対象について Playwright で：                │
│         │   1. 部屋を開く                                │
│         │   2. 設定ダイアログ → 権限タブ                 │
│         │   3. 2つの権限トグルをOFF → 保存              │
│         │   4. Chatwork API でメンバー削除               │
│         │   5. 権限トグルを再びON → 保存                │
│         ├─ 全体連絡チャットは権限変更なしでAPI削除のみ    │
│         ├─ removal-queue.json を completed に更新        │
│         └─ 社長DM(426170119)に箱型カード報告             │
│      └─ Pythonクラッシュ時のみ _fallback_notify.py で警告│
└─────────────────────────────────────────────────────────┘
```

## トリガー再登録（必要時のみ）

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\education\campers\scripts\register-removal-task.ps1"
```

## 即時テスト

```powershell
Start-ScheduledTask -TaskName 'CampersMemberRemoval'
```

`logs/removal_<timestamp>.log` に出力が残る。社長DMにも完了報告が届く。

## ファイル一覧

| ファイル | 役割 |
|---------|------|
| `campers_member_removal.py` | **メイン削除スクリプト**（Playwrightで権限OFF→API削除→ON） |
| `run_campers_removal.bat` | **Windowsタスクから起動されるラッパー**（python起動・ログ出力・失敗時通知） |
| `_fallback_notify.py` | Pythonクラッシュ時のみ呼ばれるフォールバックDM通知 |
| `register-removal-task.ps1` | Windowsタスク CampersMemberRemoval 登録/再登録 |
| `setup_chatwork_auth.py` | 初回ログイン用ヘルパ。手動でChatworkにログイン→cookieを保存 |
| `inspect_chatwork_selectors.py` | UIセレクタ調査用（Chatwork UI改変時の再調査用） |
| `1_setup_auth.bat` | setup_chatwork_auth.py を起動するバッチ（社長操作用） |
| `.chatwork_auth.json` | Playwright用ログイン状態（gitignored・機密） |
| `logs/removal_*.log` | 各実行のstdout/stderr（gitignored） |
| `_run_*.json` | スクリプトが詳細実行ログを残す（gitignored） |
| `../removal-queue.json` | 削除対象者のキュー |

## 社長が必要な操作

### 通常運用時

**メンバー削除を依頼するときだけ**：Claudeに「〇〇を△月△日で削除」と伝える。
Claude が `removal-queue.json` に追加 → 該当日の朝5:00に自動削除 → DM報告。

### Chatworkセッション切れ時のみ

スクリプトが「ログイン切れ」を検知すると DM で通知される。
そのとき社長が `1_setup_auth.bat` をダブルクリック → ブラウザでログイン → Enter押下、で再ログイン。
通常Chatworkのセッションは数週間〜数ヶ月持続するので、頻繁に必要にはならないはず。

## ドライランで検証

```bash
cd "C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\education\campers\scripts"
python campers_member_removal.py --dry-run
```

権限OFF→ON動作だけ実機で確認し、API削除はスキップ。

## トラブルシュート

### 「ログイン切れ」DMが届いた

```bash
python setup_chatwork_auth.py
```
を実行 → ブラウザでログイン → Enter → 完了。

### Chatwork UIが大きく変わってトグルが見つからない

セレクタ再調査：
```bash
python inspect_chatwork_selectors.py
```
出力されるHTMLとスクリーンショットからセレクタを特定し、`campers_member_removal.py` の以下を更新：
- 設定ボタン: `[data-testid="room-header_room-settings-button"]`
- メニュー項目: `[data-testid="room-header_room-settings_room-settings-menu"]`
- 権限タブ: `button:has-text("権限")`
- 保存ボタン: `[data-testid="room-setting-dialog_save-button"]`
- トグルラベル: 「チャットの参加者一覧を表示する」「メッセージ送信を許可する」

### Playwrightブラウザバイナリが消えた

```bash
python -m playwright install chromium
```

## 失敗時の動作（絶対厳守ルール・スクリプト内に実装済み）

メインスクリプト `campers_member_removal.py` は、いずれかの工程が失敗した場合：
1. **削除を一切実行しない**（権限OFFが完全に成功するまで削除しない）
2. **権限変更が途中なら元に戻す**（OFF→失敗時のON復元）
3. **対象者以外を絶対削除しない**（admin/member/readonly再送信時の除外ID集合に対象だけ含める）
4. **adminが0人になる削除を拒否**（安全装置で例外送出）
5. **社長のChatwork DM（room_id 426170119）に中断/完了報告を送信**
6. **キューの該当メンバーは pending のまま残し、翌朝再試行**

## 設計変遷

- 2026-04-15：Claude in Chrome MCP + Windows タスクスケジューラ多層防御で初版構築
- 2026-04-28：Anthropic 側の `permission_required` バグ（#30356/#47180）顕在化
  - Claude scheduled-task から Chrome MCP の navigate が permission_required で失敗
  - **Playwright直叩きへ全面移行**でAnthropic依存を排除
  - 当初はClaude scheduled-task経由でPython起動を試みたが、per-task承認キャッシュ問題（feedback_scheduled_tasks.md ルール3.5）で再発火しないケースが発生
  - **最終的にWindowsタスクスケジューラ → bat → python の直接ルートに変更**してClaude Code中継層を完全排除
  - 旧Windowsタスク `CampersChromeRestart` (4:50 AM) は削除済み（Chrome起動不要のため）
