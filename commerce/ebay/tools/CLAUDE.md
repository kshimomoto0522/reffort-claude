# eBayツール開発部門 — 部門ドキュメント

> 親ドキュメント: `/reffort/CLAUDE.md` を必ず先に読むこと。
> このフォルダでは「eBay輸出事業を支えるツールの開発・改善・新規構築」に特化して動く。
> **詳細ファイル一覧: `index.md` を参照。**

---

## この部門の目的

スタッフが手作業でやっている業務をツールで自動化し、最終的には「半分AI・半分スタッフ」の体制を実現する。

| ツール領域 | 概要 | 優先度 |
|-----------|------|--------|
| 在庫管理ツール（ASICS）| Firefox/Selenium版・稼働中 | ✅ 稼働中 |
| 在庫管理ツール（adidas）| Firefox/Selenium版・稼働中 | ✅ 稼働中 |
| 商品リサーチツール | 売れ筋・仕入れ候補の自動抽出 | 高 |
| 競合リサーチツール | ライバルセラーの出品・価格収集 | 高 |
| 価格調整ツール | 自動価格提案 | 中 |
| HIROUNエクセル精査ツール | 仕入候補リスト自動生成 | 中 |

---

## 開発優先順位（2026年3月21日更新）

| 優先度 | ツール | 状態 | 次のアクション |
|--------|--------|------|--------------|
| ⚠️ 改善中 | **ASICSツール** | **旧exe暫定稼働中 / v2.3待機** | v2の成功率改善・旧ツールとの差分分析 |
| ✅ 稼働中 | **adidasツール（scrape_adidas_v1.py）** | **テスト完了・タスク登録済み** | 商品追加に応じてモニタリング |
| 🟠 高 | HIROUNエクセル精査ツール | 未着手 | HIROUNのエクセル形式を確認してClaudeで試作 |
| 🟠 高 | 競合リサーチツール（eBay API版） | 未着手 | eBay Finding APIで試作 |
| 🟡 中 | 価格調整ツール（提案型） | 未着手 | 競合リサーチツール完成後 |
| 🟢 将来 | 出品補助ツール（AIタイトル生成） | 未着手 | BayChat AI Reply完成後 |

---

## 在庫管理ツール — ツールフォルダ

