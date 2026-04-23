# 01. プロンプトブロック俯瞰表

> このファイルの役割：AIに送信される**全ブロックを一枚の表で俯瞰**できるようにする。
> 「今どのブロックが、誰の管理で、何のためにあるか」を10秒で把握するためのもの。
>
> 🆕 **2026-04-23 更新**：Cowatech prd反映（2026-04-22 23:58）により FORCED_TEMPLATE [N+5] は廃止。admin_prompt [N+4] が挨拶・署名制御を吸収。

---

## 🎯 ブロック一覧（左：実装 ／ 中：目的 ／ 右：影響範囲）

| 順 | ブロック名 | role | 管理主体 | 目的（なぜ存在するか） | 影響範囲（変更時に波及する先） | 変更頻度 |
|---|-----------|------|---------|-------------------|-------------------------|--------|
| **[0]** | 商品情報JSON<br/>`item_info` | `developer` | BayChat（自動取得） | AIに「どの商品についてのやり取りか」を教える | DB商品テーブル / eBay API / UIの商品表示部 | ❌ 仕様固定 |
| **[1..N]** | チャット履歴<br/>`chat_history` | `user` / `assistant` / `system` | BayChat（DB自動取得） | バイヤーとのやり取り・発生イベントの文脈をAIに渡す | DBメッセージテーブル / DBイベントテーブル | ❌ 仕様固定 |
| **[N+1]** | 補足情報ガイド<br/>`description_guide` | `developer` | Cowatech（テンプレ固定） | 補足情報（description）が入力されているときのAIへの指示 | UIの補足情報欄 / admin_promptの`{sellerSetting}` | 🟡 低（仕様変更時のみ） |
| **[N+2]** | BASE_PROMPT<br/>`base_prompt` | `developer` | Cowatech | eBayコンプライアンス制約（違反行為の禁止） | eBayポリシー改定時のみ変更 | ❌ ほぼ不変 |
| **[N+3]** | OUTPUT_FORMAT<br/>`output_format` | `developer` | Cowatech | JSON出力強制（`jpnLanguage`/`buyerLanguage`の2フィールド） | BayChat後処理 / schema名`multi_language_reply` | ❌ ほぼ不変 |
| **[N+4]** | admin_prompt<br/>`admin_prompt` | `developer` | **Reffort（社長）** | CS品質・トーン・会話ロジックの中核＋**挨拶・署名制御（2026-04-22〜）**。最も頻繁に改善する層 | 全リプライの品質 / トーン別挙動 / 挨拶・署名 / `{buyerAccountEbay}` `{sellerAccountEbay}` 注入 | 🟢 **高（日常的に改善）** |
| ~~**[N+5]**~~ | ~~FORCED_TEMPLATE~~<br/>~~`forced_template`~~ | ~~`developer`~~ | ~~Cowatech~~ | **❌ 2026-04-22 廃止済み**。挨拶・署名制御はadmin_promptに移管 | — | ❌ 廃止 |

---

## 📊 ブロックの性質マトリクス

### 分類1：静的ブロック vs 動的ブロック

| ブロック | 静的/動的 | 動的要素 |
|---------|---------|--------|
| [0] 商品情報JSON | 動的 | ItemID経由で商品ごとに内容が変わる |
| [1..N] チャット履歴 | 動的 | バイヤーごと・やり取り進行ごとに変わる |
| [N+1] 補足情報ガイド | 条件付き注入 | ON/OFF自体が動的（description有無で切り替え） |
| [N+2] BASE_PROMPT | 静的 | テキスト完全固定 |
| [N+3] OUTPUT_FORMAT | 静的 | テキスト完全固定 |
| [N+4] admin_prompt | 半動的 | テキスト本体は社長管理（更新自由）。`{sellerSetting}` / `{toneSetting}` / 🆕`{buyerAccountEbay}` / 🆕`{sellerAccountEbay}` が動的置換 |
| ~~[N+5] FORCED_TEMPLATE~~ | ❌ 廃止 | ~~tone別に3バリエーション~~ |

### 分類2：管理主体別

| 管理主体 | 担当ブロック | 変更プロセス |
|---------|-----------|-----------|
| **BayChat自動取得** | [0] / [1..N] | コード実装。Cowatech開発 |
| **Cowatech（固定）** | [N+1] / [N+2] / [N+3] | Cowatechに依頼 → 実装確認 → 本番反映 |
| **Reffort（社長）** | [N+4] admin_prompt | admin画面から社長が直接編集・即反映 |

**→ 社長がいつでも即時に改善できるのは [N+4] admin_prompt のみ。他はCowatech実装の手が必要。**
**→ 2026-04-22以降、挨拶・署名制御も [N+4] に集約されたため社長の裁量範囲が拡大。**

---

## 🎛️ ブロック内の動的プレースホルダ一覧

admin_prompt（[N+4]）には、UI操作で値が差し込まれるプレースホルダがある（2026-04-22以降、すべて [N+4] に集約）：

