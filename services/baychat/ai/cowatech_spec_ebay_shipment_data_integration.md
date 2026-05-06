# BayChat AI Reply — eBay 発送データ取込（SHIPMENT BLOCK 注入）仕様書

> 宛先: Cowatech 様
> 作成: 株式会社リフォート（Reffort, Ltd.）
> 作成日: 2026-05-06
> ステータス: **骨子（社長レビュー前）**
> 関連: 既存実装（v2.4 系・admin_prompt v2.3 baseline natural5_lean・stg + prd 反映済み）

---

## 1. 概要・目的

AI Reply の現状では、購入後（post-purchase）のバイヤー問い合わせ（追跡未更新／配送遅延／税関保留／配送業者切替依頼 等）に対して、**実際の発送データ（追跡番号・配送業者・配送予定日・発送期限）**が GPT に渡っていません。そのため AI が以下の問題を抱えています：

| 問題 | 例 |
|---|---|
| 投げやり回答 | 「Please check the tracking number provided in your eBay order」とユーザに丸投げ |
| 抽象的回答 | 「The carrier is processing your shipment」と具体名なし |
| eBay 公式手続きへの振り | 「Please contact eBay customer support」と本来セラー側で対応すべき内容を eBay に丸投げ |

これらを解決するため、**SHIPMENT BLOCK** を AI Reply のペイロードに注入し、GPT が具体的な発送状況を把握できる状態にします。SHIPMENT BLOCK の必要性は社内テスト（cat03 シリーズ）で「絶対必要」と判定済みです。

---

## 2. Cowatech 様への実装依頼スコープ

本仕様で実装をお願いするのは以下 3 点です。

| # | 領域 | 概要 |
|---|---|---|
| (1) | OAuth2 連携追加 | eBay Sell Fulfillment API（`sell.fulfillment.readonly` スコープ）の認証連携をセラー単位で確立（章 3） |
| (2) | 発送データ取得 | AI Reply 生成時に Fulfillment API から発送情報を取得（章 4） |
| (3) | ペイロード注入 | 取得した発送情報を SHIPMENT BLOCK としてペイロードに挿入（章 5） |

### 本仕様の対象外（Reffort 側で対応）

- **admin_prompt 内の SHIPPING DATA SOURCES セクション**: 既に SHIPMENT BLOCK を解釈する記述が入っています（admin_prompt v2.3_baseline_natural5_lean）。Reffort 側で随時調整します。
- **eBay OAuth2 アプリ登録**: Reffort 既存 App ID / Cert ID / RuName を共用することを想定。新規スコープ用の同意フロー実施手順は章 9 に記載。

---

## 3. eBay Sell Fulfillment API 連携

### 3.1 採用する API

| 項目 | 値 |
|---|---|
| API | eBay **Sell Fulfillment API**（REST/OAuth2） |
| エンドポイント | `GET https://api.ebay.com/sell/fulfillment/v1/order/{orderId}` |
| スコープ | `https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly` |
| 認証方式 | OAuth2 User Access Token（refresh_token フローで自動更新） |
| refresh_token 有効期限 | 18 ヶ月 |
| access_token 有効期限 | 2 時間（refresh_token から自動再発行） |

> **補足**: 現行 BayChat が使用していると思われる eBay Trading API（XML/Auth'n'Auth）には `ShipByDate` などの新フィールドが含まれません。Fulfillment API は eBay が新機能を追加し続けている後継系で、Reffort 社内ツール（仕入管理表 GAS）でも 2026-04 から利用しています。

### 3.2 Reffort 側で確立済みの参考実装

Reffort では仕入管理表 GAS で同 API を運用しており、参考になる実装として以下のリポジトリ内に存在します（社長権限で共有可能）：

- `commerce/ebay/tools/gas/shiire/コード.js` の `getOAuth2AccessToken_()` 周辺
- App ID / Cert ID / RuName は Reffort 既存のものを共用予定

---

## 4. 発送データ取得タイミング

### 4.1 取得契機

AI Reply 生成リクエストを受けた時点で、対象オーダーの発送状態を判定し、以下の条件を満たす場合のみ Fulfillment API を呼び出します。

| 状態 | API 呼び出し |
|---|---|
| 注文が存在しない（pre-purchase の問い合わせ） | しない |
| 注文は存在するが未発送（`SHIPPED` 前） | **発送期限**（shipByDate）のみ取得 |
| 既に発送済み | **全項目**（追跡・配送業者・配送予定日・発送期限）取得 |

### 4.2 キャッシュ戦略（提案）

API レート制限と応答速度（標準 3 秒目標）の観点から、以下のキャッシュを提案します。Cowatech 様の現行アーキテクチャに合わせて調整可能です。

| 項目 | 推奨 TTL |
|---|---|
| 未発送オーダー（shipByDate のみ） | 6 時間 |
| 発送済みオーダー（追跡・配送業者など） | 30 分（追跡が直近で更新される可能性） |

---

## 5. SHIPMENT BLOCK の構造（GPT に渡す内容）

### 5.1 注入位置

GPT API リクエストの `messages` 配列のうち、**商品情報 JSON（`messages[0]`）の直後**に、`role: "developer"` メッセージとして挿入してください。

```
messages[0]   = { role: "developer", content: 商品情報JSON }
messages[1]   = { role: "developer", content: SHIPMENT_BLOCK_JSON }   ← ★新規
messages[2..] = チャット履歴 / system / admin_prompt 等（既存通り）
```

### 5.2 SHIPMENT BLOCK JSON フィールド

