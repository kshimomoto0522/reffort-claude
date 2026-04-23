# Campersメンバー削除 自動化システム

## 全体構成

毎朝5:00に無人でCampersグループメンバーを削除するための多層防御システム。

```
┌─────────────────────────────────────────────────────────┐
│ Windowsタスクスケジューラ                                 │
│   CampersChromeRestart (4:50 AM 毎日)                   │
│   └─ chrome-restart-for-removal.bat を実行               │
│      └─ Chrome完全再起動 + セッション復元                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Claude Code スケジュールタスク                            │
│   campers-member-removal-goto (5:00 AM 毎日)            │
│   └─ removal-queue.json を読み込み                       │
│   └─ 対象者をChromeで削除処理（navigate失敗時は最大2回リトライ）│
│   └─ Chatwork DMに結果報告                               │
└─────────────────────────────────────────────────────────┘
```

## ファイル一覧

| ファイル | 役割 |
|---------|------|
| `chrome-restart-for-removal.bat` | Chrome完全再起動スクリプト（4:50実行） |
| `register-windows-task.bat` | Windowsタスクスケジューラ登録用（再登録が必要なときのみ使用） |
| `../removal-queue.json` | 削除対象者のキュー |

## 社長が必要な操作

### 通常運用時
- **メンバー削除を依頼するときだけ**：Claudeに「〇〇を△月△日で削除」と伝える → Claudeが`removal-queue.json`に追加 → あとは自動

### それ以外
- **何もしない**（全て自動化済み）

## トラブル時の確認コマンド

### Windowsタスクの状態確認
```powershell
schtasks /Query /TN CampersChromeRestart /V /FO LIST
```

### Windowsタスクの実行履歴確認
```powershell
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational'; ID=200,201} | Where-Object {$_.Message -like '*CampersChromeRestart*'} | Select-Object -First 5 TimeCreated, Message
```

### Chrome再起動のログ確認
```
education/campers/scripts/chrome-restart.log
```

### Windowsタスクの削除（必要時）
```powershell
schtasks /Delete /TN CampersChromeRestart /F
```

### Windowsタスクの再登録（削除後）
```powershell
schtasks /Create /TN "CampersChromeRestart" /TR "`"C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\education\campers\scripts\chrome-restart-for-removal.bat`"" /SC DAILY /ST 04:50 /F

Set-ScheduledTask -TaskName 'CampersChromeRestart' -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable)
```

## 前提条件

- Chromeの設定「前回開いていたページから続行」が**ON**であること
  - 確認URL: `chrome://settings/onStartup`
- PCが4:50〜5:30の間スリープ状態でないこと
- Claude Codeアプリが起動し続けていること（スケジュールタスク実行のため）

## 失敗時の動作

メインタスク（`campers-member-removal-goto`）は、Chrome操作が失敗した場合：
1. **削除を一切実行しない**（絶対厳守ルール）
2. **権限変更が途中なら元に戻す**
3. **社長のChatwork DM（room_id 426170119）に中断報告を送信**
4. キューの該当メンバーは`pending`のまま残り、翌朝再試行される

## 設計日

2026-04-15（2日連続の5時失敗を受けて多層防御を構築）
