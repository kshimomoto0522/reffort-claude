# 06. 用語集・FAQ

> ✅ **v0.2 完成版**
> このファイルの役割：**社長・Claude・Cowatechが同じ言葉で議論できる共通辞書**。

---

## 📖 用語集（日英対応）

### AI・プロンプト関連

| 日本語 | 英語 | 意味 |
|-------|------|------|
| ペイロード | payload | AIに送信するデータ全体（messages配列+パラメータ） |
| メッセージ配列 | messages / input | プロンプトブロックとチャット履歴を順番に並べた配列 |
| ブロック | block / message | messages配列の1要素。`role`と`content`を持つ |
| developer role | developer role | 開発者からAIへの指示（最強制力） |
| system role | system role | システムメッセージ（event等） |
| user role | user role | ユーザー（バイヤー）のメッセージ |
| assistant role | assistant role | AI（またはセラー）のメッセージ |
| プレースホルダ | placeholder | `{sellerSetting}` 等の置換対象の変数 |
| 補足情報 | description / seller intent | セラーがUIで入力するAIへの意図指示 |
| トーン | tone | AIの文体（polite / friendly / apologetic） |
| admin prompt | admin prompt | 社長がadmin画面で編集できるプロンプト |
| BASE_PROMPT | BASE_PROMPT | Cowatech管理のeBayコンプライアンス制約 |
| OUTPUT_FORMAT | OUTPUT_FORMAT | JSON形式強制のブロック |
| FORCED_TEMPLATE | FORCED_TEMPLATE | `Hello/Best regards` 形式を強制するブロック |
| description_guide | description guide | 補足情報あるときのAI指示ブロック |

### AIモデル・APIパラメータ

| 日本語 | 英語 | 意味 |
|-------|------|------|
| モデル | model | 使用するAIの種類（GPT-4.1-Mini 等） |
| temperature | temperature | 出力の安定性パラメータ（0.0〜1.0） |
| json_schema strict | json_schema strict | JSON形式を厳密に強制するモード |
| トークン | token | AIが処理する文字の単位（コスト・レイテンシに直結） |
| レイテンシ | latency | AI応答までの時間 |
| ストリーミング | streaming | 文字を逐次表示する技術 |
| service_tier | service_tier | API処理層（default / priority） |
| prompt cache | prompt cache | プロンプトのキャッシュ機能（コスト削減） |
| verbosity | verbosity | GPT-5以降の出力詳細度パラメータ |

### BayChat機能

| 日本語 | 英語 | 意味 |
|-------|------|------|
| AI Reply | AI Reply | AIによる返信自動生成機能 |
| 要約モード | Summary mode | （将来機能）バイヤーメッセージの要約・状況整理 |
| 自動メッセージ | Automated message | 売れた時・発送時等に自動送信されるメッセージ |
| テンプレート | Template | セラーが事前登録する定型文 |
| TO/FROM | TO/FROM | 返信の宛先・署名のプルダウン |
| admin画面 | admin panel | 社長がプロンプトを編集する管理画面 |

### eBay用語

| 日本語 | 英語 | 意味 |
|-------|------|------|
| バイヤー | buyer | eBayで商品を購入する買い手 |
| セラー | seller | eBayで商品を販売している出品者 |
| リスティング | listing | eBayに出品されている商品ページ |
| オファー | offer / best offer | バイヤーからの値下げ交渉 |
| リターンリクエスト | return request | 返品リクエスト |
| ディスピュート | dispute | バイヤーからの異議申立て |
| ケース | case | eBay上のトラブル案件 |
| 未着リクエスト | item not received (INR) | 商品未着の申立て |
| バリエーション | variation | サイズ・色等の商品バリエーション |
| SKU | SKU | 在庫管理単位のID |
| フィードバック | feedback | バイヤー・セラー相互評価 |

### イベントタイプ（event enum）