```json
{
  "shippingCarrier": "FedEx International Priority",
  "trackingNumber": "770012345678",
  "estimatedDeliveryTimeMin": "2026-05-08T08:00:00.000Z",
  "estimatedDeliveryTimeMax": "2026-05-12T08:00:00.000Z",
  "shipByDate": "2026-05-03T14:59:59.000Z",
  "whoPaysShipping": "Buyer"
}
```

| フィールド | 型 | 必須 | データソース（Fulfillment API） | 備考 |
|---|---|---|---|---|
| `shippingCarrier` | string | 発送済みのみ | `shippingFulfillments[].shippingCarrierCode` の表示名 | 業者コード（例: `FEDEX`）ではなく「FedEx International Priority」など人間可読な表示名 |
| `trackingNumber` | string | 発送済みのみ | `shippingFulfillments[].shipmentTrackingNumber` | — |
| `estimatedDeliveryTimeMin` | ISO8601 | 発送済みのみ | Fulfillment API レスポンスの該当フィールド（最早到着日） | UTC・末尾 Z 推奨 |
| `estimatedDeliveryTimeMax` | ISO8601 | 発送済みのみ | Fulfillment API レスポンスの該当フィールド（最遅到着日） | UTC・末尾 Z 推奨 |
| `shipByDate` | ISO8601 | **常時必須**（注文があれば未発送でも） | `lineItems[].lineItemFulfillmentInstructions.shipByDate` | eBay が祝日・GW・セラー国カレンダーを考慮済みの正確な発送期限 |
| `whoPaysShipping` | "Buyer" \| "Seller" | 必須 | `Item.ShippingDetails.ShippingCostPaidByOption`（Trading API・既存取得） | Fulfillment API ではなく既存の Item 情報から流用可 |

> **未取得フィールドの扱い**: 該当フィールドが取得できない場合は、フィールド自体をオブジェクトから省略してください（`null` ではなく省略）。AI 側は欠落フィールドに対しては言及しない仕様です。

### 5.3 注入条件

| ケース | SHIPMENT BLOCK 注入 |
|---|---|
| pre-purchase（注文なし問い合わせ） | 注入しない |
| 注文あり・未発送 | `shipByDate` + `whoPaysShipping` のみ含む簡易版を注入 |
| 注文あり・発送済み | 全フィールドを注入 |

---

## 6. テスト観点（QA）

| # | 観点 | 期待挙動 |
|---|---|---|
| 1 | pre-purchase の AI Reply | SHIPMENT BLOCK が含まれない・既存挙動と完全同一 |
| 2 | 発送済みオーダーの AI Reply | SHIPMENT BLOCK が `messages[1]` に注入され、6 フィールドが入る |
| 3 | 未発送オーダーの AI Reply | SHIPMENT BLOCK に `shipByDate` + `whoPaysShipping` のみ入る |
| 4 | Fulfillment API がエラー時 | SHIPMENT BLOCK 注入をスキップし、AI Reply は従来通り生成（フェイルオープン） |
| 5 | refresh_token 期限切れ時 | エラーログを残し、SHIPMENT BLOCK 注入をスキップ（AI Reply 自体は継続） |
| 6 | レート制限到達時 | キャッシュから応答・キャッシュなしなら注入スキップ |

---

## 7. 後方互換性・デフォルト挙動

| 項目 | 内容 |
|---|---|
| 既存 stg / prd デプロイへの影響 | SHIPMENT BLOCK 未注入時の挙動は改修前と完全同一 |
| admin_prompt 側の対応 | 既に SHIPPING DATA SOURCES セクションで SHIPMENT BLOCK の存在を前提とした記述あり（v2.3 baseline natural5_lean）。注入が始まれば自動的に活用される |
| Trading API 既存呼び出し | 影響なし（Fulfillment API は別系統・別 refresh_token） |

---

## 8. 実装順序の推奨

1. **OAuth2 同意フロー組み込み**: セラー単位で `sell.fulfillment.readonly` スコープの refresh_token を取得・保存
2. **Fulfillment API 呼び出しロジック実装**: orderId から発送情報を取得（章 4・章 5）
3. **キャッシュ層追加**: 章 4.2 の TTL でレスポンス保存
4. **SHIPMENT BLOCK 組立 & 注入**: 章 5 のフィールド整形 → `messages[1]` に挿入
5. **stg で動作確認**: 章 6 のテスト観点
6. **prd 反映**

---

## 9. OAuth2 同意フロー（実装参考）

セラー単位で初回のみ OAuth2 同意が必要です。Reffort 既存の OAuth2 認証導線（BayChat 既存ログイン）に追加スコープとして組み込むか、別途同意ページを設けるかは Cowatech 様の設計判断にお任せします。

| 項目 | 値 |
|---|---|
| App ID / Cert ID / RuName | Reffort 既存値を共用予定（社長判断） |
| 必要スコープ | `https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly` |
| 同意エンドポイント | `https://auth.ebay.com/oauth2/authorize?...` |
| トークン発行エンドポイント | `https://api.ebay.com/identity/v1/oauth2/token` |
| refresh_token 取得後の保存 | BayChat 既存セラー認証情報テーブルに追加カラム想定 |

---

## 10. 工数・見積依頼

本仕様の実装にかかる工数とコストの見積を Slack スレッドにて頂戴できますと幸いです。特に以下 3 点の工数感を分けて教えていただけますと、Reffort 側の優先度判断がしやすくなります：

- (a) OAuth2 連携追加（章 3・9）
- (b) Fulfillment API 呼び出し & キャッシュ（章 4）
- (c) SHIPMENT BLOCK 組立 & 注入（章 5）

不明点・仕様確認が必要な箇所があれば、Slack thread にてご連絡ください。

以上、よろしくお願いいたします。

株式会社リフォート（Reffort, Ltd.）
代表取締役　下元 敬介
