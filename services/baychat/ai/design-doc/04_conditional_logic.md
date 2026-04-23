# 04. 条件分岐表（完全版）

> ✅ **v0.3 更新版（2026-04-23）**
> このファイルの役割：**「どのブロックが、どの条件で、ON/OFFされるか」「どの値が、どの条件で、何に置換されるか」** を一覧で見える化する。
> 🆕 **2026-04-23 更新**：Cowatech prd反映（2026-04-22 23:58）を反映。FORCED_TEMPLATE廃止・プレースホルダ命名を `{buyerAccountEbay}/{sellerAccountEbay}` に統一。

---

## 🚦 ブロック単位の条件分岐

| ブロック | ON/OFF判定 | 判定条件 | 判定ロジック | 根拠 |
|---------|----------|---------|----------|------|
| [0] 商品情報JSON | **常時ON** | — | ItemIDから eBay API `GetItem` で取得 | `gpt_api_payload.txt` |
| [1..N] チャット履歴 | **常時ON（履歴あれば）** | 履歴1件以上 | DB の view_chat_ebay から抽出 | 同上 |
| [N+1] 補足情報ガイド | **条件付きON** | descriptionが「空でない」 | 🔴 判定詳細はCowatech確認待ち（Q3） | 本番実例で欠落→推測 |
| [N+2] BASE_PROMPT | **常時ON** | — | 固定テキスト | `gpt_api_payload.txt` |
| [N+3] OUTPUT_FORMAT | **常時ON** | — | 固定テキスト | 同上 |
| [N+4] admin_prompt | **常時ON** | — | admin画面登録テキスト（`{sellerSetting}` / `{toneSetting}` / 🆕`{buyerAccountEbay}` / 🆕`{sellerAccountEbay}` 置換後）を注入 | 同上＋2026-04-22 prd反映 |
| ~~[N+5] FORCED_TEMPLATE~~ | **❌ 廃止済み（2026-04-22）** | — | Cowatech stg+prdでブロック生成ロジック削除 | Slack thread_ts `1776427836.602699` |

---

## 🎚️ トーン選択による分岐

### 現行（2026-04-22以降）：admin_prompt 内で制御

トーン選択値 `{toneSetting}` はadmin_promptのINPUTSセクションに注入され、
TONE GUIDELINES / GREETING & SIGNATURE POLICY セクションがAIに挙動を指示する。

| トーン値 | 挨拶 | 結句 | 特記事項 |
|---------|------|------|--------|
| `polite` | `Hello {buyerAccountEbay},` | `Best regards,\n{sellerAccountEbay}` | — |
| `friendly` | `Hi {buyerAccountEbay},` | `Best,\n{sellerAccountEbay}` | カジュアル調 |
| `apologetic` | `Hello {buyerAccountEbay},` | 怒り判定で `Sincerely,` / `Kind regards,` → `\n{sellerAccountEbay}` | AI判定（admin_prompt内指示） |

### 廃止済み（〜2026-04-22）：[N+5] FORCED_TEMPLATE での強制
- tone別3バリエーション（polite/friendly/apologetic）を `SUMMARY_PROMT.csv` から注入
- `{buyer_name}` / `{seller_name}` / `{output_content}` / `{greeting}` の4プレースホルダで制御
- 詳細は `03_block_cards/block_n5_forced_template.md` を参照

---

## 🔁 値の動的置換マトリクス（2026-04-22以降）

### BayChat が置換（ペイロード組立時）

