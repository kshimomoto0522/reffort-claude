# Input_item_info.csv 訂正メモ — Quantity の意味（2026-05-06）

## 訂正対象

| 行 | パラメータ | 元の記述（Ý nghĩa） | 訂正後の意味 |
|---|---|---|---|
| 17 | `Item.Quantity` | Số lượng sản phẩm | **eBay API 生値 = 累計販売数 + 販売可能数**（= 出品開始時に登録した在庫総数） |
| 18 | `Item.QuantitySold` | Số lượng đã bán | **累計販売数**（出品開始時からの累計） |
| 50 | `Item.Variations.Variation.Quantity` | Số lượng biến thể | **各バリエーションの eBay API 生値 = そのバリエーションの累計販売数 + 現在の販売可能数** |

## GPT に渡す値の算出ルール（2026-05-05 修正済み）

eBay API の `Item.Quantity` をそのまま GPT に渡すと「在庫が大量にある」と誤認するため、**販売可能数（Available）を算出して渡す**。

```
GPT入力 Quantity     = max(0, Item.Quantity - Item.SellingStatus.QuantitySold)
GPT入力 Variation.Quantity = max(0, Variation.Quantity - Variation.SellingStatus.QuantitySold)
```

- 各バリエーション単位で個別算出（バリエーションの累計でも合計でもない）
- 負値が出た場合は 0 でガード
- Variation がない商品（単一在庫）も同じ式で対応

## 検証例（ItemID 355315032752・2026-05-06 時点）

| 項目 | eBay API 生値 | 算出後（GPT入力） |
|---|---|---|
| Top-level | Quantity=424, QuantitySold=409 | **15** |
| Variation US 6.5 | Quantity=41, Sold=40 | **1**（eBay 表示「Last one」一致） |
| Variation US 7 | Quantity=46, Sold=45 | **1** |
| Variation US 7.5 | Quantity=23, Sold=22 | **1** |

## 経緯

- 2026-05-04: Claude が「`Item.Quantity` の値が累計販売数と一致している」と誤認指摘 → 仕様書通りに修正してほしいと依頼
- 2026-05-05: クエットさんから「仕様書の誤り。`Item.Quantity = QuantitySold + 販売可能数` が eBay API 仕様」と説明
- 同日: 社長がバリエーション在庫ロジックを補足説明（各バリエーション単位）
- 同日: クエットさんが BayChat バックエンドの算出ロジック修正を実装（「上の件対応しました」）
- 2026-05-06: 設計図側を本ファイルおよび `design-doc/03_block_cards/block_00_item_info.md` で訂正

## 関連ファイル

- 設計図カード: `services/baychat/ai/design-doc/03_block_cards/block_00_item_info.md`
- 仕様書原本: `services/baychat/ai/cowatech_payloads/spec_sheets/Input_item_info.csv`（行17/18/50）
- Slack スレッド: `#baychat-ai導入` 「商品データ Item.Quantity / Variations[].Quantity の値について」
