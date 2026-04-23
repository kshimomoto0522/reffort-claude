# 09. 未解決論点集約

> ✅ **v0.2 完成版**
> このファイルの役割：**AI Replyの仕様に関する未解決論点** を一箇所に集約。Cowatechに質問する際のパッケージとしても使える。

---

## 🎯 論点の分類基準

| 重要度 | 意味 | 対応 |
|-------|-----|------|
| 🔴 **高** | 品質・機能・運用に直接影響 | 優先的に解決 |
| 🟡 **中** | 将来の運用に影響 | 計画的に解決 |
| 🟢 **低** | 改善余地 | 余裕のあるタイミングで |

---

## 🔴 現在進行中の論点

（現時点で🔴高優先度の進行中論点はなし。Q1/Q3は2026-04-22に解決済み → 下部の✅解決済みセクション参照）

---

## 🟡 優先度見直し済み（2026-04-20 夜）：今は聞かない論点

以下は吟味の結果、「今の作業の進行を阻む穴ではない」と判断したため Cowatech への質問を保留。
設計図完備の前提で、必要になったタイミングで個別に確認する。

- **Q4**：FORCED_TEMPLATE除去完了後のテスト課題時に再考
- **Q5**：要約モード実装着手時に再考
- **Q6**：FORCED_TEMPLATE除去・v2.5本番反映が完了してから再開
- **Q7**：「whoPaysShipping 欠損対応」を別案件として切り出し
- **Q9**：CSV移行計画（08）の3か月ロードマップ内で確認

---

### Q4：チャット履歴の件数・トークン上限

**論点**：チャット履歴が肥大化した場合（長期顧客・複雑ケース）、どう切り詰められているか？

**確認したい点**：
- 全件渡す？
- 直近N件のみ？
- トークン数でリミット？
- 優先順位（古いイベント優先？新しい会話優先？）

**影響**：古い文脈の欠落でAIが文脈を誤読するリスク

**次のアクション**：Cowatechに確認

**関連ドキュメント**：
- `block_chat_history.md`
- `04_conditional_logic.md`

---

### Q5：multi_language_reply schema名の参照有無

**論点**：response_format の `name: "multi_language_reply"` を BayChat後処理が参照しているか？

**確認したい点**：
- 参照している場合：変更時にBayChat側の破壊的変更
- 参照していない場合：schema名を自由に変更可能

**影響**：要約モード実装時に別schema名が必要 → BayChat後処理への影響範囲

**次のアクション**：Cowatechに確認

**関連ドキュメント**：
- `block_n3_output_format.md`
- `15_summary_mode.md`

---

### Q6：Gemini 2.5 Flash実装ロードマップ

**論点**：2026-03-19に次期採用決定済みだが、Cowatech側のGoogle AI API実装進捗が未確認。

**確認したい点**：
- 実装完了見込み時期
- 実装工数
- 並行稼働期間（OpenAI → Gemini 切り替え時のロールバック保険）
- フェイルオーバー戦略

**影響**：速度・コスト・品質すべてで優位なので、早期切替が望ましい

**次のアクション**：Cowatechに確認

**関連ドキュメント**：
- `11_model_selection.md`
- `services/baychat/ai/CLAUDE.md`（モデル選定結論）

---

### Q7：`whoPaysShipping: "No data available to respond."` の原因

**論点**：本番ペイロードで `whoPaysShipping` が `"No data available to respond."` となっている。AIが送料責任を誤回答するリスク。

**確認したい点**：
- eBay APIで取れるフィールドか？
- 取れる場合、なぜ欠損しているのか？
- 取れない場合、`Item.ShippingCostPaidByOption` から導出すべきか？

**次のアクション**：Cowatechに確認＋eBay APIドキュメント確認

**関連ドキュメント**：
- `block_00_item_info.md`
- `12_ebay_api_integration.md`

---

### Q8：自動メッセージとセラー手動メッセージの区別 ✅ 解決済み

**論点**：本番チャット履歴で、セラーの手動返信とBayChat自動メッセージが両方 `assistant` role で入っている。AIがセラーの本当の意図を誤読するリスク。

