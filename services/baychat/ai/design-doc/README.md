# BayChat AI Reply プロンプト構成

AI Reply（バイヤー返信文の自動生成）でAIに送られるプロンプトは、以下の7ブロックで構成される。

| 順序 | ブロック | 何のため | 管理者 |
|------|---------|---------|--------|
| [0] | [商品情報JSON](03_block_cards/block_00_item_info.md) | どの商品についてのやり取りかをAIに教える | BayChat（eBay APIから自動取得） |
| [1..N] | [チャット履歴](03_block_cards/block_chat_history.md) | これまでのバイヤーとのやり取り・イベントをAIに渡す | BayChat（DBから自動取得） |
| [N+1] | [description_guide](03_block_cards/block_n1_description_guide.md) | セラーが補足情報を入力した時のAIへの指示 | Cowatech |
| [N+2] | [BASE_PROMPT](03_block_cards/block_n2_base_prompt.md) | eBayコンプライアンス違反行為の禁止ルール | Cowatech |
| [N+3] | [OUTPUT_FORMAT](03_block_cards/block_n3_output_format.md) | AI出力をJSON（日本語訳＋バイヤー言語の2フィールド）に強制 | Cowatech |
| [N+4] | [admin_prompt](03_block_cards/block_n4_admin_prompt.md) ⭐ | CS品質・トーン・会話の中身。挨拶・署名の制御も | Reffort（社長がadmin画面で直接編集） |
| [N+5] | [FORCED_TEMPLATE](03_block_cards/block_n5_forced_template.md) | 🔴 廃止済み（2026-04-22）。挨拶・署名制御は[N+4]に移管 | — |
