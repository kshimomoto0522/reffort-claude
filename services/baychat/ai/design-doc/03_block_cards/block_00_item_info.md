# [0] 商品情報JSON

**何のため**：どの商品についてのやり取りかをAIに教える
**管理者**：BayChat（eBay APIから自動取得）

## 在庫数（Quantity）の扱い — 重要

eBay公式 API の `Item.Quantity` は **「累計販売数 + 現在の販売可能数」の合計値**（= 出品開始時に登録した在庫総数）。これをそのまま GPT に渡すと「395個も在庫がある」と誤認する。

GPT に渡す `Quantity` は **販売可能数（Available）= eBay API の `Quantity` − `SellingStatus.QuantitySold`** を算出した値（バリエーションも同じ式・各バリエーション単位で算出）。負値が出た場合は 0 でガード。

| eBay API 生値 | GPT に渡す値 |
|---|---|
| `Item.Quantity` | `max(0, Item.Quantity - Item.SellingStatus.QuantitySold)` |
| `Variation.Quantity` | `max(0, Variation.Quantity - Variation.SellingStatus.QuantitySold)` |

> 2026-05-05 修正済み（クエットさん対応）。誤りの背景：当初の仕様書（`cowatech_payloads/spec_sheets/Input_item_info.csv` 行17/50）が `Item.Quantity` を「販売可能数」と誤記していた。

## 実物コード（修正後の例）

```json
{
  "ItemID": "355315032752",
  "Title": "Onitsuka Tiger MEXICO 66 Kill Bill 1183C102 751 YELLOW BLACK",
  "PrimaryCategoryName": "Clothing, Shoes & Accessories:Men:Men's Shoes:Athletic Shoes",
  "ListingType": "FixedPriceItem",
  "StartPrice": "150.0",
  "BuyItNowPrice": "0.0",
  "Quantity": "15",
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
      "Size": "US 6.5",
      "Color": "YELLOW BLACK",
      "Quantity": "1",
      "StartPrice": "150.0"
    }
    // ... バリエーションは商品ごとに複数入る
    // ※ Variation.Quantity も販売可能数（残り在庫）。例：US 6.5 サイズは「Last one」=残り1
  ]
}
```

> 上記 Quantity=15 は ItemID 355315032752 の 2026-05-06 時点 stg 値（API生値: Quantity=424, QuantitySold=409 → 算出 15）。Variation.Quantity=1 は size US 6.5 バリエーション（API生値: Q=41, Sold=40 → 算出 1）。
