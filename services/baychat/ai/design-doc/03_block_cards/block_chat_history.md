# ブロックカード：[1..N] チャット履歴

> ✅ **v0.2 完成版**

---

## 📇 基本情報

| 項目 | 内容 |
|------|------|
| **ブロックID** | `chat_history` |
| **順序** | [1..N]（商品情報JSONの直後、プロンプトブロック群の前） |
| **role** | `user` / `assistant` / `system` |
| **管理主体** | BayChat（DB自動取得） |
| **編集場所** | 編集不可（DBメッセージ・イベントテーブル） |
| **現行バージョン** | 仕様固定 |
| **実物ファイル** | `gpt_api_payload.txt` [1..9] + `SUMMARY_PROMT.csv`（仕様） + `quy_doi_type_chat.csv`（event変換ルール） |
| **変更頻度** | ❌ 仕様固定 |
| **ON/OFF** | 常時ON（履歴が1件以上ある場合） |
| **概算トークン** | ~1500 tokens（10往復想定） |

---

## 🎯 このブロックの目的

バイヤーとのやり取り・発生イベントの文脈をAIに渡す。AIはこれを読んで：
1. 会話の現状を把握（何が解決済みか・何が未解決か）
2. LATESTメッセージで何が求められているかを特定
3. 現在関連することだけに応答

---

## 📐 role別の構造（`SUMMARY_PROMT.csv` 由来）

### 3種類のrole

| role | 意味 | content形式 |
|------|-----|-----------|
| `user` | バイヤーのメッセージ | `[{timing}] {buyer's message}` |
| `assistant` | セラーのメッセージ（手動返信＋自動メッセージ含む） | `[{timing}] {seller's message}` |
| `system` | eBayイベント（注文・返品リクエスト等） | `event: [{timing}] {event content}` |

### timing形式
すべて **ISO 8601 UTC** で統一：`2026-03-13T08:20:57.000Z`

### 実例（`gpt_api_payload.txt` より）

**user role（バイヤーメッセージ）**：
```
content: "[2026-03-18T01:09:46.000Z] I ordered it on accident."
```

**assistant role（セラーメッセージ）**：
```
content: "[2026-03-13T08:51:05.000Z] Hello Michaela Kuchařová,
Thank you for your purchase!
The item will be shipped by Mar 23 (Japan time)..."
```

**system role（イベント）**：
```
content: "event: [2026-03-13T08:20:57.000Z] purchase_completed"
content: "event: [2026-04-02T14:32:46.000Z] return_request;reason=doesnt_fit"
```

---

## 📋 event enum 完全リスト（`SUMMARY_PROMT.csv` / `quy_doi_type_chat.csv` 由来）

### AUCTION / Offer / Order 系

| event code | 日本語通知 |
|-----------|---------|
| `auction_won` | AUCTION（落札） |
| `best_offer_created` | OfferOrder（オファー成立） |
| `purchase_completed` | Order（注文完了） |
| `best_offer_accepted` | OfferAccepted（オファー承認） |

### Dispute 系（異議申立て）

| event code | 詳細 |
|-----------|-----|
| `dispute_open;reason=fraud` | FRAUD |
| `dispute_open;reason=buyer_did_not_receive` | ITEM_NOT_RECEIVED（未着） |
| `dispute_open;reason=transaction_issue` | TRANSACTION_ISSUE |
| `dispute_open;reason=unrecognized_transaction` | 取引不認識 |
| `dispute_open;reason=buyer_transaction_issue` | 取引トラブル |
| `dispute_open;reason=item_not_as_described` | 商品説明不一致 |
| `dispute_open;reason=transaction_cancelled` | 取引キャンセル |
| `dispute_closed` | Dispute終了 |

### OrderCancelRequest 系（キャンセルリクエスト）

| event code | 理由 |
|-----------|------|
| `cancel_request;reason=found_better_price` | 他で安く見つけた |
| `cancel_request;reason=placed_by_mistake` | 注文ミス |
| `cancel_request;reason=unknown` | 理由不明 |
| `cancel_request;reason=wont_arrive_on_time` | 間に合わない |
| `cancel_request;reason=wrong_payment_information` | 支払い情報間違い |
| `cancel_request;reason=wrong_shipping_address` | 住所間違い |
| `cancel_request;reason=wrong_shipping_method` | 配送方法間違い |
| `cancel_request_closed` | キャンセル終了 |

