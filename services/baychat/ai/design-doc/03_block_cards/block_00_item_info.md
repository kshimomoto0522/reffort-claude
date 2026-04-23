# [0] 商品情報JSON

**何のため**：どの商品についてのやり取りかをAIに教える
**管理者**：BayChat（eBay APIから自動取得）

## 実物コード

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
      "Size": "US 6.5",
      "Color": "YELLOW BLACK",
      "Quantity": "5",
      "StartPrice": "150.0"
    }
    // ... バリエーションは商品ごとに複数入る
  ]
}
```
