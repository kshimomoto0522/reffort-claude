# 12. eBay API 連携仕様

> ✅ **v0.2 完成版**
> このファイルの役割：**商品情報JSON（[0]ブロック）のデータソース** である eBay API 取得項目を完全ドキュメント化。`Input_item_info.csv` をマスター化する。

---

## 🎯 概要

BayChatは eBay Trading API の **GetItem** エンドポイントを使って商品情報を取得し、AI Replyペイロードの[0]ブロックに JSON 文字列として埋め込む。

`Input_item_info.csv` には **42フィールド** の取得パラメータが定義されており、Tân・Quyết・下元さんの3者で採用可否を議論済み。

---

## 📋 完全フィールドリスト（42項目）

凡例：
- ✅ = 採用（ペイロードに含める）
- 🟡 = Tân/Quyết採用だが下元×
- ❌ = 不採用

### Item 基本情報（5項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.ItemID` | 商品ID | ✅ | ✅ | ✅ | **✅** |
| `Item.Title` | 商品タイトル | ✅ | ✅ | ✅ | **✅** |
| `Item.Subtitle` | サブタイトル | ✅ | ✅ | ✅ | ❌ |
| `Item.Description` | 商品説明（詳細HTML） | ✅ | ✅ | ✅ | ❌ |
| `Item.ListingType` | 出品形式 | ✅ | ✅ | ✅ | **✅** |

### カテゴリ（2項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.PrimaryCategory.CategoryName` | 主カテゴリ名 | ✅ | ✅ | ✅ | **✅** |
| `Item.SecondaryCategory.CategoryName` | 副カテゴリ名 | ✅ | ✅ | ✅ | ❌ |

### 価格・在庫（6項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.ListingDuration` | 出品期間 | ✅ | ✅ | ❌ | ❌ |
| `Item.StartPrice` | 開始価格 | ✅ | ✅ | ✅ | **✅** |
| `Item.BuyItNowPrice` | 即決価格 | ✅ | ✅ | ✅ | **✅** |
| `Item.Quantity` | 在庫総数 | ✅ | ✅ | ✅ | **✅** |
| `Item.QuantitySold` | 売却数 | ✅ | ❌ | ❌ | ❌ |
| `Item.SellingStatus.CurrentPrice` | 現在価格 | ✅ | ✅ | ✅ | **✅** |

### 出品状況（4項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.SellingStatus.BidCount` | 入札数 | ✅ | ✅ | ❌ | ❌ |
| `Item.SellingStatus.ListingStatus` | 出品ステータス | ✅ | ✅ | ✅ | **✅** |
| `Item.SellingStatus.TimeLeft` | 残り時間 | ✅ | ✅ | ✅ | **✅** |
| `Item.ListingDetails.EndTime` | 終了日時 | ✅ | ❌ | ✅ | **✅** |

### URL・セラー情報（4項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.ListingDetails.ViewItemURL` | 商品ページURL | ✅ | ❌ | ✅ | **✅** |
| `Item.Seller.UserID` | セラーID | ✅ | ❌ | ❌ | ❌ |
| `Item.Seller.FeedbackScore` | FBスコア | ✅ | ❌ | ❌ | ❌ |
| `Item.Seller.PositiveFeedbackPercent` | ポジティブFB % | ✅ | ✅ | ❌ | ❌ |

### 配送（3項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.ShippingDetails.ShippingType` | 配送種別 | ✅ | ✅ | ✅ | **✅** |
| `Item.ShippingDetails.ShippingServiceOptions.ShippingService` | 配送サービス名 | ✅ | ✅ | ✅ | **✅** |
| `Item.ShippingDetails.ShippingServiceOptions.ShippingServiceCost` | 配送料金 | ✅ | ✅ | ✅ | **✅** |

### リターンポリシー（4項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.ReturnPolicy.ReturnsAcceptedOption` | リターン受付 | ✅ | ✅ | ✅ | **✅** |
| `Item.ReturnPolicy.RefundOption` | 返金方式 | ✅ | ✅ | ✅ | **✅** |
| `Item.ReturnPolicy.ReturnsWithinOption` | リターン期間 | ✅ | ✅ | ✅ | **✅** |
| `Item.ReturnPolicy.ShippingCostPaidByOption` | リターン送料負担 | ✅ | ✅ | ✅ | **✅** |

### 画像・所在地（5項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.PictureDetails.PictureURL` | 画像URL | ✅ | ❌ | ❌ | ❌ |
| `Item.Country` | 商品所在国 | ✅ | ✅ | ✅ | **✅** |
| `Item.Location` | 所在地 | ✅ | ✅ | ✅ | **✅** |
| `Item.Currency` | 通貨 | ✅ | ✅ | ✅ | **✅** |
| `Item.HitCount` | 閲覧数 | ✅ | ❌ | ❌ | ❌ |