`C:\Users\KEISUKE SHIMOMOTO\Desktop\eBay在庫調整ツール（アシックス）\`

### ファイル一覧

| ファイル | 役割 | 対象 |
|---------|------|------|
| `scrape_data_v2.py` | メインツール（Firefox/Selenium版） | ASICS |
| `test_3rows.py` | 3件テスト用 | ASICS |
| `run_v2.bat` | タスクスケジューラ用（→ run_asics.ps1を呼ぶ） | ASICS |
| `scrape_adidas_v1.py` | メインツール（Firefox/Selenium版） | adidas |
| `test_adidas_3rows.py` | 3件テスト用 | adidas |
| `run_adidas.bat` | タスクスケジューラ用（→ run_adidas.ps1を呼ぶ） | adidas |
| `run_asics.ps1` | PowerShellランチャー（ツールフォルダ内） | ASICS |
| `run_adidas.ps1` | PowerShellランチャー（ツールフォルダ内） | adidas |
| `fix_status.py` | ステータスを「編集OK」に手動リセット | ASICS |
| `stop_tool.bat` | ツール手動停止 | 共通 |
| `config.xlsx` | APIキー・設定 | 共通 |
| `multivariations-8bd0cb82d2e1.json` | Google認証ファイル | 共通 |
| `geckodriver.exe` | Firefox用ドライバ | ASICS・adidas共通 |

### デスクトップのランチャーファイル（重要）

タスクスケジューラの日本語パス問題を回避するため、以下のps1ファイルをデスクトップに配置。
**これらは絶対に削除しないこと。**（詳細経緯: `development-history.md`）

| ファイル | 場所 | 役割 |
|---------|------|------|
| `run_asics.ps1` | `C:\Users\KEISUKE SHIMOMOTO\Desktop\` | ASICSツール起動（UTF-8 BOM） |
| `run_adidas.ps1` | `C:\Users\KEISUKE SHIMOMOTO\Desktop\` | adidasツール起動（UTF-8 BOM） |

---

## ASICSツール（稼働中）

### 仕様
- **方式**: Firefox/Selenium（ヘッドレス）。Scrapling版→Selenium版への移行経緯は `development-history.md` 参照
- **待機時間**: 240秒（固定）— 10〜20秒だとAkamaiにBot検出される
- **バッチ書き込み**: 15件ごとにスプレッドシートに途中保存（カウンター方式）
- **シート名**: `eBay在庫調整`（旧ツール互換のため元の名前に戻した）
- **SPREADSHEET_KEY**: `12SGD4RLze25JC6PWCFCOTxbk2qtL5UGp0D3B_mklK68`

### タスクスケジューラ（登録済み）
| タスク名 | 実行時刻 | 呼び出し先 |
|---------|---------|-----------|
| ASICS_v2_01ji | 毎日 01:00 | run_v2.bat → Desktop\run_asics.ps1 |
| ASICS_v2_09ji | 毎日 09:00 | run_v2.bat → Desktop\run_asics.ps1 |
| ASICS_v2_17ji | 毎日 17:00 | run_v2.bat → Desktop\run_asics.ps1 |

### スプレッドシート構造
- **行1**: ヘッダー行（旧ツール互換のためステータス行を撤廃）
- **行2以降**: データ
- ※ v2のA1ステータス書き込み機能は旧ツールのヘッダーを破壊するため注意

### 運用ルール
| 操作 | タイミング |
|------|----------|
| 行削除・途中挿入 | ツール停止中のみ（行番号ズレでデータ破損） |
| 一番下への追加 | いつでもOK |
| End商品の削除 | 行ごと削除（セルだけ消さない） |

### 旧ツール（exe）の現状（2026年3月30日更新）
- `scrape_data.exe` はPyInstaller製（Python 3.8）
- 起動不可だった根本原因はシート名リネーム。`'eBay在庫調整'` に戻して起動成功（2026/3/30）
- **現在**: 土日の暫定運用として旧exeで稼働中
- **注意**: config.xlsxのD-G列（eBay APIトークン）は旧exeも使用する。値を変更しないこと
- **次のステップ**: v2の成功率を改善し、旧exeから移行する（v2.3詳細は `development-history.md`）

---

## adidasツール（稼働中）

### 仕様
- **方式**: Selenium + Firefox（ヘッドレス）
  - adidas.jpはAkamai Bot Managerで強力に保護
  - Scraplingは完全ブロック → Firefoxなら突破できることを確認済み
  - ヘッドレス = 画面に表示されない（バックグラウンド動作）
- **待機時間**: 10〜15秒ランダム
- **シート名**: `【adidas】在庫管理`（同じスプレッドシートの別タブ）
- **現在の商品数**: 1件（テスト済み・正常動作確認）

### HTMLパース仕様
```
サイズ取得: soup.select('button[role="radio"]')
在庫判定: '現在ご購入いただけません。' が含まれていない → 在庫あり
```

### タスクスケジューラ（登録済み）
| タスク名 | 実行時刻 | 呼び出し先 |
|---------|---------|-----------|
| ASICS_adidas_01ji | 毎日 01:00 | run_adidas.bat → Desktop\run_adidas.ps1 |
| ASICS_adidas_09ji | 毎日 09:00 | run_adidas.bat → Desktop\run_adidas.ps1 |
| ASICS_adidas_17ji | 毎日 17:00 | run_adidas.bat → Desktop\run_adidas.ps1 |

---

## スクレイピング技術メモ

| サイト | 方式 | 結果 |
|--------|------|------|
| ASICS.com | Scrapling（HTTP） | ❌ 数件後に403（Bot検出） |
| ASICS.com | Selenium + Firefox | ✅ 安定動作 |
| adidas.jp | Scrapling（HTTP） | ❌ Akamaiブロック |
| adidas.jp | Selenium + Firefox | ✅ 突破可能 |

**結論**: 両サイトともFirefox/Seleniumが必要。Scraplingは使わない。

---

## SKU・在庫管理ルール（ASICS・adidas共通）

### Zフラグシステム
- 在庫あり: `S05288-25Z`（末尾にZ）
- 在庫なし: `S05288-25`（Zなし）
- 0→1更新時: 連番インクリメント（`S05288-25Z` → `S05288-26Z`）

### 在庫状況フォーマット
| 表示 | 意味 |
|------|------|
| `X/在Y` | サイト在庫X件 / eBay有在庫Y件 |
| `在庫切れ` | サイト・eBay両方ゼロ |
| `在庫処理停止` | 14日以上在庫切れ継続 |
| `出品無し` | eBayに出品なし |
| `End` | eBayリスティングが終了 |

---

## Claudeがスプレッドシートを直接読める

ツールと同じGoogle Sheets APIの認証情報を使えば、Claudeがスプレッドシートを直接読み取り可能。
スクリーンショットは不要。

```python
# 読み取りコード例
from scrape_data_v2 import SpreadsheetClass, read_config
_, _, KEY, _, _, _, _ = read_config()
ss = SpreadsheetClass(KEY)
ws = ss._get_worksheet('【ASICS】在庫管理')
rows = ws.get_all_values()
```

---

## 仕入管理表 GASツール（gas_shiire_tool.js）— 要点のみ

- **概要**: eBay Trading API（GetOrders）で新規オーダーを自動取得→仕入管理表に反映するGAS
- **トリガー**: 毎朝9:45頃・本番設定済み
- **APIキー**: Script Properties に保存（コード直書き禁止）
- **状態**: 2026-04-22 大改修後・本番反映完了
- **詳細仕様・本番/テスト環境ID・3層重複防御・コード更新手順**: `gas-shiire-tool-spec.md` 参照

---

## Claudeへの重要ルール（ツール開発部門専用）

- **スクレイピングは必ず対象サイトのrobots.txtを確認してから行うこと**
- **本番データへのアクセス・eBayへの自動操作は必ず社長確認を取ること**
- **ツール実行中にコードを変更してもOK**（Pythonはすでにメモリに読み込み済み、次回実行から反映）
- **繰り返しアクセスでIPブロックされないよう注意すること**
- eBay APIのレート制限に注意（特にTrading API）
- コードには日本語コメントを必ず入れること
- 提案は「今すぐClaudeで作れるもの」と「Cowatechに依頼が必要なもの」を分けて提示すること
- Access Denied ≠ IPブロック。ブラウザで開ければBot検出（詳細 `development-history.md` の教訓参照）

---

*最終更新: 2026-04-24（竹案T4実施 — 296→約180行圧縮・退避2ファイル作成・index.md新設）*
*ASICSツール: v2.3稼働中 / adidasツール: 稼働中 / 仕入管理表GASツール: 本番反映完了*