**解決**：`services/baychat/ai/CLAUDE.md` に「本番ではセラー自動メッセージはAIに渡らない仕組み（Cowatech確認済み）」と記載あり。設計図（`block_chat_history.md`）にも反映済み。

**根拠**：`services/baychat/ai/CLAUDE.md` のテストデータ取得状況セクション：
> ⚠️ ただしステージング環境のデータ：自動メッセージ（セラー側）が含まれており正確なテスト不可
> 本番ではセラーの自動メッセージはAIに渡らない仕組み（Cowatech確認済み）

**ステータス**：Cowatechに追加確認不要

**関連ドキュメント**：
- `block_chat_history.md`
- `10_api_testing.md`
- `services/baychat/ai/CLAUDE.md`

---

### Q9：CSV廃止がCowatech実装に与える影響

**論点**：`cowatech_payloads/spec_sheets/` のCSVへのリンクや参照が Cowatechのコード・ドキュメントに埋まっている可能性。勝手に移動すると依存が壊れるリスク。

**確認したい点**：
- CSV参照コードの存在
- 参考資料のまま維持が必要か、実装依存か
- 再整理の合意タイミング

**次のアクション**：Cowatechに確認（移行計画の前に）

**関連ドキュメント**：
- `08_migration_plan.md`

---

## 🟡 中優先度の論点（11件）

### Q10：BASE_PROMPT の単純版 vs 詳細版の正式化

`promt_spec_48665.csv` に詳細版が残っているが、本番は単純版を使用。どちらがマスターか明確化したい。

---

### Q11：description_guide の "sreen" typo 修正

原文に `{{User input in sreen}}` というtypo（本来は "screen"）。仕様書と本番コード両方で修正が必要。

---

### Q12：FORCED_TEMPLATE のtone別固定値

friendly版・apologetic版のサンプル値（`rioxxrinaxjapan`, `kapital_japan` 等）が固定値で仕様書に書かれている。本来UI値で動的置換されるはずだが、仕様書のtypo or 実装時置換漏れのリスク。

---

### Q13：`<Break line here>` 記述の仕様書と本番の齟齬

`SUMMARY_PROMT.csv` polite版には `<Break line here>` 記述がないが、本番実装 `gpt_api_payload.txt` にはある。どちらが正か。

---

### Q14：`{greeting}` の怒り判定をAIに任せる信頼性

apologetic版の `{greeting}` は AIが怒り判定で `Sincerely` or `Kind regards` を選ぶ。信頼性を検証するテストが未実施。

---

### Q15：返品・Dispute系event時の特別処理

クレーム対応の品質に直結。現状は汎用プロンプトで対応しているが、eventカテゴリ別の専用プロンプトを用意すべきか。

---

### Q16：プロンプトキャッシュの検討

現状 `prompt_cache_key: null`。OpenAI Prompt Caching を使えばコスト削減可能。Gemini切替前の暫定対応として検討余地。

---

### Q17：`Item.Description`（商品説明）を[0]に含めるか

バイヤーの商品詳細質問への回答精度向上が期待できる。ただしトークン増加のトレードオフ。

---

### Q18：descriptionフィールドdescriptionが英語で書かれている件

response_format schema の description フィールドが英語。日本語プロンプトとの一貫性が気になる。

---

### Q19：admin画面に複数バージョン履歴を保存できるか

即ロールバック用。新バージョンで問題が出たとき、1クリックで旧版に戻せるUIが欲しい。

---

### Q20：eBayポリシー改定時の BASE_PROMPT 更新プロセス

誰が監視・反映するか。現状は非明文化。

---

## 🟢 低優先度の論点（4件）

### Q21：要約モードの料金プラン
AI Replyオプションに含めるか、別オプションか。

### Q22：新トーン追加時の運用フロー
casual等の4番目のトーンを追加するときの手順（UI・admin_prompt・FORCED_TEMPLATE同時更新）。

### Q23：並列テスト実行時のコスト爆発防止
テストケース×モデル×プロンプト版の組み合わせが大きくなるとコストが爆発する。上限設定のルール。

### Q24：画像URLをAIに渡す将来構想
Vision対応モデル（GPT-4o、Gemini 1.5 Pro）で画像解析。