### ウォッチ・値引き（3項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.WatchCount` | ウォッチ数 | ✅ | ❌ | ❌ | ❌ |
| `Item.BestOfferDetails.BestOfferEnabled` | 値引き交渉可否 | ❌ | ❌ | ✅ | ❌ |
| `Item.BestOfferDetails.BestOfferCount` | 値引き提案数 | ✅ | ✅ | ✅ | ❌ |

### 商品属性（2項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.ItemSpecifics.NameValueList.Name` | 属性名 | ✅ | ✅ | ✅ | ❌ |
| `Item.ItemSpecifics.NameValueList.Value` | 属性値 | ✅ | ✅ | ✅ | ❌ |

### バリエーション（5項目）

| Param | 意味 | Tân | Quyết | 下元 | 本番採用 |
|-------|------|-----|-------|------|---------|
| `Item.Variations.Variation.SKU` | SKU | ✅ | ✅ | ✅ | **✅** |
| `Item.Variations.Variation.StartPrice` | バリ価格 | ✅ | ✅ | ✅ | **✅** |
| `Item.Variations.Variation.Quantity` | バリ在庫 | ✅ | ✅ | ✅ | **✅** |
| `Item.Variations.Variation.VariationSpecifics.NameValueList.Name` | バリ属性名 | ✅ | ✅ | ✅ | **✅**（`SpecificName`） |
| `Item.Variations.Variation.VariationSpecifics.NameValueList.Value` | バリ属性値 | ✅ | ✅ | ✅ | **✅**（`SpecificValue`） |

---

## 📊 採用状況サマリ

| 状態 | 件数 | 割合 |
|------|-----|-----|
| 本番採用（24項目） | 24 | 57% |
| 3者採用だが本番未実装 | 4 | 10% |
| 一部賛成（部分採用） | 14 | 33% |
| **合計** | **42** | **100%** |

---

## 🆕 追加フィールドの検討余地

### 高優先度（追加検討すべき）

| フィールド | 理由 |
|----------|------|
| `Item.Description` | バイヤーの商品特性質問への精度向上 |
| `Item.ItemSpecifics.NameValueList` | サイズ・色・素材の詳細回答 |
| `Item.BestOfferDetails.BestOfferEnabled` | 値引き交渉への対応可否を明確に |

### 中優先度

| フィールド | 理由 |
|----------|------|
| `Item.PictureDetails.PictureURL` | 将来のVision対応時に必要 |
| `Item.Seller.PositiveFeedbackPercent` | セラーの信用度情報 |

### 低優先度（追加不要）

| フィールド | 理由 |
|----------|------|
| `Item.Seller.UserID` | 別途BayChat側で持っている |
| `Item.HitCount` / `Item.WatchCount` | 返信品質に不要 |

---

## 🐛 既知の問題

### `whoPaysShipping` の欠損

本番ペイロードで観察：
```json
"whoPaysShipping": "No data available to respond."
```

**原因推定**：
- eBay Trading API `GetItem` では `whoPaysShipping` は直接取れない
- 代わりに `Item.ShippingDetails` から推測する必要がある
- BayChat側で推測ロジックが未実装？

**影響**：AIが送料責任を誤って伝えるリスク

**対応案**：
1. `Item.ShippingCostPaidByOption` + `Item.InternationalShippingServiceOption` から導出する
2. 値が取れない場合はフィールド自体を省略する（AI に誤情報を与えない）

---

## 🔌 API仕様

### 使用API
- **eBay Trading API**：`GetItem` エンドポイント
- または：**eBay Sell API**：`GetInventoryItem`（新世代）

### 認証
- OAuth 2.0（user token）
- セラーごとにトークン管理

### レート制限
- Trading API：1日5,000コール/アプリケーション
- Sell API：より緩い制限

### キャッシング
- BayChat側で商品情報をDBキャッシュしている可能性あり
- ただしキャッシュ更新タイミングは未確認

---

## ⚠️ 未解決の論点

| # | 論点 | 重要度 |
|---|-----|------|
| — | `whoPaysShipping` 取得ロジックの修正 | 🔴 高 |
| — | `Item.Description` 追加の検討（トークン増加のトレードオフ） | 🟡 中 |
| — | eBay API キャッシュの更新頻度・仕様 | 🟡 中 |
| — | バリエーション150+ 商品のトークン最適化 | 🟡 中 |

---

## 🤝 Cowatech合意事項

| 項目 | 合意内容 | 合意日 | 根拠 |
|------|--------|------|------|
| 採用フィールド | Input_item_info.csv の3者TRUE行 | プロジェクト初期 | `Input_item_info.csv` |
| API選定 | eBay Trading API | プロジェクト初期 | BayChat実装 |

---

## 📚 関連ドキュメント

| ドキュメント | 役割 |
|----------|------|
| `Input_item_info.csv` | 一次情報（Cowatech側で管理） |
| `block_00_item_info.md` | ブロックカード（このドキュメントの概要版） |
| `gpt_api_payload.txt` | 本番実装の実データ |