| コード | 意味 |
|-------|-----|
| `auction_won` | オークション落札 |
| `best_offer_created` | オファー提示 |
| `best_offer_accepted` | オファー承認 |
| `purchase_completed` | 注文完了 |
| `cancel_request;reason=...` | キャンセルリクエスト |
| `cancel_request_closed` | キャンセル終了 |
| `return_request;reason=...` | 返品リクエスト |
| `return_request_closed` | 返品終了 |
| `dispute_open;reason=...` | 異議申立て |
| `dispute_closed` | 異議終了 |
| `item_not_received;reason=...` | 未着リクエスト |
| `item_not_received_closed` | 未着終了 |
| `case_closed` | ケース終了 |

**完全リストは `block_chat_history.md` 参照**

### トーン（tone enum）

| コード | 日本語 | 使い方 |
|-------|-------|-------|
| `polite` | 丁寧 | フォーマル・プロフェッショナル |
| `friendly` | フレンドリー | 親しみやすい・カジュアル |
| `apologetic` | 謝罪 | 共感・責任表明 |

---

## ❓ FAQ（よくある疑問）

### Q: 「admin_prompt」と「ベースプロンプト」の違いは？
**A:** 役割が違います。
- **ベースプロンプト（[N+2] BASE_PROMPT + [N+3] OUTPUT_FORMAT）**：Cowatech管理。eBayコンプライアンスとJSON形式強制。ほぼ不変。
- **admin_prompt（[N+4]）**：社長管理。CS品質・トーン・会話ロジック。日常的に改善。

### Q: プロンプトを変更したら、変更は即座に本番に反映される？
**A:** 変更する場所によります。
- **admin_prompt**：admin画面から編集すれば即反映
- **BASE_PROMPT / OUTPUT_FORMAT / FORCED_TEMPLATE**：Cowatechへの実装依頼が必要

### Q: AIが変な返信を生成したとき、どこを確認すればいい？
**A:** 以下の順番で確認：
1. **admin_prompt v2.4** を見て、該当ケースへの指示があるか
2. **バイヤーメッセージ分類**（BUYER MESSAGE TYPE HANDLING）で正しく分類されているか
3. **FORCED_TEMPLATE** が適切か（除去検証中）
4. **チャット履歴** にノイズ（無関係な自動メッセージ等）が多すぎないか
5. **商品情報JSON** が正しい商品を指しているか

### Q: 新しいトーン（例：casual）を追加したい場合はどうすればいい？
**A:** 以下の更新が必要：
1. UIにトーン選択肢を追加（Cowatech実装）
2. `[N+4] admin_prompt` のTONE GUIDELINESに追加（社長）
3. `[N+5] FORCED_TEMPLATE` にcasualバリエーションを追加（Cowatech実装）
4. `02_ui_injection_matrix.md` の表を更新
5. `04_conditional_logic.md` のトーン分岐表を更新
6. `06_glossary.md`（このファイル）のトーン enum に追加
7. `05_changelog.md` に記録

### Q: 「descriptionが空でない場合のみ [N+1] が注入される」ってどう判定してる？
**A:** **v0.2時点で判定ロジック未確認（Q3）**。Cowatechへの確認事項。空文字列・null・trim後の空の扱いを明確化する必要あり。

### Q: なぜFORCED_TEMPLATEを除去すると品質が上がるの？
**A:** admin_prompt v2.4 が「状況判断で挨拶・結句を柔軟にせよ」と指示しているのに対し、FORCED_TEMPLATEが「必ず Hello/Best regards を使え」と矛盾する強制をしているため。
12ケーステストで平均19.5 → 21.5（+2.0pt）改善。ただしTO/FROMのUI値の代替注入経路の設計が未決（Q1）。

### Q: 本番とテストは同じ構造でやってる？
**A:** はい。`services/baychat/ai/testing/payload_builder.py` を使うと本番と同構造のペイロードでテストできます。2026-04-16以降、このインフラで検証しています。