| プレースホルダ | 注入先ブロック | 置換元 | 空のときの挙動 | Cowatech確認状態 |
|-------------|-------------|-------|------------|---------------|
| `{sellerSetting}` | [N+4] admin_prompt（2箇所） | UI補足情報 | 空文字連結。admin_prompt v2.4で空許容ロジックあり | ✅ 確認済み |
| `{toneSetting}` | [N+4] admin_prompt（1箇所・INPUTSセクション） | UIトーンプルダウン | 必須UIのため空にならない | ✅ 確認済み |
| 🆕 `{buyerAccountEbay}` | [N+4] admin_prompt（GREETING & SIGNATURE POLICY + INPUTS + FINAL CHECK） | UI「TO（受取人）」プルダウン（ID / 氏名 / 担当者名 / **なし**） | 「なし」選択時は空文字で置換。admin_prompt「WHEN A PLACEHOLDER IS EMPTY」ルールで挨拶省略 | ✅ **2026-04-22 prd反映済み** |
| 🆕 `{sellerAccountEbay}` | [N+4] admin_prompt（同上） | UI「FROM（送信者）」プルダウン（ID / 氏名 / 担当者名 / **なし**） | 同上（署名省略） | ✅ **2026-04-22 prd反映済み** |
| `{{Tone}}` | [N+1] description_guide | UIトーン | 必須UIのため空にならない | 🟡 要確認 |
| `{{User input in sreen}}` | [N+1] description_guide | UI補足情報 | 空ならブロック全体スキップ想定 | 🔴 未確認 |
| ~~`{buyer_name}`~~ | ~~[N+5] FORCED_TEMPLATE~~ | — | ❌ **2026-04-22 廃止**：`{buyerAccountEbay}` に統一 | — |
| ~~`{seller_name}`~~ | ~~[N+5] FORCED_TEMPLATE~~ | — | ❌ **2026-04-22 廃止**：`{sellerAccountEbay}` に統一 | — |

### AI が置換（生成時）

| プレースホルダ | 注入先ブロック | 置換元 |
|-------------|-------------|-------|
| ~~`{output_content}`~~ | ~~[N+5] FORCED_TEMPLATE~~ | ❌ **廃止**：AI出力は jpnLanguage/buyerLanguage フィールドに直接格納 |
| ~~`{greeting}`~~ | ~~[N+5] FORCED_TEMPLATE apologetic版~~ | ❌ **廃止**：admin_prompt TONE GUIDELINES で AI判断を指示 |

---

## 🎯 APIパラメータの分岐

### 固定パラメータ（常時同じ）

| パラメータ | 値 | 意味 |
|---------|---|-----|
| `model` | `gpt-4.1-mini-2025-04-14` | 使用AIモデル |
| `temperature` | `0.2` | 出力安定性（低い=一貫） |
| `top_p` | `1` | ニュークリアスサンプリング |
| `frequency_penalty` | `0` | 頻度ペナルティなし |
| `presence_penalty` | `0` | 存在ペナルティなし |
| `service_tier` | `default` | サービス層 |
| `parallel_tool_calls` | `true` | 並列ツール呼び出し許可 |
| `store` | `true` | リクエスト保存ON |
| `truncation` | `disabled` | 自動切り詰めOFF |
| `tool_choice` | `auto` | ツール自動選択（ただし tools=[]） |
| `tools` | `[]` | ツールなし |

### null パラメータ（未使用・将来拡張用）

| パラメータ | 値 | 本来の用途 |
|---------|---|----------|
| `max_output_tokens` | `null` | 出力トークン上限 |
| `max_tool_calls` | `null` | ツール呼び出し上限 |
| `instructions` | `null` | システム指示 |
| `safety_identifier` | `null` | 安全識別子 |
| `prompt_cache_key` | `null` | プロンプトキャッシュキー |
| `prompt_cache_retention` | `null` | キャッシュ保持期間 |
| `reasoning.effort` | `null` | 推論努力レベル |
| `reasoning.summary` | `null` | 推論サマリ |
| `previous_response_id` | `null` | 前回レスポンスID |
| `user` | `null` | ユーザー識別子 |

### 出力形式（固定）