---

## 📮 Cowatechへの質問パッケージ（草案）

設計図完成後、以下を**一括でCowatechに送る**：

```markdown
## BayChat AI Reply 統合設計図 v0.2 のレビュー依頼

設計図（下記URL）をご確認いただき、以下の高優先度論点（Q1〜Q9）への回答をお願いします。

【設計図リポジトリ】
https://github.com/kshimomoto0522/reffort-claude/tree/main/baychat-ai/design-doc

【高優先度論点】
- ~~Q1：FORCED_TEMPLATE除去時のTO/FROM注入経路（案A/B/C）~~ → ✅ 2026-04-22 解決済み
- ~~Q3：description・TO/FROMの「空/なし」判定ロジック~~ → ✅ 2026-04-22 TO/FROM側は解決。description側は残課題
- Q4：チャット履歴の件数・トークン上限
- Q5：multi_language_reply schema名の参照有無
- Q6：Gemini 2.5 Flash実装ロードマップ
- Q7：whoPaysShipping欠損の原因
- Q8：自動メッセージ/手動返信の区別ロジック
- Q9：既存CSVのコード依存の有無

【詳細】
各論点の詳細は `09_open_questions.md` をご参照ください。

お手数をおかけしますが、よろしくお願いします。
```

---

## 🔄 このドキュメントの運用

- 新しい論点が生まれたら即追加
- 解決した論点は「✅ 解決済み」セクションに移動（次セクション）
- 解決の根拠（Slackログ・テスト結果等）を必ず記録

---

## ✅ 解決済み論点（参考）

### 🆕 Q1：FORCED_TEMPLATE除去時のTO/FROM値の代替注入経路（2026-04-22 解決）
- **回答**：admin_prompt内に `{buyerAccountEbay}` / `{sellerAccountEbay}` プレースホルダを追加し、UI signature/receiver 選択値で動的置換する方式で決着
- **根拠**：Cowatech stg+prd両環境に実装反映済み（2026-04-22 23:58）
- **出典**：Slack thread_ts `1776427836.602699` クエットさん返信「対応してstgとprdに反映済みです」
- **関連変更**：
  - FORCED_TEMPLATEブロック生成ロジック削除
  - admin_prompt内にプレースホルダ注入機構を追加
  - Reffort側：`prompt_admin_v2.6.md` 命名統一（2026-04-23）
- **次のアクション**：社長が v2.6 を admin画面にアップロードすれば即 FORCED_TEMPLATE除去＋新プレースホルダ運用が稼働

### 🆕 Q3：TO/FROM「なし」選択時の挙動（2026-04-22 解決）
- **回答**：UI選択値（ID / 氏名 / 担当者名 / なし）がそのまま動的置換される。「なし」選択時は `{buyerAccountEbay}` / `{sellerAccountEbay}` が空文字で置換される
- **挙動**：admin_prompt v2.6 の「GREETING & SIGNATURE POLICY → WHEN A PLACEHOLDER IS EMPTY」ルールにより、AIが挨拶・署名を省略する
- **根拠**：Slack thread_ts `1776427836.602699` クエットさん返信「ご認識通りです」（2026-04-22 23:13）
- **出典**：同上

### Q2：`{sellerSetting}`/`{toneSetting}` の置換処理の場所
- **回答**：BayChat側で置換（2026-03-21）
- **根拠**：Slack履歴・CLAUDE.md記載
- **出典**：`services/baychat/ai/CLAUDE.md`

### descriptionが空のとき [N+1] ブロックが注入されないか
- **回答**：本番ペイロード実例で欠落していたため、注入されないと推定
- **根拠**：`gpt_api_payload.txt`
- **ステータス**：実装確認要（Q3系列・未決部分）

### AI出力の`buyerLanguage`をBayChat側で後処理しているか
- **回答**：タブ表示に使用（日本語訳・返信で2タブ分ける）
- **根拠**：`baychat_api_payload.txt` の `language: "buyerLanguage"` フィールドから推定

---

## 📚 関連ドキュメント

全ブロックカード、全番号付きファイルにクロスリファレンスされる横断ドキュメント。