| プレースホルダ | 置換元 | 注入先ブロック | 注入タイミング |
|--------------|--------|-------------|------------|
| `{sellerSetting}` | UI「補足情報」欄 | [N+4] admin_prompt の2箇所（SELLER INTENT / INPUTS） | ペイロード組み立て時 |
| `{toneSetting}` | UIトーンプルダウン | [N+4] admin_prompt の1箇所（INPUTS） | ペイロード組み立て時 |
| 🆕 `{buyerAccountEbay}` | UI「TO（受取人）」プルダウン（ID / 氏名 / 担当者名 / なし） | [N+4] admin_prompt（GREETING & SIGNATURE POLICY / INPUTS / FINAL CHECK） | ペイロード組み立て時 |
| 🆕 `{sellerAccountEbay}` | UI「FROM（送信者）」プルダウン（ID / 氏名 / 担当者名 / なし） | 同上 | ペイロード組み立て時 |
| ~~`{buyer_name}`~~ | ~~UI「TO」~~ | ~~[N+5] FORCED_TEMPLATE~~ | ❌ **2026-04-22 廃止**：`{buyerAccountEbay}`に統一 |
| ~~`{seller_name}`~~ | ~~UI「FROM」~~ | ~~[N+5] FORCED_TEMPLATE~~ | ❌ **2026-04-22 廃止**：`{sellerAccountEbay}`に統一 |
| ~~`{output_content}`~~ | — | ~~[N+5] FORCED_TEMPLATE~~ | ❌ **廃止**：AI出力はjpnLanguage/buyerLanguageフィールドへ直接格納 |
| ~~`{greeting}`~~ | — | ~~[N+5] FORCED_TEMPLATE apologetic版~~ | ❌ **廃止**：admin_prompt TONE GUIDELINESでAI判断を指示 |

**→ UI↔プロンプトの対応表は `02_ui_injection_matrix.md` を参照。**

---

## 🔢 ブロックのトークン消費量（参考値・2026-04計測）

| ブロック | 概算トークン数 | 全体に占める比率 |
|---------|-------------|--------------|
| [0] 商品情報JSON（バリエーション15個想定） | ~800 | ~25% |
| [1..N] チャット履歴（10往復想定） | ~1500 | ~45% |
| [N+1] 補足情報ガイド | ~30 | ~1% |
| [N+2] BASE_PROMPT | ~120 | ~4% |
| [N+3] OUTPUT_FORMAT | ~80 | ~2% |
| [N+4] admin_prompt（v2.6） | ~900 | ~27% |
| ~~[N+5] FORCED_TEMPLATE~~ | ❌ 廃止（~70トークン削減） | — |
| **合計（入力・v2.6想定）** | **~3430** | **100%** |

（参考：廃止前 `gpt_api_payload.txt`の返品ケース1件 = 3350 input_tokens。FORCED_TEMPLATE廃止で純減するが、admin_prompt拡張（v2.4→v2.6）で相殺傾向）

**→ トークン最適化の余地が大きいのは [1..N] チャット履歴 と [0] 商品情報JSON。**

---

## 🚦 ブロック追加・変更時のチェックリスト

新しいブロックを追加したり、既存ブロックを変更するとき、以下を確認する：

- [ ] 順序性に影響するか（前後のブロックの前提が崩れないか）
- [ ] 条件分岐に影響するか（`04_conditional_logic.md` の更新が必要か）
- [ ] UI操作と連動するか（`02_ui_injection_matrix.md` の更新が必要か）
- [ ] プレースホルダが増えるか（置換ロジックのCowatech実装が必要か）
- [ ] トークン数が大きく変わるか（コストとレイテンシに影響）
- [ ] Cowatech合意が必要か（[N+1][N+2][N+3][N+5]変更時は必須）
- [ ] ブロック詳細カード（`03_block_cards/`）の更新を忘れていないか
- [ ] `05_changelog.md` への記録

---

## 📌 Cowatech確認事項の状況

| # | 論点 | 状態 |
|---|-----|-----|
| ~~Q1~~ | ~~FORCED_TEMPLATE除去時のTO/FROM値の代替注入経路~~ | ✅ **2026-04-22 解決**（admin_promptへプレースホルダ注入方式でCowatech実装完了） |
| Q2 | admin_promptの`{sellerSetting}`/`{toneSetting}`置換はBayChat側？AI側？ | ✅ BayChat側（確認済み） |
| ~~Q3~~（TO/FROM部分） | ~~TO/FROM「なし」選択時の挙動~~ | ✅ **2026-04-22 解決**（空文字置換＋admin_promptの空許容ルールで省略） |
| Q3（description部分） | description「空」判定ロジック（空文字列？null？trim後？） | 🔴 未解決 |
| Q4 | チャット履歴の件数上限（全件？直近N件？トークン制限？） | 🔴 未解決 |
| Q5 | `multi_language_reply` schema名をBayChatが参照しているか（strict modeの後処理） | 🔴 未解決 |

**→ 詳細は `09_open_questions.md` を参照。**