```json
response_format: {
  "type": "json_schema",
  "name": "multi_language_reply",
  "strict": true,
  "verbosity": "medium",
  "schema": {
    "type": "object",
    "properties": {
      "jpnLanguage": {"type": "string", "description": "Answer in Japanese language"},
      "buyerLanguage": {"type": "string", "description": "Answer in English language"}
    },
    "required": ["jpnLanguage", "buyerLanguage"],
    "additionalProperties": false
  }
}
```

### 課金設定
| パラメータ | 値 |
|---------|---|
| `billing.payer` | `developer` |

---

## 🧩 チャット履歴内の role 分岐

### 基本ルール

| 条件 | role | content形式 |
|------|------|-----------|
| バイヤーのメッセージ | `user` | `[{ISO timestamp}] {buyer's message}` |
| セラーのメッセージ（手動＋自動） | `assistant` | `[{ISO timestamp}] {seller's message}` |
| eBayイベント | `system` | `event: [{ISO timestamp}] {event content}` |

### typeChat（DB内部種別）の変換

| typeChat | 変換先 | 備考 |
|---------|------|------|
| `AUCTION` | `system`: `event: auction_won` | 落札 |
| `OfferOrder` | `system`: `event: best_offer_created` | オファー成立 |
| `Order` | `system`: `event: purchase_completed` | 注文完了 |
| `OfferAccepted` | `system`: `event: best_offer_accepted` | オファー承認 |
| `Trouble` | `system`: `event: (trouble詳細変換)` | 下表 |
| **`Task`** | **削除（AIに渡さない）** | — |
| **`eBay`** | **削除（AIに渡さない）** | — |

### Trouble詳細変換（完全リスト）

**event enum一覧は `block_chat_history.md` を参照**。要点：
- Dispute 8種（fraud / INR / transaction_issue / 他）
- CancelRequest 7種 + closed
- ReturnRequest 9種 + 2 status + closed
- ItemNotReceived 1種 + closed
- Case 1種（closed）

---

## 🔀 将来の条件分岐候補（未実装）

### モード分岐（将来の要約モード実装時）

| モード | プロンプトブロック | 出力schema |
|-------|----------------|----------|
| 返信生成（現行） | BASE+OUTPUT+admin+FORCED_TEMPLATE | `multi_language_reply` |
| 要約（Call-1） | 要約専用プロンプト | `summary_output` |
| 返信生成Call-2（将来） | 要約結果＋パターン選択 | `multi_language_reply` |

---

## 🚨 暗黙の条件分岐（Cowatech確認必要）

v0.2 時点で「暗黙に動作している」と推測される分岐：

| # | 推測される条件分岐 | 影響 | 優先度 | 対応論点 |
|---|-----------------|-----|------|------|
| A | descriptionが空なら [N+1] をスキップ | トークン削減・ロジック簡素化 | 🔴 高 | Q3 |
| B | チャット履歴の件数制限（トークン or 直近N件） | 古い文脈の欠落リスク | 🔴 高 | Q4 |
| ~~C~~ | ~~TO/FROM「なし」選択時の挙動~~ | ✅ **2026-04-22 解決**：UI値が空文字で置換され、admin_promptが挨拶・署名を省略 | — | ~~Q3~~ |
| D | 返品・Dispute系eventがあるときの特別処理 | クレーム対応品質 | 🟡 中 | — |
| E | トークン上限超過時の切り詰めロジック | 長期履歴で発生 | 🟡 中 | — |
| F | `whoPaysShipping: "No data available"` 時の挙動 | 送料誤回答リスク | 🟡 中 | — |
| G | typeChat `Task` / `eBay` を削除する判定タイミング | AI文脈欠落リスク | 🟡 中 | — |

---

## 🔄 このファイルの更新タイミング

- [ ] 新しい条件分岐の追加・変更
- [ ] プレースホルダの追加・変更
- [ ] トーン選択肢の追加（4番目のトーン追加時等）
- [ ] event enum の追加（eBay仕様変更時）
- [ ] APIパラメータの条件分岐追加
- [ ] モード分岐の実装（要約モード等）

**更新時は `05_changelog.md` にも記録する。**
