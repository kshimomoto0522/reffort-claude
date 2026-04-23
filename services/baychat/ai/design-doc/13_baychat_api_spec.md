# 13. BayChat API 仕様（BayChat → Cowatech インターフェース）

> ✅ **v0.2 完成版**
> このファイルの役割：**BayChatフロントエンドからCowatechバックエンドへのリクエスト仕様** を定義。ペイロード組立の入り口。

---

## 🎯 概要

BayChat画面でセラーが「AIで返信を生成」ボタンを押したとき、BayChatフロントエンドからCowatechバックエンドへ送信されるリクエスト構造。これが [1] 商品情報JSON 〜 [N+5] FORCED_TEMPLATE への組立の入力となる。

実物：`services/baychat/ai/cowatech_payloads/baychat_api_payload.txt`

---

## 📐 リクエスト構造（完全仕様）

```json
{
  "tonePrompt": "polite",
  "histories": [],
  "description": "",
  "sellerId": "9ad58d8d-ee75-4e28-9bee-8dd7e0d3bf30",
  "buyerId": "19901cfc-dd0a-4364-8d9b-43abddb5986a",
  "itemId": "6fb330e1-8303-46f4-8e57-28062334a02b",
  "language": "buyerLanguage",
  "signature": "id",
  "receiver": "id"
}
```

---

## 📋 フィールド完全仕様

| フィールド | 型 | 必須 | 意味 | 実例 |
|----------|---|-----|------|-----|
| `tonePrompt` | string enum | ✅ | トーン指定 | `polite` / `friendly` / `apologetic` |
| `histories` | array | ✅ | チャット履歴（**または空配列**） | `[]` or `[{...}, ...]` |
| `description` | string | ✅ | 補足情報（セラー意図） | `""` or `"Be concise"` |
| `sellerId` | string (UUID) | ✅ | BayChat内部のセラーID | UUID v4 |
| `buyerId` | string (UUID) | ✅ | BayChat内部のバイヤーID | UUID v4 |
| `itemId` | string (UUID) | ✅ | BayChat内部の商品ID | UUID v4 |
| `language` | string enum | ✅ | 出力言語モード | `buyerLanguage` / `english` |
| `signature` | string enum | ✅ | FROM署名のソース | `id` / `name` / `staff` / `none` |
| `receiver` | string enum | ✅ | TO宛先のソース | `id` / `name` / `none` |

---

## 🔀 各フィールドの役割

### `tonePrompt`
- UIトーンプルダウンの選択値
- BayChatが [N+4] admin_prompt の `{toneSetting}` に注入
- BayChatが [N+5] FORCED_TEMPLATE のバリエーション選択に使用
- BayChatが [N+1] description_guide の `{{Tone}}` に注入（補足情報あるとき）

### `histories`
- BayChat DB `view_chat_ebay` から取得したチャット履歴
- 空配列の場合：新規会話（AIはSTAGE 1「FIRST MESSAGE」と判定）
- 要素構造：詳細は `block_chat_history.md` 参照

### `description`
- UI「補足情報」欄にセラーが入力したテキスト
- 空文字の場合：[N+1] description_guide ブロックをスキップ（推定）
- 空でない場合：admin_prompt の `{sellerSetting}` に注入＋ [N+1] に `{{User input in sreen}}` として注入

### `sellerId` / `buyerId` / `itemId`
- BayChat内部UUID
- Cowatech側でDB参照してeBayのItemID・userID等を取得
- eBay API呼び出しに使用

### `language`
- `buyerLanguage`：バイヤーの推定言語で返信を生成
- `english`：英語固定で返信を生成
- 既定値は `buyerLanguage`

### `signature`（FROM）
- `id`：セラーのeBayユーザーID（例：`rioxxrinaxjapan`）
- `name`：セラーの氏名
- `staff`：担当者名
- `none`：署名なし

### `receiver`（TO）
- `id`：バイヤーのeBayユーザーID（例：`michkuc_71`）
- `name`：バイヤーの氏名
- `none`：宛名なし

---

## 🔄 BayChat → Cowatech → OpenAI の変換フロー

```
【BayChat フロントエンド】
   セラーが「AIで返信を生成」ボタン押下
      ↓
   BayChatリクエスト作成
   {
     tonePrompt, histories, description,
     sellerId, buyerId, itemId,
     language, signature, receiver
   }
      ↓
【Cowatech バックエンド（BayChat API）】
   1. sellerId → eBayセラーID解決
   2. buyerId → eBayバイヤーID解決
   3. itemId → eBay ItemID解決 → eBay API GetItem呼び出し
   4. signature / receiver 値をテンプレプレースホルダに用意
      ({seller_name} / {buyer_name})
   5. histories → OpenAI messages形式に変換
   6. 8ブロック構造で OpenAI messages 組立
   7. OpenAI API呼び出し（temperature=0.2, schema strict）
      ↓
【OpenAI API】
   AI生成 → JSON返却 ({jpnLanguage, buyerLanguage})
      ↓
【Cowatech バックエンド】
   後処理（もしあれば）→ BayChatへ返却
      ↓
【BayChat フロントエンド】
   2タブで表示（日本語訳 / 英語返信）
```

---

## 🔧 Cowatech実装の責任範囲

| 処理 | 責任 |
|------|------|
| BayChatリクエストの受信 | Cowatech |
| DBからのID解決（seller/buyer/item） | Cowatech |
| eBay API GetItem呼び出し | Cowatech |
| OpenAI messages 組立 | Cowatech |
| `{sellerSetting}` / `{toneSetting}` 置換 | Cowatech |
| `{buyer_name}` / `{seller_name}` 置換 | Cowatech |
| `[N+1]` description_guide のON/OFF判定 | Cowatech |
| OpenAI API呼び出し | Cowatech |
| レスポンス後処理 | Cowatech |

**→ BayChatフロントエンドはリクエスト送信・レスポンス表示のみ。** プロンプト組立・API呼び出しの本体は Cowatechバックエンド側。

---

## ⚠️ 未解決の論点

| # | 論点 | 重要度 |
|---|-----|------|
| **Q1** | `signature` / `receiver` が `none` のときの処理 | 🔴 高 |
| Q3 | `description` が空のときの判定（空文字？trim後？） | 🔴 高 |
| Q4 | `histories` の件数上限（クライアント側で絞る？サーバー側で絞る？） | 🔴 高 |
| — | `language: "english"` 指定時の挙動（本番で使われているか） | 🟡 中 |
| — | エラー時のレスポンス構造（rate limit、API error等） | 🟡 中 |
| — | 非同期処理の有無（リクエスト→処理中→結果取得のフロー） | 🟡 中 |

---

## 🤝 Cowatech合意事項

| 項目 | 合意内容 | 合意日 | 根拠 |
|------|--------|------|------|
| リクエスト構造 | 上記9フィールド | 2026-04時点 | `baychat_api_payload.txt` |
| ID形式 | UUID v4（BayChat内部ID） | プロジェクト初期 | 同上 |

---

## 📚 関連ドキュメント

| ドキュメント | 役割 |
|----------|------|
| `baychat_api_payload.txt` | 本番リクエスト実例 |
| `gpt_api_payload.txt` | Cowatech→OpenAI送信実例 |
| `00_overall_flow.md` | 全体フロー図 |
| `04_conditional_logic.md` | 条件分岐の詳細 |
| `09_open_questions.md` | Q1/Q3/Q4 詳細 |
