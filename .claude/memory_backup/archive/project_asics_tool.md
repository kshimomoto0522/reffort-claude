---
name: eBay在庫調整ツール（ASICS・adidas・全メーカー共通）プロジェクト
description: ASICS・adidasのeBay在庫管理ツールの開発状況・設計情報・監視体制・処理速度課題
type: project
---

## フォルダ
`C:\Users\KEISUKE SHIMOMOTO\Desktop\eBay在庫調整ツール（アシックス）\`

## スプレッドシート情報
- SPREADSHEET_KEY: `12SGD4RLze25JC6PWCFCOTxbk2qtL5UGp0D3B_mklK68`
- 認証ファイル: `multivariations-8bd0cb82d2e1.json`
- 列構成: A=ItemID, B=自社SKU, C=タイトル, D=仕入先URL①, N=在庫状況, Q=仕入れフラグ, R=エラー情報, S=更新日時
- **行構成**: 行1=ヘッダー, 行2以降=データ（旧ツール互換のためステータス行撤廃）
- **シート名**: `eBay在庫調整`（旧exeがハードコードしているため変更禁止）
- **Claudeがスプレッドシートを直接読める**（同じGoogle Sheets API認証を使用）

## スプレッドシート運用ルール
- **シート名変更禁止**: 旧exe（scrape_data.exe）が `'eBay在庫調整'` をハードコード
- **削除・途中挿入**: ツール停止中のみ（行番号がズレてデータ破損の原因になる）
- **一番下への追加**: いつでもOK（ツール実行中でも可）
- **End商品の削除**: 行ごと削除（セルだけ消すとズレる）

---

## ASICSツール — 現在の運用体制（2026-03-30更新）

### 旧ツール（scrape_data.exe）— 暫定稼働中
- PyInstaller製（Python 3.8）、修正不可
- Firefox/Selenium（ヘッドレス）+ 240秒間隔
- シート名 `'eBay在庫調整'` をハードコード → シート名変更で起動不可になっていた（3/30解決）
- **config.xlsxのD-G列（eBay APIトークン）も旧exeが使用。値を変更しないこと**
- 社長がデスクトップでダブルクリックで手動起動

### v2.3（scrape_data_v2.py）— 待機中
- Firefox/Selenium（ヘッドレス）版
- Access Denied処理を旧ツール準拠にシンプル化済み
- タスクスケジューラは現在無効化（旧ツール手動運用中）
- シート名参照を `'eBay在庫調整'` に修正済み

### v2.3仕様
- 待機: configのdelay値（240秒）±20%ランダム
- バッチ書き込み: 15件ごと（カウンター方式）
- ロックファイル: `asics.lock`（同時実行防止、2時間で自動解除）
- 5.5時間制限（MAX_RUNTIME_SECONDS）
- Access Denied時: Firefox再起動しない。30-60秒待機リトライ（最大3回）
- 連続失敗時: 5件連続で3分クールダウン（Firefox再起動なし）
- 累計失敗制限: なし（時間制限まで続行）

### タスクスケジューラ（現在無効化）
- `ASICS_v2_01ji` → 毎日 01:00
- `ASICS_v2_09ji` → 毎日 09:00
- `ASICS_v2_17ji` → 毎日 17:00

### 日本語パス問題（解決済み）
- bat → Desktop\run_asics.ps1（UTF-8 BOM）→ PowerShellが日本語パスを正しく処理
- **Desktop上のps1ファイルは絶対に削除しないこと**

---

## adidasツール（Firefox/Selenium版）

### ファイル
- `scrape_adidas_v1.py` - メインツール
- `test_adidas_3rows.py` - 3件テスト用
- `run_adidas.bat` → `Desktop\run_adidas.ps1` を呼ぶ

### 仕様
- Selenium + Firefox（ヘッドレス）でadidas.jpにアクセス
- 待機: 10〜15秒ランダム
- ロックファイル: `adidas.lock`（同時実行防止、2時間で自動解除）
- シート名: `【adidas】在庫管理`
- 現在の登録商品数: 1件

### タスクスケジューラ（登録済み）
- `ASICS_adidas_01ji` → 毎日 01:00
- `ASICS_adidas_09ji` → 毎日 09:00
- `ASICS_adidas_17ji` → 毎日 17:00

---

## 自動監視スクリプト

### ファイル
- `monitor_tools.py` — メイン監視スクリプト（シート名修正済み）
- `run_monitor.bat` → `Desktop\run_monitor.ps1` を呼ぶ

### タスクスケジューラ（登録済み）
- `Monitor_inventory_09ji` → 毎日 09:00
- `Monitor_inventory_12ji` → 毎日 12:00
- `Monitor_inventory_18ji` → 毎日 18:00

### 通知先
- 現在: 社長個人Chatwork DM（room_id: 426170119）

---

## 技術メモ

### Bot検出の教訓（重要）
- ASICSのCDN（Akamai）はIP単位でレート制限をかける
- 10-20秒間隔 → 30件程度でブロック
- 240秒間隔でもAccess Deniedは発生する
- **configのdelay値は絶対に無視しないこと**

### Claudeがスプレッドシートを読む方法
```python
import gspread
sa = gspread.service_account(filename='multivariations-8bd0cb82d2e1.json')
sh = sa.open_by_key('12SGD4RLze25JC6PWCFCOTxbk2qtL5UGp0D3B_mklK68')
ws = sh.worksheet('eBay在庫調整')
rows = ws.get_all_values()
```

### ⚠️ 環境変更時の注意（3/30の教訓）
- **シート名変更禁止**: 旧exeがハードコードしている
- **config.xlsx変更注意**: D-G列のAPIトークンは旧exeも使用する
- **行1のステータス行禁止**: 旧exeはヘッダーが行1にある前提で動作する
- v2で環境を変更したら、必ず旧exeでも動作確認すること
