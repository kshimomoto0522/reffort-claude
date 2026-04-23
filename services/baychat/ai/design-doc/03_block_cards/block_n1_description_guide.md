# [N+1] description_guide（補足情報ガイド）

**何のため**：セラーが補足情報を入力した時、AIに「そのトーンと補足内容をもとに回答を作れ」と指示する
**管理者**：Cowatech
**条件**：補足情報が空でない場合のみ注入（空ならこのブロックはスキップされる）

## 実物コード

```text
Create questions/answers as requested,
with a '{{Tone}}' tone and the main content being: '{{User input in sreen}}'.
```

## プレースホルダ

| プレースホルダ | 置換元 |
|--------------|--------|
| `{{Tone}}` | UIトーンプルダウン（polite / friendly / apologetic） |
| `{{User input in sreen}}` | UI補足情報欄の入力値 |

※ `sreen` は原文typo（本来は `screen`）だが仕様として固定
