# eBay 週次レポート仕様・Chatwork連携

> 親: `commerce/ebay/analytics/CLAUDE.md` から「必要時ロード」として参照される詳細ファイル。
> `create_weekly_report_v3.py` / `write_gsheets.py` / `send_weekly_report.py` を改修する時・Chatwork送信処理を触る時に参照。

---

## Chatwork連携設定

| 項目 | 内容 |
|------|------|
| 送信アカウント | REFFORT AI（keishimomoto0522@gmail.com） |
| APIトークン保存場所 | **`.env` 経由で環境変数 `CHATWORK_TOKEN` を参照（コード直書き厳禁・`feedback_security.md`準拠）** |
| 送信先ルーム | 【AI】eBay運営（room_id: **426169912**） |
| 送信方法 | `curl` または Chatwork MCP経由 |
| 設定日 | 2026年3月16日 |

### Chatworkへのメッセージ送信コマンド（テンプレート）

```bash
python -c "
import os, urllib.request, urllib.parse
token = os.environ.get('CHATWORK_TOKEN')  # .env から読み込み（コード直書き厳禁）
room_id = '426169912'
msg = '【メッセージ内容】'
data = urllib.parse.urlencode({'body': msg}).encode()
req = urllib.request.Request(f'https://api.chatwork.com/v2/rooms/{room_id}/messages', data=data, method='POST')
req.add_header('X-ChatWorkToken', token)
with urllib.request.urlopen(req) as res:
    print('送信完了:', res.read().decode())
"
```

### 主要Chatworkルーム一覧

| ルーム名 | room_id | 用途 |
|---------|---------|------|
| 【AI】eBay運営 | 426169912 | AI通達・週次レポート（メイン） |
| ebay業務連絡 | 271411089 | スタッフ日常業務連絡 |
| 【KeiS】発送 | 289258037 | 発送業務 |
| 【KeiS】スニーカー | 319685466 | スニーカー商品関連 |
| 【Reffort】業務連絡 | 395343446 | 全社業務連絡 |

---

## 週次レポート分析スクリプト

| ファイル | 場所 | 役割 | バージョン |
|---------|------|------|-----------|
| `analyze_ads.py` | ebay-analytics/ | 広告レポート単体分析 | 旧 |
| `analyze_traffic.py` | ebay-analytics/ | Traffic×広告統合分析・result_traffic.txt出力 | 旧 |
| `create_weekly_report.py` | ebay-analytics/ | Excelレポート初版（5シート） | 旧 |
| `create_weekly_report_v2.py` | ebay-analytics/ | Excelレポート改訂版（7シート） | 旧 |
| **`create_weekly_report_v3.py`** | ebay-analytics/ | **Excel＋Google Sheets レポート最新版（12シート）** | **現行** |
| **`write_gsheets.py`** | ebay-analytics/ | **Google Sheets直接書き込みモジュール（v3から呼び出し）** | **現行** |
| **`send_weekly_report.py`** | ebay-analytics/ | **Chatworkへの自動配信（Excel＋Googleスプレッドシートリンク＋前週比コメント）** | **現行** |
| `weekly_history.json` | ebay-analytics/ | **週次履歴データ（前週比較の元データ・価格/在庫含む）絶対に削除しないこと** | 自動生成 |
| `weekly_notes.json` | ebay-analytics/ | **備考永続化ファイル（スタッフの書き込みを次週に引き継ぐ）** | 自動生成 |
| `reffort-sheets-*.json` | ebay-analytics/ | **Google Sheetsサービスアカウントキー（.gitignoreで除外）** | 秘密 |

---

## Google Sheets 連携設定

| 項目 | 内容 |
|------|------|
| スプレッドシート | eBay週次レポート_v3 |
| URL | https://docs.google.com/spreadsheets/d/1AT4x_qyohYiEs08RSHs5uFgqBAm51IRsY1ajybsJe0s |
| SPREADSHEET_ID | `1AT4x_qyohYiEs08RSHs5uFgqBAm51IRsY1ajybsJe0s` |
| サービスアカウント | reffort-claude@reffort-sheets.iam.gserviceaccount.com |
| プロジェクト | reffort-sheets（Google Cloud Console） |
| 認証方式 | サービスアカウントJSON鍵ファイル |
| 出力形式 | Excel（openpyxl）＋ Google Sheets（gspread）の両方を毎回出力 |

---

## 週次レポートの配信フロー（自動化済み）

**スケジュールタスク `monday-ebay-report-delivery` が毎週月曜10:00に自動実行:**

