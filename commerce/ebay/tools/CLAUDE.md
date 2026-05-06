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

## 開発優先順位（2026年5月6日午後更新）

| 優先度 | ツール | 状態 | 次のアクション |
|--------|--------|------|--------------|
| ✅ 稼働中 | **ASICSツール v8+補正版** | **本番稼働中（5/6 13:47ビルド・210秒待機）** | 1周完走後にBot検出頻度レビュー（210秒の妥当性判定） |
| ⏸ 中止 | **ASICS v9 並列ワーカー** | **コスト過大で中止** | コード残置（将来モバイルSIM案で再開可能・`memory/project_asics_parallel_v9.md`参照） |
| ⚠️ 改修待ち | **adidasツール（scrape_adidas_v1.py）** | 5/1 出品無しスキップ解除＆redirectリトライ済 | v8+補正の知見（identify_retry_targets改修・1047対応）を適用 |
| 🟢 NEW | **無在庫リサーチツール Ver.1**（`research/`） | **2026-04-30 完成・5/31デモ用** | 楽天/Yahoo APIキー登録＋Marketplace Insights API申請（社長判断） |
| 🟠 高 | HIROUNエクセル精査ツール | 未着手 | HIROUNのエクセル形式を確認してClaudeで試作 |
| 🟠 高 | 競合リサーチツール（eBay API版） | **無在庫リサーチに統合済み** | research/ で並行カバー |
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

## ASICSツール v8+補正版（2026-05-06 現行・本番稼働中）— 要点

- **方式**: Firefox/Selenium（visible・画面外配置）／PyInstaller 4.6 + Python 3.8.10／5/6 13:47ビルド
- **シート**: `【ASICS】在庫管理` / SPREADSHEET_KEY: `12SGD4RLze25JC6PWCFCOTxbk2qtL5UGp0D3B_mklK68`
- **待機時間**: 210秒（Akamai対策・5/6 240→210秒に短縮試行中）
- **1周**: 約35時間（605件×3.5分）→ 1時間休憩 → 自動ループ
- **5/6補正3点**: ①identify_retry_targets でURL空+ItemIDあり+未処理行を Mod E に追加 ②Policy違反を在庫状況/エラー情報に分離 ③EndItem ErrorCode 1047 を成功扱い
- **詳細仕様（機能Mod A-G・運用ルール・待機時間戻し条件・GAS連携）**: → [`asics_v8plus_spec.md`](asics_v8plus_spec.md)
- **タスクスケジューラ**: v8 は自動再起動するため**不要**（旧 ASICS_v2_*ji は無効化推奨）

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

## 無在庫リサーチツール Ver.1（`research/`）— 要点のみ

- **概要**: eBay Browse API で「日本セラーが米国向けに売っている商品」を取得 → 楽天/Yahoo!ショッピングで仕入候補を自動検索 → 全コスト（FVF・送料・関税・為替）込みの純利益を計算
- **完成日**: 2026-04-30（一晩構築・5/31 Campers ウェビナー実例デモ用）
- **使い方**: `python research/orchestrator.py --quick`（4 キーワード × 4 件・約 2 分） / `python research/orchestrator.py`（13 キーワード × 6 件・約 30 分）
- **コア構成**: ebay_app_token.py（client_credentials）/ ebay_browse.py / rakuten_search.py / yahoo_shopping.py / matcher.py / pricing.py / fx.py / orchestrator.py / report.py
- **2026 年版前提反映**: De Minimis $800 廃止 + Section 122 10% + スニーカー $150+ FVF 8%（StockX 対抗）+ EMS 米国向け停止
- **Ver.1 の限界**: SOLD データ × / 楽天/Yahoo は HTML スクレイピング暫定 / Amazon/メルカリ未対応
- **社長判断待ち**: 楽天 Application ID 登録（5 分・無料）/ Yahoo Client ID 登録（10 分・無料）/ eBay Marketplace Insights 申請（30 分＋数日待ち）
- **詳細**: `research/README.md` + `research/handoff_20260430_morning.md`

---

## 仕入管理表 GASツール（`gas/shiire/コード.js`）— 要点のみ

- **概要**: eBay Trading API（GetOrders）で新規オーダーを自動取得→仕入管理表に反映するGAS
- **トリガー**: 毎朝9:45頃・本番設定済み
- **APIキー**: Script Properties に保存（コード直書き禁止）
- **状態**: 2026-04-28 clasp移行完了（旧Monaco貼付け運用は廃止）
- **コード更新**: `cd gas/shiire/ && clasp push`（Chrome/Monaco不要）
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

*最終更新: 2026-05-06午後（v9並列化中止・v8+補正版本番投入・210秒試行中・1047対応反映）*
*ASICSツール: v8+補正版稼働中 / adidasツール: 稼働中 / 仕入管理表GASツール: 本番反映完了*
