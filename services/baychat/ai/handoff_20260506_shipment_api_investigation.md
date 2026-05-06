# BayChat AI Reply — 発送追跡 API 調査・方針確定 / 次セッション引継ぎ（2026-05-06）

> **次セッション冒頭でこのファイルを最初に読んでください。**
> 続いて自動ロード対象 memory: `feedback_baychat_ai_reply_stance.md` / `feedback_baychat_vs_campers_user_count.md`（**今日新設**）

---

## 🟡 セッションを一旦中断する理由

Orange Connex（OC）担当者に **非公開追跡 API の共有依頼メッセージを送信済み**。返信待ちのため、本件はそこで再開。

---

## 🟢 本日（2026-05-06）の到達点

### A. Quantity 修正の検証 → 完了
- stg DB（`view_product_ebay`）に直接アクセスし、ItemID `355315032752` の eBay 生値を確認
  - `Item.Quantity = 424`、`SellingStatus.QuantitySold = 409` → 期待 Available = **15**
  - Variation 各サイズも `Q − Sold` で eBay 表示「Last one」と整合
- 設計図側を訂正
  - **更新**: `services/baychat/ai/design-doc/03_block_cards/block_00_item_info.md`（Quantity 計算ルール明記＋例値訂正）
  - **新規**: `services/baychat/ai/cowatech_payloads/spec_sheets/Input_item_info_quantity_correction_20260506.md`（仕様書 行17/18/50 訂正メモ）
- ライブペイロード検証（Cowatech 側コードの直接確認）は次の本番ペイロード受領時にまとめて実施。緊急性なし

### C. eBay Shipment history API 取込 → **方針大転換** & 仕様書骨子は破棄予定

#### 当初路線（破棄）
- Cowatech向け `cowatech_spec_ebay_shipment_data_integration.md` を作成（10章構成・200行超）→ **eBay Sell Fulfillment API 経由で SHIPMENT BLOCK 注入**前提
- **致命的事実誤認**: ① App ID 共用前提（BayChat は別 App と社長指摘）② 「全部新規」前提（BayChat が既に未発送/発送済/配達済/トラブルを保持と社長指摘）

#### 徹底調査の結論
eBay 全 API（Sell Fulfillment / Sell Logistics beta / Trading / Buy Order v1 / Post-Order / Resolution / Marketplace Insights / Browse 等）を実機テスト含めて確認した結果：

- ✅ **eBay は scan events のデータ自体は持っている**（Post-Order `/return/{returnId}/tracking` の scanHistory がその証拠）
- ❌ **しかし通常の outbound shipment には公開 API が一切ない**
  - Post-Order tracking: 実機で `400 Invalid Input - parameter: returnId` 確定（returnId 必須・orderId 不可）
  - `/post-order/v2/order/{orderId}/tracking` 推測端点: 実機で `404`
  - Sell Logistics getShipment: `403 Insufficient permissions` + そもそも eBay 純正ラベル限定（Reffort は Cpass 経由なので対象外）
  - Buy Order API getPurchaseOrder: purchaseOrderId 必須・バイヤー側 ID でセラー取得不可

#### 確定した実装方針（社長 OK）

| 層 | 内容 | 工数 |
|---|---|---|
| **層A**（即実装可）| BayChat 既存DBの未発送/発送済/配達済/トラブル状態 + 追跡番号 + 配送業者 + 配達予定日を **構造化** SHIPMENT BLOCK として GPT に注入 | 小 |
| **層B1** | FedEx 公開 Tracking API（無料・10万req/日・OAuth2）→ scan events 追加 | 中 |
| **層B2** | DHL Express 公開 Tracking API（無料・API Key）→ scan events 追加 | 中 |
| **層B3** | **Orange Connex 非公開 API**（社長コネ経由）→ scan events 追加。**SpeedPAK Standard / Expedited / Economy（裏 EMS 等）まで OC が集約取得しているなら全カバー** | 中（仕様到着後）|
| 層C | UPS / USPS / EMS 直契約 | **切り捨て**（cross-border中心のためカバー率影響小）|