1. `create_weekly_report_v3.py` が実行される
   - GetOrders APIで最新トランザクション取得（CSVダウンロード不要）
   - WEEKS自動計算（月〜日の4週間）
   - Traffic Report・Ads Report CSVは手動ダウンロードが必要（APIなし）
   - Excel版を生成（openpyxl）
   - **Google Sheets版を直接書き込み（write_gsheets.py / gspread）**
2. `send_weekly_report.py` がExcelをChatwork【AI】eBay運営グループにアップロード
   - 挨拶＋前週比コメント（受注数・売上・CVR）付き
   - **Googleスプレッドシートリンクも配信メッセージに含む**

### 手動でレポートを再生成する場合

1. Traffic Report・Ads Report CSVをダウンロードして`create_weekly_report_v3.py`の先頭パスを更新
2. `py create_weekly_report_v3.py` を実行
3. テスト送信: `send_weekly_report.py` の `TEST_MODE = True` にして社長DM宛確認

---

## レポート構成（v3・12シート・Google Sheets対応）

| シート | 内容 | 主な目的 |
|--------|------|---------|
| 💬 AI総評 | 具体的商品名入りの要因分析・サイト別動向・今週やるべきこと | 全体方針・スタッフ共有 |
| 📊 サマリー | KPIブロック・週別サイト別売上（US/UK/EU/AU/CA）・売上ゼロ比率・収支サマリー | 全体把握・経営判断 |
| 🔥 コア売れ筋TOP15 | W4販売数ランキング・前週比Δ・CVR・PV・インプ・価格・PLP経由✅ | 在庫確保・広告強化 |
| 🚨 コア落ち | W3→W4でTOP15から外れた商品・価格・原因自動推測 | 異常検知・即対応 |
| ⭐ 準売れ筋 | sold>0・TOP15外・ポテンシャルスコア順・価格・備考 | 伸びしろ候補の育成 |
| 🌱 育成候補 | PV50以上・売上ゼロ・TOP20・価格・備考 | 購入障壁の発見・改善 |
| ⚠️ 要調査 | インプ500以上・売上ゼロ・掲載90日以上・価格・備考 | 在庫ツールバグ・仕入先URL切れの特定 |
| 🗑 削除候補 | L1:即削除 / L2:要確認・価格・削除判定（自動）・備考 | 断捨離・整理 |
| 🔥 コア売れ筋（月間） | 4週間合計のTOP15・価格 | 月間トレンド確認 |
| 🗑 削除候補（月間） | 4週間売上ゼロ・掲載90日以上・価格 | 確実な死蔵の特定 |
| 📈 改善追跡 | 前週「要調査・削除候補」→今週sold>0の改善成功商品・前週/今週の価格・在庫・PV・インプ比較 | スタッフのモチベーション |
| 📋 週次履歴 | weekly_history.jsonから自動蓄積 | 前週比較の基礎データ |

---

## v3の主な機能（2026/3/31更新）

- **💬 AI総評シート**：具体的商品名（【SKU】タイトル形式）で伸び・落ち・コア落ち原因を分析。「今週やるべきこと」を提示
- **通貨ベースサイト分類**：USD=US, GBP=UK, EUR=EU, AUD=Australia, CAD=Canada（TransactionSiteIDではなく通貨で判定）
- **サイト別売上をサマリーに統合**：【US】【UK】【EU】【AU】【CA】の注文数・売上を交互色で一覧表示
- **売上ゼロ比率（週次KPI）**：W1-W4ごとに売上ゼロSKU比率を表示（減少=改善）
- **前週カテゴリ正確化**：HISTORY_DATE_KEYをW4終了日（日曜）に変更。同一週の複数実行で上書き。6日以上前のデータのみ前週として参照
- **コア落ちシートに前週/今週カテゴリ2列**：カテゴリ変遷が一目でわかる
- **PLP経由列**：コア売れ筋にPLP広告経由の売上があれば✅表示
- **前週比表示を「110%/90%」形式に統一**（▲▼記号廃止）
- **Δ販売数は+3/-2形式**（記号なしの直感的表示）
- **Sell Analytics API（OAuth 2.0）完全対応**：Traffic CSV不要。日別・週別・商品別データを自動取得
- **CVR単位自動変換**：API（ratio 0.001）→ 表示（% 0.1%）を正しく変換
- **在庫数・掲載日数をseller_cacheから取得**：GetMyeBaySelling APIでQuantityAvailable/StartTimeを取得
- **全カウントSKUベース**：バリエーション数ではなくユニークSKU数を商品数として使用
- **weekly_history.json**：W4終了日をキーとして自動保存。テスト実行のゴミが溜まらない設計
- **GetOrders APIでトランザクション自動取得**：FVFはAPIから正確取得、International/PLG/Offsiteは売上比率推定
- **WEEKS自動計算**：今日基準で直近4週（月〜日）を自動生成
- **Chatwork自動配信**（`send_weekly_report.py`）：挨拶＋前週比コメント＋Excelアップロード＋Googleスプレッドシートリンク
- **Google Sheets直接書き込み**（`write_gsheets.py`）：gspread経由で全12シートをスプレッドシートに直接出力
- **2段ヘッダー**：3行目にカテゴリ（販売数・PV等）、4行目に詳細（W3・W4・Δ）。6シート対象
- **全シートに価格列**：seller_cacheから現在価格を取得。改善追跡では前週価格・前週在庫も表示
- **備考永続化**：weekly_notes.json ＋ スプレッドシートの備考セルから読み取り→次週に引き継ぎ
- **Item IDハイパーリンク**：全データシートのItem IDクリックでeBay出品ページに直接遷移
- **終了済み商品フィルター**：seller_cache不在 or 在庫0＆トラフィック0の商品を除外
- **CVR再計算**：Traffic API TOP200制限でCVR=0の商品をsold/pvから再計算
- **総出品数の週別表示**：weekly_history.jsonから各週末時点の値を参照（蓄積で精度向上）

