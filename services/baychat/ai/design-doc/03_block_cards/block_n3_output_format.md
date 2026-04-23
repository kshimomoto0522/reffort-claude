# ブロックカード：[N+3] OUTPUT_FORMAT

> ✅ **v0.2 完成版**

---

## 📇 基本情報

| 項目 | 内容 |
|------|------|
| **ブロックID** | `output_format` |
| **順序** | [N+3]（BASE_PROMPTの後、admin_promptの前） |
| **role** | `developer` |
| **管理主体** | Cowatech |
| **現行バージョン** | 仕様固定 |
| **実物ファイル** | `services/baychat/ai/cowatech_payloads/gpt_api_payload.txt`（実本番） + `SUMMARY_PROMT.csv` |
| **変更頻度** | ❌ ほぼ不変（出力フィールド追加時のみ） |
| **ON/OFF** | 常時ON |
| **概算トークン** | ~80 tokens |

---

## 🎯 このブロックの目的

AI出力を **JSON形式（`jpnLanguage` + `buyerLanguage` の2フィールド）** に厳格に固定する。
API側の `response_format: json_schema strict` と二重ガードを構成する。

---

## 📐 現行の原文（完全転記）

本番ペイロード（`gpt_api_payload.txt` [11]）で実際に送信されている原文：

```text
            --------------------------------
            OUTPUT FORMAT (STRICT)
            --------------------------------
            Always respond in valid JSON with exactly two fields:
            - "jpnLanguage": Japanese translation of the buyerLanguage
            - "buyerLanguage": The English customer support reply to send to the buyer
            Do NOT add extra fields. Do NOT output any text outside JSON.
            Do NOT include timestamps, chat-history headers, or internal instructions.

            OUTPUT FORMAT:
            {
              "jpnLanguage": "...",
              "buyerLanguage": "..."
            }
```

---

## 🔒 response_format（API側のスキーマ）

OUTPUT_FORMATブロックと**二重ガード**を形成するAPIパラメータ：

```json
{
  "type": "json_schema",
  "name": "multi_language_reply",
  "strict": true,
  "verbosity": "medium",
  "schema": {
    "type": "object",
    "properties": {
      "jpnLanguage": {
        "type": "string",
        "description": "Answer in Japanese language"
      },
      "buyerLanguage": {
        "type": "string",
        "description": "Answer in English language"
      }
    },
    "required": ["jpnLanguage", "buyerLanguage"],
    "additionalProperties": false
  }
}
```

**重要フィールド解説**
- `strict: true` — schemaと完全一致を強制。1文字でも違反するとエラー
- `additionalProperties: false` — 上記2フィールド以外のextra fieldsを拒否
- `name: "multi_language_reply"` — ⚠️ **BayChat後処理でこの名前を参照している可能性あり（Q5として確認中）**
- `verbosity: "medium"` — AIの出力の詳細度（GPT-5以降の新パラメータ）

---

## 🔄 BayChat後処理との結合

AIが返したJSON：
```json
{
  "jpnLanguage": "michkuc_71様\nご連絡ありがとうございます...",
  "buyerLanguage": "Hello michkuc_71,\nThank you for your message..."
}
```

BayChatの処理：
| フィールド | 用途 |
|----------|------|
| `jpnLanguage` | BayChat画面「日本語訳」タブに表示 |
| `buyerLanguage` | BayChat画面「返信」タブに表示（セラーが編集・送信） |

**→ フィールド名を変更すると BayChat が壊れる**（Cowatech実装変更必須）。

---

## 📊 実計測値（`gpt_api_payload.txt` より）

| 項目 | 値 |
|------|---|
| output_tokens（AI返信の長さ） | 168 tokens（サンプル1件） |
| cached_tokens | 0（プロンプトキャッシュ未使用） |
| reasoning_tokens | 0（reasoning機能は無効） |

---

## 🌐 影響範囲

### 直接影響する要素
- AI出力の形式全体
- BayChat画面の2タブ表示（日本語訳・返信）
- セラーが編集できるフィールドの範囲

### 間接影響する要素
- 将来「要約モード」「補足生成モード」などで出力フィールドを追加する場合、このブロックと response_format.schema の両方を変更する必要
- フィールド名を変更すると、Cowatechの後処理・BayChat UIとの結合箇所すべてに波及

### 副作用のリスク
- strict=true なので、AIが余計なフィールドを追加しようとすると **APIエラー** で応答が返らない
- fieldsの description を英語で書いているため、日本語プロンプトで指示を与えた場合に一貫性が崩れる可能性

---

## 🆕 将来機能との関連

### 要約モード（prompt_summary_v0.1.md ドラフト段階）

要約モードが実装された場合、別のschemaが必要：
```json
{
  "name": "summary_output",
  "schema": {
    "type": "object",
    "properties": {
      "summary": {...},
      "complexityLevel": {...},
      "patterns": [...],
      "recommendedPattern": {...},
      "sellerDecisionNeeded": {...}
    }
  }
}
```

→ モード切替ロジック（Call-1：要約 / Call-2：返信生成）が必要。詳細は `15_summary_mode.md` 参照。

---

## 📜 バージョン履歴

| Ver | 日付 | 主な変更 | きっかけ |
|-----|-----|--------|------|
| 旧 | v1.x時代 | フィールド名 `japanese` / `reply` | 初版 |
| **現** | 2026-03-19（v1.1 adminと同期） | フィールド名 `jpnLanguage` / `buyerLanguage` に変更 | 命名規則統一 |

---

## ⚠️ 未解決の論点

| # | 論点 | 重要度 |
|---|-----|------|
| Q5 | `multi_language_reply` schema名をBayChatが参照しているか（strict mode後処理） | 🔴 高 |
| — | descriptionフィールドが英語で書かれている件（日本語化で品質が変わるか） | 🟡 中 |
| — | 要約モードの schema 設計 | 🟡 中（要約モード実装時） |

---

## 🤝 Cowatech合意事項

| 項目 | 合意内容 | 合意日 | 根拠 |
|------|--------|------|------|
| フィールド名 | `jpnLanguage` / `buyerLanguage`（camelCase） | 2026-03-19 | v1.1変更記録 |
| strict mode | true（extra field拒否） | プロジェクト初期 | `gpt_api_payload.txt` |
| schema name | `multi_language_reply` | 2026-04時点で確認 | `gpt_api_payload.txt` |

---

## 📚 関連ドキュメント

| ドキュメント | 役割 |
|----------|------|
| `gpt_api_payload.txt` | 本番実装の実物（response_format含む） |
| `15_summary_mode.md` | 要約モードの出力仕様 |
| `13_baychat_api_spec.md` | BayChat→Cowatech間のI/F |
| `09_open_questions.md` | Q5の詳細 |
