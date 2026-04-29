# 仕入管理表 GASツール仕様（gas/shiire/コード.js）

> 親: `commerce/ebay/tools/CLAUDE.md` から「必要時ロード」として参照される詳細ファイル。
> GASツール改修・トリガー調整・重複バグ調査時に参照する。

---

## 概要

eBay Trading API（GetOrders）から新規オーダーを自動取得し、仕入管理表スプレッドシートに反映するGoogle Apps Scriptツール。
発送期限は別途 eBay **Sell Fulfillment API (REST)** から取得（Trading APIには `ShipByDate` が含まれないため）。

---

## ファイル・環境

| 項目 | 値 |
|------|-----|
| マスターファイル | `commerce/ebay/tools/gas/shiire/コード.js`（clasp管理・本番GASと同期） |
| マニフェスト | `commerce/ebay/tools/gas/shiire/appsscript.json` |
| clasp設定 | `commerce/ebay/tools/gas/shiire/.clasp.json`（scriptId本番） |
| 本番Apps Script | `1EGuRaF3Hj1Uhayek4jCIgGQcxzKEJxLaqZmqfsgZbRph_RYUNZRgCNNf` |
| テストApps Script | `1s52yu6RVQ3kCPk0MIvR4Gst-bG_DcmXD3jFLjrFBfqNNbbAtb24hlusv` |
| 本番スプレッドシート | `1B1kFIiu8M5Pw8U8YuERK8ApKUa4S--GfIzBkW53kY3g` |
| テストスプレッドシート | `1vkhstYuPhgQJecDfSdMjL67mWsdthtkHJ6HjnXF-KAk` |
| トリガー | 毎朝9:45頃（nearMinute(45)）本番設定済み |
| Trading API認証 | **Script Properties**: EBAY_DEV_ID / APP_ID / CERT_ID / USER_TOKEN（Auth'n'Auth） |
| Fulfillment API認証 | **Script Properties**: EBAY_OAUTH_REFRESH_TOKEN（18ヶ月有効・OAuth2） |
| Fulfillment APIキャッシュ | `EBAY_OAUTH_ACCESS_TOKEN` + `EBAY_OAUTH_ACCESS_TOKEN_EXPIRES_AT`（自動管理・2時間TTL） |

---

## 主な機能（2026-04-24 Fulfillment API対応後）

- eBay Trading API GetOrders で**過去2日**分のオーダーを取得（FETCH_DAYS_BACK=2）
- `OrderStatus=All` で取得（Cancelled/CancelPendingも含む → キャンセル検知漏れ防止）
- **前回処理時刻（LAST_PROCESSED_CREATED_TIME）以降のみ処理**（Refunded蘇り防止）
- OrderNo + 正規化SKU の組み合わせで重複排除（Z除去正規化で過去データと共存）
- **発送期限: Sell Fulfillment API (REST) から取得**（祝日・GW・週末すべてeBay計算済みの正確な値）
- 過去の仕入履歴から型番・仕入先・仕入値を自動参照
- **タイトルから型番抽出（履歴より完全な値があれば上書き）**＋ **Width（New Balance）**も抽出
- **ミズノ型番: スペース/ハイフン区切り対応**（"P1GC2530 09" → `P1GC253009` 等）
- キャンセル検知4系統（OrderStatus・CancelStatus・BuyerRequestedCancel・CancelReason）
- **多言語サイズラベル対応**（Schuhgröße / Pointure / Taglia 等 + US/JP/UK/EU値パターン検出）
- O列にタイトル（eBay商品ページハイパーリンク付き）
- E3に赤文字太字の処理中通知（スタッフ向け）
- LockService排他ロック（2重実行防止）
- **Z除去はしない**（シートにZ付きSKUを維持、有在庫判定は `hasStock` フラグで）
- 同一オーダー複数商品 → E列（送料）セル結合

---

## 重複バグ対策（3層防御）

- **対策A（根本）**: `normalizeSkuForCompare_` でシート側・API側の両方をZ除去正規化して比較
- **対策G（検出）**: 同一orderNumberが既存にあるのに新規判定された場合、実行ログに警告
- **対策H（事前検査）**: 🛡️ 重複安全チェックメニューで既存重複・Z混在を事前洗い出し

---

## 新設メニュー

- 🛡️ 重複安全チェック（本番反映前に推奨）
- 🔍 特定オーダーのXMLを確認（デバッグ用・特定オーダーIDで生XML取得）
- 📅 ShipByDate抽出テスト（Trading API応答のタグダンプ調査用・基本使わない）
- ⏮️ 前回処理時刻をリセット


