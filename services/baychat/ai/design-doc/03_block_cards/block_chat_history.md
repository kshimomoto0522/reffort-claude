# [1..N] チャット履歴

**何のため**：これまでのバイヤーとのやり取り・発生イベントをAIに渡す（会話の現状把握のため）
**管理者**：BayChat（DBメッセージ・イベントテーブルから自動取得）

## 実物コード（role別の例）

3種類の role を時系列で並べてAIに渡す：

### user role（バイヤーのメッセージ）
```
content: "[2026-03-18T01:09:46.000Z] I ordered it on accident."
```

### assistant role（セラーの返信）
```
content: "[2026-03-13T08:51:05.000Z] Hello Michaela Kuchařová,
Thank you for your purchase!
The item will be shipped by Mar 23 (Japan time)..."
```

### system role（eBayイベント）
```
content: "event: [2026-03-13T08:20:57.000Z] purchase_completed"
content: "event: [2026-04-02T14:32:46.000Z] return_request;reason=doesnt_fit"
```

## event の種類（主なもの）

| event code | 意味 |
|-----------|------|
| `purchase_completed` | 注文完了 |
| `auction_won` | 落札 |
| `best_offer_created` | オファー成立 |
| `best_offer_accepted` | オファー承認 |
| `return_request;reason=xxx` | 返品リクエスト（理由付き） |
| `cancel_request;reason=xxx` | キャンセルリクエスト（理由付き） |
| `item_not_received` | 未着申告 |
| `dispute_opened;type=xxx` | 異議申立て |

※ timing は全て ISO 8601 UTC 形式
※ typeChat が `Task` / `eBay` のものはAIに渡さない（システム内部用）