---

## 商品分類の定義

| 分類 | 基準 | アクション |
|------|------|-----------|
| 🔥 コア売れ筋 | 販売数TOP15 | 在庫確保・広告維持 |
| ⭐ 準売れ筋 | sold>0・TOP15外 | 価格微調整でコア化を狙う |
| 🌱 育成候補 | sold=0・PV>=20 | 価格・タイトル・競合調査 |
| ⚠️ 要調査 | sold=0・imps>=500・掲載90日以上 | 在庫ツール確認・仕入先URL確認 |
| 🗑 削除L1（即削除） | imps=0・PV=0・sold=0 | eBayでウォッチ・累計販売数確認後に取り下げ |
| 🗑 削除L2（要確認） | imps<50・PV<5・sold=0・掲載180日以上 | 同上 |

### 削除判断の重要ルール

**削除候補シートのAPI自動判定を参考に最終確認すること：**

- **✅ 削除OK**：ウォッチ数10以下 & 生涯販売数0 → 削除推奨
- **⚠️ 要確認**：ウォッチ数11〜50 または 生涯販売数1以上 → 慎重に判断
- **🚫 削除NG**：ウォッチ数50超 または 生涯販売数4以上 → 削除禁止
- これらはGetMyeBaySelling APIで自動取得済み（Traffic CSVには含まれない情報）

---

## Traffic Report CSVの列構成（重要・パース参考）

- 0: Listing title / 1: eBay item ID / 2: Item Start Date / 3: Category
- 4: Current promoted listings status / 5: Quantity available
- 6: Total impressions / 7: CTR / 8: Quantity sold
- 9: % Top 20 Search Impressions / 10: CVR
- 21: Total Promoted Listings impressions（eBayサイト）
- 22: Total Promoted Offsite impressions（eBay外）
- 23: Total organic impressions on eBay site
- 24: Total page views
- ヘッダー行はindex=5（先頭5行がメタ情報）

## Transaction Report CSVの列構成（重要・パース参考）

- ヘッダー行はindex=11（先頭11行がメタ情報）
- 0: Transaction creation date（"Mar 15, 2026"形式）/ 1: Type
- 10: Net amount / 11: Payout currency / 17: Item ID / 21: Quantity
- 22: Item subtotal / 26: Final Value Fee - fixed / 27: Final Value Fee - variable
- 31: International fee / 34: Gross transaction amount / 35: Transaction currency / 38: Description
- **除外ルール**: Transaction currency = USD のみ集計(ebaymag = AUD/GBP/EUR/CAD)
- PLG費用: Type="Other fee", Description="Promoted Listings - General fee"
- Offsite費用: Type="Other fee", Description="Promoted Offsite fee"
- PLP費用: **Transaction Reportに含まれない** → 手入力（`PLP_FEE_TOTAL` 変数に設定）

---

## 分析で判明した重要な知識

- **Transaction Reportの除外ルール**: `Transaction currency = USD` のみ使用（ebaymag除外）
- **FVF率**: $150以上〜約8-9%、$150未満〜15-20%（eBay標準）
- **PLP費用**: Transaction Reportに**含まれない**（Seller Hub広告管理画面で別途確認し手入力）
- **Offsite費用**: Transaction Reportの「Promoted Offsite fee」に記載（クリック課金・CPC）
- **PLG**: 成果報酬型（売れた時のみ課金・CPS）
- **要調査1831件問題**: 全出品2856件の64%がインプあり売上ゼロ → 在庫ツールのバグが広範囲に影響している可能性が非常に高い。Cowatechへの修正依頼が最優先。
