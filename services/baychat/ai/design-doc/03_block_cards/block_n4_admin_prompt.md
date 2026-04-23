# [N+4] admin_prompt ⭐

**何のため**：CS品質・トーン・会話の中身を決める中核。挨拶・署名制御（2026-04-22以降）もここで行う
**管理者**：Reffort（社長がadmin画面で直接編集・即反映）

## プレースホルダ

| プレースホルダ | 置換元 |
|--------------|--------|
| `{sellerSetting}` | UI「補足情報」欄 |
| `{toneSetting}` | UI「トーン」プルダウン |
| `{buyerAccountEbay}` | UI「TO（受取人）」プルダウン（ID / 氏名 / 担当者名 / なし） |
| `{sellerAccountEbay}` | UI「FROM（送信者）」プルダウン（ID / 氏名 / 担当者名 / なし） |

## 実物コード（バージョン別）

- **本番稼働中**：[`../../prompt_admin_v2.4.md`](../../prompt_admin_v2.4.md)
- **次期ドラフト**：[`../../prompt_admin_v2.6.md`](../../prompt_admin_v2.6.md)（社長がadmin画面にアップロード待ち）
- **admin画面アップロード用JSON**：[`../../prompt_admin_v2.6.json`](../../prompt_admin_v2.6.json)
