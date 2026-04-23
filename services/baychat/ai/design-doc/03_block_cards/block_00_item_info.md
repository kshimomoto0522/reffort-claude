# ブロックカード：[0] 商品情報JSON

> ✅ **v0.2 完成版**

---

## 📇 基本情報

| 項目 | 内容 |
|------|------|
| **ブロックID** | `item_info` |
| **順序** | [0]（先頭） |
| **role** | `developer` |
| **管理主体** | BayChat（DB自動取得・eBay API連携） |
| **編集場所** | 編集不可（DBスキーマ＋eBay API仕様依存） |
| **現行バージョン** | 仕様固定 |
| **実物ファイル** | `services/baychat/ai/cowatech_payloads/gpt_api_payload.txt` [0]（完全実データ） |
| **変更頻度** | ❌ 仕様固定（フィールド追加時のみ） |
| **ON/OFF** | 常時ON |
| **概算トークン** | ~800 tokens（バリエーション15個想定） |

---

## 🎯 このブロックの目的

AIに **「どの商品についてのやり取りか」** の完全な文脈を最初に与える。バイヤーが商品名・サイズ・色等を言及した際、この情報を参照して正確に応答できるようにする。

---

## 📐 現行の完全フィールド一覧（本番実データ）

本番ペイロード（`gpt_api_payload.txt` [0]）の実データ：

```json
{
  "ItemID": "355315032752",
  "Title": "Onitsuka Tiger MEXICO 66 Kill Bill 1183C102 751 YELLOW BLACK",
  "PrimaryCategoryName": "Clothing, Shoes & Accessories:Men:Men's Shoes:Athletic Shoes",
  "ListingType": "FixedPriceItem",
  "StartPrice": "150.0",
  "BuyItNowPrice": "0.0",
  "Quantity": "395",
  "CurrentPrice": "150.0",
  "ListingStatus": "Active",
  "TimeLeft": "P8DT1H28M14S",
  "EndTime": "2026-04-24T03:28:17.000Z",
  "ViewItemURL": "https://www.ebay.com/itm/Onitsuka-Tiger-MEXICO-66-Kill-Bill-1183C102-751-YELLOW-BLACK-/355315032752",
  "ShippingType": "Flat",
  "ShippingService": "US_ExpeditedSppedPAK",
  "ShippingServiceCost": "30.0",
  "ReturnsAcceptedOption": "ReturnsAccepted",
  "RefundOption": "MoneyBack",
  "ReturnsWithinOption": "Days_60",
  "ShippingCostPaidByOption": "Seller",
  "Country": "JP",
  "Location": "YOKOHAMA",
  "Currency": "USD",
  "Variations": [
    {
      "SKU": "V0265-6.5-57",
      "StartPrice": "150.0",
      "Quantity": "36",
      "SpecificName": "US Shoe Size (Men's)",
      "SpecificValue": "US6.5/JP25"
    },
    ... （全15バリエーション）
  ],
  "whoPaysShipping": "No data available to respond."
}
```

---

## 📋 フィールド完全リスト（22フィールド + Variations配列）

| フィールド | 型 | 意味 | 実例 |
|----------|---|------|-----|
| `ItemID` | string | eBay商品ID | `"355315032752"` |
| `Title` | string | 商品タイトル | `"Onitsuka Tiger MEXICO 66 Kill Bill..."` |
| `PrimaryCategoryName` | string | カテゴリ階層（`:`区切り） | `"Clothing, Shoes & Accessories:Men:Men's Shoes:Athletic Shoes"` |
| `ListingType` | string | 出品形式 | `"FixedPriceItem"` |
| `StartPrice` | string (decimal) | 開始価格 | `"150.0"` |
| `BuyItNowPrice` | string (decimal) | 即決価格 | `"0.0"` |
| `Quantity` | string (int) | 在庫総数 | `"395"` |
| `CurrentPrice` | string (decimal) | 現在価格 | `"150.0"` |
| `ListingStatus` | string | 出品ステータス | `"Active"` |
| `TimeLeft` | string (ISO8601 Duration) | 残り時間 | `"P8DT1H28M14S"`（8日1時間28分14秒） |
| `EndTime` | string (ISO8601) | 終了日時 | `"2026-04-24T03:28:17.000Z"` |
| `ViewItemURL` | string (URL) | 商品ページURL | eBay URL |
| `ShippingType` | string | 配送種別 | `"Flat"`, `"Calculated"`, etc |
| `ShippingService` | string | 配送サービス名 | `"US_ExpeditedSppedPAK"` |
| `ShippingServiceCost` | string (decimal) | 配送料金 | `"30.0"` |
| `ReturnsAcceptedOption` | string | リターン受付 | `"ReturnsAccepted"`, `"ReturnsNotAccepted"` |
| `RefundOption` | string | 返金方式 | `"MoneyBack"` |
| `ReturnsWithinOption` | string | リターン期間 | `"Days_60"`, `"Days_30"`, etc |
| `ShippingCostPaidByOption` | string | リターン送料負担 | `"Seller"`, `"Buyer"` |
| `Country` | string | 商品所在国コード | `"JP"` |
| `Location` | string | 商品所在地 | `"YOKOHAMA"` |
| `Currency` | string | 通貨 | `"USD"` |
| `Variations` | array | バリエーション配列 | 下記参照 |
| `whoPaysShipping` | string | 送料負担者 | ⚠️ `"No data available to respond."` ← **問題あり** |