#### 生成時間への影響対策
**バックグラウンド同期＋キャッシュ方式で確定**（社長 OK）：
- BayChat バックエンドが定期ポーリング（未発送=6h / 発送済=30min / 配達済=固定 等）で配送業者 API → DB 保存
- AI Reply 時は DB 読込のみ（+5〜10ms、生成時間に実質影響なし）
- 同期呼出（+300〜800ms）方式は不採用

#### Orange Connex 担当者宛て依頼メッセージ
社長から OC 担当者に送信済み。要点：
- BayChat（約500セラー利用）の AI Reply に組み込みたい
- SpeedPAK 追跡番号に対するスキャンイベント取得 API 仕様希望
- 認証方式・レート制限・利用条件を含む API ドキュメント希望
- バイヤー直接公開はせずバックエンドのみで利用

→ **OC 返信が来るまで仕様書ドラフトは凍結**

---

## 📂 次セッション開始時に確認するもの

| ファイル | 役割 |
|---|---|
| 本ファイル | 当面の唯一の引継ぎ |
| `cowatech_spec_ebay_shipment_data_integration.md` | **凍結中・OC 仕様到着後にまるごと書き直し**（旧 Fulfillment API 前提のため流用不可） |
| `design-doc/03_block_cards/block_00_item_info.md` | Quantity 計算ルールが入ったので参照 |

---

## 🟡 OC 返信後の作業順（推奨）

1. OC API 仕様確認 → SpeedPAK Economy も取れるか判定（取れない場合は EMS 直契約セラーを切り捨て扱い）
2. 凍結中の `cowatech_spec_ebay_shipment_data_integration.md` を **層A + 層B1 + 層B2 + 層B3** 構成に全面書き直し
3. Cowatech に Slack で見積依頼
4. 並行して `block_chat_history.md` または新カード（仮 `block_shipment_status.md`）の設計図更新

---

## ⚠️ 残課題（natural5_lean プロンプト側・本日未着手）

`handoff_20260505_natural5_lean_complete.md` に記載の以下は本日未着手（OC 案件と並行して再開可能）：

- 🔴 cat03_05 保証書欠品ケース（全トーン低スコア）
- 🟡 cat03 FRIENDLY/ASSERTIVE スコア低下（圧縮影響）
- 🟡 cat02_05 / cat02_10 negative denial 残存

---

## 📋 本日のクエットさん側 Slack 状況

- **「主張」トーン追加スレッド**: 工数・コスト見積待ち（催促禁止）
- **商品データ Quantity 値スレッド**: クエットさん修正完了報告済み・stg 検証は次の本番ペイロード受領時

---

## 📝 本日新設・更新ファイル一覧

| 種別 | パス |
|---|---|
| 新規 | `services/baychat/ai/handoff_20260506_shipment_api_investigation.md`（本ファイル）|
| 新規 | `services/baychat/ai/cowatech_payloads/spec_sheets/Input_item_info_quantity_correction_20260506.md` |
| 新規（凍結）| `services/baychat/ai/cowatech_spec_ebay_shipment_data_integration.md` |
| 更新 | `services/baychat/ai/design-doc/03_block_cards/block_00_item_info.md` |
| 軽微更新 | `services/baychat/ai/testing/db_connect.py`（`.env.vps` 探索パス追加） |
| 削除 | `commerce/ebay/analytics/_probe_fulfillment_api.py`（PII 含むため）|
| 削除 | `commerce/ebay/analytics/_probe_fulfillment_api_result.json`（PII 含むため）|
| 削除 | `commerce/ebay/analytics/_probe_postorder_tracking.py` |
| memory 新規 | `memory/feedback_baychat_vs_campers_user_count.md` |
| memory 更新 | `memory/MEMORY.md`（インデックス追記）|

---

*作成: 2026-05-06 夕方（A完了・C方針大転換確定・OC返信待ち）*