### Q: AIモデルを変更したい場合、Cowatechには何を伝えればいい？
**A:** 以下を明記：
1. 変更後のモデル名（例：`gemini-2.5-flash`）
2. プロバイダ（OpenAI / Google / Anthropic）
3. APIパラメータの差分（temperature等）
4. response_format対応の有無
5. JSON strict mode対応の有無

→ Gemini 2.5 Flashは現在検討中。詳細は `11_model_selection.md` 参照。

### Q: 設計図とCSVに矛盾があった場合、どちらを信じる？
**A:** **設計図を信じる**。CSVは「参考資料」にデモートされているため。矛盾を発見したら `09_open_questions.md` に記録してCowatechに確認。

### Q: Cowatechに質問する前にやるべきことは？
**A:** 以下を確認：
1. 設計図内で回答が見つからないか（検索）
2. 既存論点（`09_open_questions.md`）に同じ質問がないか
3. 質問がCowatechの管理範囲か（`07_cowatech_operation.md` 参照）
4. 社長の承認が必要か（新規方針決定は社長承認要）

### Q: 新しい不具合を見つけたらどうする？
**A:** `14_qa_testing.md` の「過去の不具合記録」セクションに追記＋ `05_changelog.md` に記録。

### Q: バージョン番号のルールは？
**A:** 
- 設計図全体：v0.1（叩き台）→ v0.2（実データ統合）→ v1.0（Cowatechレビュー完了）
- admin_prompt：v1.0 → v1.1 → v2.0 → v2.1 → v2.2 → v2.3 → v2.4（現行）
- 各ブロック：設計図全体バージョンに連動

### Q: トークン（token）って何？
**A:** AIが文字を処理する単位。1トークン ≈ 0.75単語（英語）/ 1文字（日本語）。
- コスト：トークン数 × モデル単価
- レイテンシ：入力トークンが多いほど遅い
- 上限：モデルごとに最大入力トークン数がある

### Q: 「本番モード」と「テストモード」って何が違う？
**A:** 
- **本番モード**：Cowatech実装の本番と完全同構造のペイロード（FORCED_TEMPLATE含む）
- **テストモード**：検証用。`--no-forced-template` などで一部ブロックをON/OFF可能
- 本番モード：`batch_test.py --production-payload`

### Q: Gemini 2.5 Flash はいつ本番に入るの？
**A:** Cowatech実装完了待ち（Q6）。採用は**2026-03-19に決定済み**だが実装時期は未確認。

### Q: 設計図を見ればすべてが分かる状態を目指しているとのことだが、本当に？
**A:** はい、目指しています。現状 v0.2 の完成度は高いですが、Q1-Q9（特に高優先度）が解決するまで完全ではありません。解決したら v1.0 として Cowatech レビュー完了版になります。

---

## 🔤 略語集

| 略語 | 意味 |
|------|------|
| API | Application Programming Interface |
| CS | Customer Support |
| DB | Database |
| FB | Feedback |
| INR | Item Not Received |
| JSON | JavaScript Object Notation |
| LLM | Large Language Model |
| QA | Quality Assurance |
| RDS | Relational Database Service（AWS） |
| SDK | Software Development Kit |
| SKU | Stock Keeping Unit |
| SSH | Secure Shell |
| STG | Staging |
| UI | User Interface |
| UX | User Experience |
| UUID | Universally Unique Identifier |
| VPS | Virtual Private Server |
| eID | eBay ID |

---

## 🧭 この用語集の育て方

- **議論で疑問が出たら即追加**：後で書こうとすると忘れる
- **Cowatechとのやり取りで使った英語用語を日本語と対で残す**：共通言語を増やす
- **曖昧な用語は「要定義」マークで残す**：未確定を可視化
- **FAQは実際に聞かれた質問を残す**：仮想的なFAQは書かない

---

*このファイルは「共通辞書」。設計図の他のファイルで分からない用語が出てきたら、ここを参照する。*