### Variations配列の構造

```json
{
  "SKU": "V0265-6.5-57",
  "StartPrice": "150.0",
  "Quantity": "36",
  "SpecificName": "US Shoe Size (Men's)",
  "SpecificValue": "US6.5/JP25"
}
```

| フィールド | 意味 |
|----------|------|
| `SKU` | バリエーション固有ID（内部在庫管理用） |
| `StartPrice` | バリエーション別価格（通常は親商品と同じ） |
| `Quantity` | バリエーション別在庫数 |
| `SpecificName` | 属性名（サイズ名・色名等） |
| `SpecificValue` | 属性値（`"US6.5/JP25"` のような複合表記可） |

---

## 📊 eBay APIから取得するフィールドの全体像

**重要**：BayChatがeBay APIから取得できるフィールドは `Input_item_info.csv` に **42項目** 定義されている。そのうち実際にペイロードに含めているのは上記の約24フィールド。残りは将来の拡張候補。

**未使用だが取得可能なフィールド（例）**：
- `Item.Description`（商品説明HTML）
- `Item.Subtitle`（副タイトル）
- `Item.Seller.FeedbackScore` / `Item.Seller.PositiveFeedbackPercent`
- `Item.PictureDetails.PictureURL`（画像URL）
- `Item.BestOfferDetails.BestOfferEnabled`（値引き交渉可否）
- `Item.ItemSpecifics.NameValueList`（商品属性）
- `Item.HitCount` / `Item.WatchCount`（閲覧・ウォッチ数）

**完全リストは `12_ebay_api_integration.md` を参照。**

---

## 🌐 影響範囲

### 直接影響する要素
- AIがバイヤー質問に答える精度（サイズ・価格・在庫・配送に関する質問）
- 返品ポリシーの自動説明
- バリエーション特定の精度

### 間接影響する要素
- トークン消費量の大部分（~800 tokens）
- バリエーションが多い商品（150種等）のペイロード肥大化
- 古いDBデータを参照している場合の情報鮮度問題

### 副作用のリスク
- バリエーション配列の無制限展開による**トークン超過リスク**
- `whoPaysShipping` が `"No data available to respond."` と欠損時、AIが誤った送料情報を伝えるリスク

---

## ⚠️ 未解決の論点

| # | 論点 | 重要度 |
|---|-----|------|
| — | バリエーション数が150個など多い場合のトークン最適化（全展開 vs 代表Nのみ vs サマリ化） | 🔴 高 |
| — | `whoPaysShipping: "No data available to respond."` の原因・対応 | 🔴 高 |
| — | `Item.Description`（商品説明）を含めるべきか（バイヤー質問への精度向上） | 🟡 中 |
| — | 画像URLを含めない理由（現状テキスト専用のため） | 🟡 低 |

---

## 🤝 Cowatech合意事項

| 項目 | 合意内容 | 合意日 | 根拠 |
|------|--------|------|------|
| 取得フィールド | 上記24フィールド | プロジェクト初期 | `Input_item_info.csv` TRUE列 |
| 取得ソース | eBay GetItem API | プロジェクト初期 | BayChat実装 |
| 配置順序 | [0] 先頭 | プロジェクト初期 | `gpt_api_payload.txt` |
| フォーマット | JSON文字列として `content` に埋め込み | プロジェクト初期 | 同上 |

---

## 📚 関連ドキュメント

| ドキュメント | 役割 |
|----------|------|
| `gpt_api_payload.txt` | 本番実装の実データ |
| `Input_item_info.csv` | eBay API取得パラメータ全42項目 |
| `12_ebay_api_integration.md` | eBay API連携仕様（このカードの拡張） |
| `04_conditional_logic.md` | このブロックが常時ONであることの確認 |
