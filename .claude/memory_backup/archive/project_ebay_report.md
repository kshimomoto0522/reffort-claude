---
name: eBay週次レポートv3の現状
description: 週次レポートv3の完成状態・Google Sheets対応済み・12シート・2段ヘッダー・月曜自動配信
type: project
---

## 週次レポートv3（2026/3/31更新）

**スクリプト**: `commerce/ebay/analytics/create_weekly_report_v3.py`
**Google Sheets出力**: `commerce/ebay/analytics/write_gsheets.py`（gspread経由）
**配信スクリプト**: `commerce/ebay/analytics/send_weekly_report.py`
**OAuth管理**: `commerce/ebay/analytics/ebay_oauth.py`
**現行シート数**: 12シート

### 完成済み機能（主要）
- **Google Sheets直接書き込み完成**（2026/3/31）：Excel＋Google Sheetsの両方を毎回出力
- **2段ヘッダー**：3行目にカテゴリ（販売数・PV等）、4行目に詳細（W3・W4・Δ）。6シート対象
- **全シートに価格列**：seller_cacheから現在価格を取得
- **改善追跡に前週価格・前週在庫**：価格/在庫変更が改善に寄与したか確認可能
- **総出品数の週別表示**：weekly_history.jsonから各週末時点の値を正確に参照
- **備考永続化**：weekly_notes.json ＋ スプレッドシートセルから読み取り→次週引き継ぎ
- **Chatwork配信にGoogleスプレッドシートリンク含む**
- **AI総評・サマリー・コア売れ筋TOP15・コア落ち・準売れ筋・育成候補・要調査・削除候補・コア月間・削除月間・改善追跡・週次履歴**の12シート

### Google Sheets設定
- スプレッドシートID: `1AT4x_qyohYiEs08RSHs5uFgqBAm51IRsY1ajybsJe0s`
- サービスアカウント: `reffort-claude@reffort-sheets.iam.gserviceaccount.com`
- APIレート対策: シート間 `time.sleep(3)` ＋ `_batch_merge_and_freeze()` でAPI呼び出し削減

### weekly_history.json の設計
- **キー**: W4終了日（日曜日）の`YYYY-MM-DD`
- **per_item保存内容**: sold, cvr, pv, imps, title, price, qty（price/qtyは2026/3/31追加）
- **total_items**: 各週の出品数を保存（週別表示に使用）
- **保持**: 最大12週分

### スケジュールタスク
- `monday-ebay-report-delivery`: 毎週月曜10:00。create_weekly_report_v3.py→send_weekly_report.py自動実行

### まだCSVが必要なもの
- **Advertising Report CSV**: eBayにAPIがないため手動ダウンロード（なくてもレポート生成可能）

### 次の優先タスク
1. 完全死蔵14件の削除確認（佐藤さんへ依頼）
2. 収支表にPLP・Offsite費用を追加（正確な値）
3. promo status（広告状況列）をad_by_itemから正確に表示
4. PLGキャンペーン統合（10個→1個キーベース）

**Why:** eBay売上が月$60,000に低下。スタッフが毎週KPIを確認してアクションできる仕組みが急務
**How to apply:** レポートの話が出たらv3前提。出力はGoogle Sheets優先（Excel併用）。配信は月曜10:00自動。CSVはAdsのみ必要