---

## Fulfillment API (REST) の仕組み

### 認証フロー
1. **初回セットアップ（手動・1回のみ）**:
   - eBay Developer Console で OAuth2 同意フロー実施
   - `sell.fulfillment.readonly` スコープで認可
   - 戻り値の `refresh_token`（18ヶ月有効）を Script Properties `EBAY_OAUTH_REFRESH_TOKEN` に保存
2. **実行時（自動）**:
   - `getOAuth2AccessToken_()` が refresh_token から access_token を取得しキャッシュ
   - access_token は 2時間 TTL、Script Properties にキャッシュされる
   - 期限切れ5分前になったら自動更新

### APIエンドポイント
- `GET https://api.ebay.com/sell/fulfillment/v1/order/{orderId}`
- レスポンス抜粋: `lineItems[].lineItemFulfillmentInstructions.shipByDate` (ISO8601)

### なぜ Trading API では取れないか
- Trading API `GetOrders` の `OrderArray.Order.ShippingDetails` には `ShipByDate` が含まれない
- 2026-04-24 のタグダンプ実測で48/48件すべて未返却を確認
- Fulfillment API (REST) は eBay が新しい OAuth2 ベースで提供している後継系
- BayChat などのサービスもこちらを利用している

### OAuth2 Refresh Token の取得手順（将来の再発行用）
1. `commerce/ebay/analytics/_oauth_step1_open_consent.py` を作成して実行
   - `EBAY_APP_ID`・`EBAY_RUNAME` を .env から読み、eBay同意画面を開く
2. 同意後のリダイレクトURL（`?code=...` 含む）を控える
3. `_oauth_step2_exchange.py` を作成して実行 → URLを貼り付け → refresh_token を自動で .env に保存
4. Apps Script の Script Properties に `EBAY_OAUTH_REFRESH_TOKEN` として登録
5. スクリプトは `.gitignore` 化で残さない（機密取扱い）

### 既存のOAuth基盤との関係
`commerce/ebay/analytics/ebay_oauth.py` が既に存在し、Marketing API / Analytics API 用の
OAuth認証を管理している（scopes: `sell.analytics.readonly` + `sell.marketing(.readonly)`）。
今回の仕入管理表GASでは別スコープ（`sell.fulfillment.readonly`）が必要で、refresh_token も
別物になる。将来的にスコープ統合することも可能だが、現状は分離運用で問題なし。
同じApp ID・Cert ID・RuName を共用しているだけで、発行されるトークンは別。

---

## SKU Zフラグルール

- サイズ部分のZ = 有在庫（例: `V0126-8.5Z-30`）
- 親SKU先頭のZ ≠ 有在庫（例: `Z0196-11-23` は無在庫）
- 有在庫判定正規表現: `/-\d+\.?\d*Z(?:-|$)/`
- 重複比較時の正規化正規表現: `/(\d+\.?\d*)Z(?=-|$)/`（書き込み時は除去しない）

---

## 本番既存の重複4組（放置・社長指示で削除しない）

過去のZ除去バグによる重複。新コードでは発生しない。

- 行 7233/7597、7242/7363、7361/7776、7568/7792

---

## コード更新手順（2026-04-28以降・clasp版）

```bash
# 1. ローカルで編集
edit commerce/ebay/tools/gas/shiire/コード.js

# 2. 本番にpush（数秒で完了）
cd commerce/ebay/tools/gas/shiire
clasp push

# 3. （任意）本番との差分が気になる時はpullで上書きせず確認
clasp status   # 差分一覧
clasp pull     # 本番を取得（ローカル上書き注意）
```

**Chromeブラウザ・Monaco editor・Ctrl+V 操作は不要**。Google公式CLI経由で完結。

### 旧手順（2026-04-28 以前・Monaco貼付け方式）

旧: PowerShell→Set-Clipboard→Chrome開く→Monaco の setValue('')→ 手動Ctrl+V→ 8秒wait → Ctrl+S

旧手順用の補助ファイル（`gas_copy.html` / `serve_gas.py` / `update_gas_copy.py` / `gas_shiire_b64.txt` / `gas_shiire_content.json` / `gas_shiire_tool.js`）は **clasp移行で全て不要**。social後の手で削除。

### 認証

`clasp login` を1回実行すれば `~/.clasprc.json` に保存され、社長のGoogleアカウントに紐づく**全 Apps Script プロジェクト**で使い回せる。トークンは長期有効（リフレッシュ自動）。
