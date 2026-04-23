# [N+3] OUTPUT_FORMAT

**何のため**：AI出力をJSON形式（日本語訳＋バイヤー言語の2フィールド）に厳格固定
**管理者**：Cowatech（出力フィールド追加時のみ変更）

## 実物コード（プロンプト側）

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

## API側の response_format（二重ガード）

```json
{
  "type": "json_schema",
  "name": "multi_language_reply",
  "strict": true,
  "schema": {
    "type": "object",
    "properties": {
      "jpnLanguage": { "type": "string", "description": "Answer in Japanese language" },
      "buyerLanguage": { "type": "string", "description": "Answer in English language" }
    },
    "required": ["jpnLanguage", "buyerLanguage"],
    "additionalProperties": false
  }
}
```
