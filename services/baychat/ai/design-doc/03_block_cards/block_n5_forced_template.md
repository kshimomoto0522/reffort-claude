# [N+5] FORCED_TEMPLATE 🔴 廃止済み

**何のため**（当時）：AIの出力を「Hello {buyer_name}, ... Best regards, {seller_name}」形式に強制
**ステータス**：**2026-04-22 廃止**（Cowatech stg+prd両環境で削除完了）
**移管先**：挨拶・署名の制御は [N+4] admin_prompt の GREETING & SIGNATURE POLICY セクションに一元化

## 廃止前の実物コード（参考・polite版）

```text
The response MUST ABSOLUTELY adhere to the following format.
  Do not add explanations, markdown, or extra text.

  Hello {buyer_name},
  {output_content}

  Best regards,
   {seller_name}

  Replace the placeholders with actual values.
  seller_name: {{user select in sreen}}
  buyer_name: {{user select in sreen}}

  ABSOLUTELY: Always ensure that the output of the .jpn Language
  and the buyer Language adhere to the above format.
```

## 廃止理由

テストで除去により品質スコア +2.0pt 改善を確認（admin_prompt側のほうが状況判断で柔軟に挨拶・署名を扱える）。
現在は `{buyerAccountEbay}` / `{sellerAccountEbay}` を admin_prompt に注入する方式で動作。