### ReturnRequest 系（返品リクエスト）

| event code | 理由 |
|-----------|------|
| `return_request;reason=arrived_damaged` | 破損到着 |
| `return_request;reason=changed_mind` | 気が変わった |
| `return_request;reason=didnt_like_item` | 気に入らなかった |
| `return_request;reason=doesnt_fit` | サイズ合わず |
| `return_request;reason=doesnt_match_description` | 説明と違う |
| `return_request;reason=defective` | 不良品 |
| `return_request;reason=missing_parts` | 部品欠品 |
| `return_request;reason=ordered_by_mistake` | 誤注文 |
| `return_request;reason=wrong_item` | 違う商品が届いた |
| `return_request;status=item_shipped_by_buyer` | バイヤー返送済み |
| `return_request;status=item_delivered_to_seller` | 返送品到着済み |
| `return_request_closed` | 返品終了 |

### ItemNotReceived 系（未着リクエスト）

| event code | 意味 |
|-----------|------|
| `item_not_received;reason=buyer_did_not_receive` | バイヤー未受領 |
| `item_not_received_closed` | 未着終了 |

### ケース

| event code | 意味 |
|-----------|------|
| `case_closed` | ケース終了 |

---

## 🔄 typeChat → event 変換ルール（`quy_doi_type_chat.csv` 由来）

BayChat DB内部の typeChat フィールドを eventコードに変換するマッピング：

| typeChat（DB） | 変換後 event | 備考 |
|--------------|-----------|------|
| AUCTION | `event: auction_won` | — |
| OfferOrder | `event: best_offer_created` | — |
| Order | `event: purchase_completed` | — |
| OfferAccepted | `event: best_offer_accepted` | — |
| Trouble | （trouble別変換） | 下表 |
| **Task** | **削除** | AIに渡さない |
| **eBay** | **削除** | AIに渡さない |

---

## 🌐 影響範囲

### 直接影響する要素
- AIが現在の状況を把握する情報源
- 「未解決の問題」と「解決済みの問題」の区別
- セラーの過去の発言との整合性（復唱禁止との関係）

### 間接影響する要素
- トークン消費の大半を占める（~45%）
- 長期顧客との会話が肥大化するとトークン上限に達するリスク
- 自動メッセージ（フィードバック催促・発送通知等）がassistantとして渡る

### 副作用のリスク
- **自動メッセージの混入**：セラーが手動で書いたメッセージと、BayChat自動メッセージの区別がつかない
- **歴史の切り捨て**：古いメッセージが落ちた場合、AIが文脈を見誤る（Q4）

---

## ⚠️ 未解決の論点

| # | 論点 | 重要度 |
|---|-----|------|
| **Q4** | チャット履歴の件数上限（全件？直近N件？トークン制限？） | 🔴 高 |
| — | 自動メッセージとセラー手動メッセージをAIが区別できているか | 🔴 高 |
| — | `Task` / `eBay` typeChatを削除する理由・タイミング | 🟡 中 |
| — | event発生時刻とbuyer/sellerメッセージ時刻の前後関係処理 | 🟡 中 |

---

## 🤝 Cowatech合意事項

| 項目 | 合意内容 | 合意日 | 根拠 |
|------|--------|------|------|
| role構造 | user/assistant/system の3種 | プロジェクト初期 | `SUMMARY_PROMT.csv` |
| timing形式 | ISO 8601 UTC | プロジェクト初期 | `gpt_api_payload.txt` |
| event prefix | `event:` で開始 | プロジェクト初期 | 同上 |
| typeChat除外 | `Task` / `eBay` は削除 | プロジェクト初期 | `quy_doi_type_chat.csv` |

---

## 📚 関連ドキュメント

| ドキュメント | 役割 |
|----------|------|
| `gpt_api_payload.txt` | 本番実装の実データ |
| `SUMMARY_PROMT.csv` | role・event仕様書 |
| `quy_doi_type_chat.csv` | typeChat→event変換ルール |
| `Quy_doi_chat.csv` | 簡潔版変換表 |
| `04_conditional_logic.md` | event enum分岐一覧 |
| `09_open_questions.md` | Q4詳細 |
