---
name: eBay API 2系統の使い分け（Trading vs Sell Fulfillment）
description: Reffortで使うeBay API選定基準とそれぞれの認証・用途
type: reference
originSessionId: 56271ff7-ea79-4c37-b6d5-0b01b13015d1
---
# eBay API 2系統の使い分け

Reffortのツール群は2つのeBay APIを併用する。

## Trading API（XML・Auth'n'Auth）

- **エンドポイント**: `https://api.ebay.com/ws/api.dll`
- **認証**: Auth'n'Auth User Token（`EBAY_USER_TOKEN`）＋ DevID/AppID/CertID
- **用途**:
  - `GetOrders`: オーダー一覧取得・キャンセル状態検知
  - `GetItem`: 商品詳細（DispatchTimeMax など）
  - `GetSellerTransactions` 等その他レガシー機能
- **特徴**:
  - XML/POST・長寿命トークン
  - 新フィールドは反映されない（例: ShipByDate が 2026-04 時点で未返却）
  - 後方互換性のためにeBayは残しているが機能追加はほぼ止まっている
- **Reffortでの扱い**: オーダー取得・キャンセル検知の基本情報源

## Sell Fulfillment API（REST・OAuth2）

- **エンドポイント**: `https://api.ebay.com/sell/fulfillment/v1/...`
- **認証**: OAuth2 User Access Token（refresh_token フローで自動更新）
- **スコープ**: `https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly` （読み取り専用ならこれで十分）
- **用途**:
  - `GET /order/{orderId}`: 正確な発送期限（shipByDate）・フルフィルメント状態
  - `POST /order/{orderId}/shipping_fulfillment`: 出荷作成（将来の自動トラッキング連携用）
- **特徴**:
  - REST/JSON・OAuth2 access_token は 2時間TTL
  - `lineItems[].lineItemFulfillmentInstructions.shipByDate` は eBay が祝日・GW・セラー国カレンダー・商品毎ハンドリングを全て考慮した正確な期限
  - 新機能はこちらに追加される
- **Reffortでの扱い**: 仕入管理表GASで発送期限取得用に使用（2026-04-24〜）。BayChatも同系と推定

## 選定ルール

- オーダー取得・キャンセル状態 → Trading API（コスト低・既存実装流用）
- 発送期限・フルフィルメント詳細 → Sell Fulfillment API（正確性必須）
- 新機能追加時はまず Sell 系（Fulfillment / Inventory / Analytics / Marketing）を調査

## 認証情報の保存場所

- `commerce/ebay/analytics/.env`:
  - `EBAY_APP_ID` / `EBAY_DEV_ID` / `EBAY_CERT_ID`: 両API共通
  - `EBAY_USER_TOKEN`: Trading API用（Auth'n'Auth）
  - `EBAY_RUNAME`: OAuth2フロー用
  - `EBAY_OAUTH_REFRESH_TOKEN`: Sell Fulfillment API用（18ヶ月有効）
- Apps Script の Script Properties に同じキー名でコピー必要（.env だけでは GAS から参照不可）

## refresh_token の再発行手順

1. `commerce/ebay/analytics/` で `_oauth_step1_open_consent.py` を作成・実行
   - EBAY_APP_ID + EBAY_RUNAME + scope を組んで同意URLをブラウザで開く
2. リダイレクト先URL全体を Python 対話スクリプト `_oauth_step2_exchange.py` に貼る
3. スクリプトが `code` を抽出 → eBay token endpoint に POST → refresh_token を .env に自動保存
4. Script Properties にも同じ値を手動で設定（Apps Script側）
5. 使用後 `_oauth_*.py` は削除（機密取扱い）

詳細コード例は [commerce/ebay/tools/gas-shiire-tool-spec.md](../../Desktop/reffort/commerce/ebay/tools/gas-shiire-tool-spec.md) の「Fulfillment API の仕組み」セクション参照。
