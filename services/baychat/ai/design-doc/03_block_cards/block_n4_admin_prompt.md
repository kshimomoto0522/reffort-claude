# ブロックカード：[N+4] admin_prompt

> **このカードはv0.2の完成版です。**
> 🆕 **2026-04-23 更新**：Cowatech prd実装（2026-04-22 23:58反映）に合わせて、プレースホルダ正式名を `{sellerAccountEbay}/{buyerAccountEbay}` に統一。FORCED_TEMPLATE除去完了に伴い、本ブロックが挨拶・署名制御の主担当となった。

---

## 📇 基本情報

| 項目 | 内容 |
|------|------|
| **ブロックID** | `admin_prompt` |
| **順序** | [N+4]（6ブロック中6番目・FORCED_TEMPLATE廃止後は最後尾） |
| **role** | `developer` |
| **管理主体** | **Reffort（社長）** |
| **編集場所** | BayChat admin画面 |
| **現行バージョン** | **v2.4 本番稼働中**（2026-04-15）／ **v2.6 ドラフト**（2026-04-23 プレースホルダ命名統一済み・社長admin画面アップロード待ち） |
| **実物ファイル** | `services/baychat/ai/prompt_admin_v2.4.md`（本番）／ `prompt_admin_v2.6.md`（次期） |
| **変更頻度** | 🟢 高（日常的に改善） |
| **ON/OFF** | 常時ON（条件分岐なし） |

---

## 🎯 このブロックの目的（なぜ存在するか）

BayChat AIの **CS品質・トーン・会話ロジックの中核**を担うプロンプト。

- [N+2] BASE_PROMPT は「eBayコンプライアンス」という土台ルール
- [N+3] OUTPUT_FORMAT は「JSON形式」という出力形式の強制
- **[N+4] admin_prompt は「どんなCSパーソンとして、どう考えて、どう返すか」という頭脳**

社長が admin画面から直接編集・即反映できる唯一のブロック。
**= AI Replyの品質改善の主戦場。**

---

## 📐 現行の構成要素（v2.4）

admin_prompt v2.4 は以下のセクションから構成される：

| # | セクション | 役割 |
|---|----------|-----|
| 1 | ROLE | AIが演じる役割（eBay CS professional）と基本制約 |
| 2 | CONVERSATION STAGE DETECTION | 会話段階（初回/継続中/複数未読）の判定ルール |
| 3 | BUYER MESSAGE TYPE HANDLING | バイヤーメッセージの5分類（A〜E）と対応スタイル |
| 4 | SELLER INTENT | 補足情報（`{sellerSetting}`）の扱い方・品質基準 |
| 5 | TONE GUIDELINES | polite / friendly / apologetic の3トーンの挙動 |
| 6 | RESPONSE STRUCTURE | 返信の構造（acknowledge → answer → next step → close） |
| 7 | INPUTS | 動的プレースホルダ（`{sellerSetting}` / `{toneSetting}`）の宣言 |
| 8 | FINAL CHECK | 出力前の自己チェック（復唱禁止・約束禁止・プレースホルダ残存チェック） |

---

## 🎛️ 動的プレースホルダ（UIからの注入）

> 🆕 **2026-04-23 更新**：Cowatech prd反映（2026-04-22 23:58）により `{buyerAccountEbay}` / `{sellerAccountEbay}` が本ブロックへ注入される仕組みが実装済み。v2.6ドラフトから命名統一済み。

| プレースホルダ | 置換元（UI） | 注入される箇所 | 空のときの挙動 |
|--------------|-----------|-------------|------------|
| `{sellerSetting}` | 補足情報欄 | SELLER INTENTセクション冒頭<br/>INPUTSセクション | 空文字連結。「If not provided: the buyer's request IS the direction.」で空許容ロジックあり |
| `{toneSetting}` | トーンプルダウン | INPUTSセクション | 必須UI項目のため空にならない想定 |
| 🆕 `{buyerAccountEbay}` | UI「TO（受取人）」プルダウン（ID / 氏名 / 担当者名 / なし） | GREETING & SIGNATURE POLICYセクション<br/>INPUTSセクション<br/>FINAL CHECK言及 | 「なし」選択時：`{buyerAccountEbay}`が空文字に置換され、プロンプトの「WHEN A PLACEHOLDER IS EMPTY」ルールでAIが挨拶を省略 |
| 🆕 `{sellerAccountEbay}` | UI「FROM（送信者）」プルダウン（ID / 氏名 / 担当者名 / なし） | 同上 | 同上（署名を省略） |

---

## 🌐 影響範囲（このブロックを変更したときに波及する先）

### 直接影響する要素

| 要素 | 影響内容 |
|------|--------|
| 全リプライの品質 | 全ケースで生成されるAI返信の品質・トーン・構造 |
| トーン別挙動 | TONE GUIDELINESセクションがトーン選択の振る舞いを規定 |
| バイヤーメッセージ分類 | BUYER MESSAGE TYPE HANDLINGが挨拶・URLのみ・クレーム等への対応を分岐 |
| 復唱・約束禁止 | MUST NOT / FINAL CHECKが過去情報の再説明・将来約束を抑制 |

### 間接影響する要素

| 要素 | 影響内容 |
|------|--------|
| ~~[N+5] FORCED_TEMPLATE との整合~~ | **✅ 2026-04-22 prd反映でFORCED_TEMPLATE廃止済み**。挨拶・署名制御はadmin_prompt（GREETING & SIGNATURE POLICY）に一元化された |
| [N+1] 補足情報ガイド との整合 | 両方とも `{sellerSetting}` を扱うため、descriptionあり時のロジックがダブる可能性 |
| BayChat後処理 | `jpnLanguage` / `buyerLanguage` の2フィールドを前提とする後処理と結合（OUTPUT_FORMATと重複指定） |

### 変更による副作用のリスク

- **過剰ルール化**：セクションを増やすほど、AIが矛盾したルール間で揺れる
- **既存成功ケースの劣化**：1ケース直すつもりが、10ケース悪化することがある（v2.3→v2.4でも1ケース劣化あり）
- **バージョン混乱**：admin画面に古いバージョンが残っている場合、本番と認識がズレる

---

## 📜 バージョン履歴（完全版・エージェント3調査結果より）

| Ver | 日付 | 主な変更 | きっかけ・設計思想 |
|-----|-----|--------|------|
| v1.0 | 2026-03-18 | 初版。ベースプロンプト最小化に伴いCS品質全般をadminに移管 | BayChat AI Reply最初の設計 |
| v1.1 | 2026-03-19 | 出力フィールド名修正（japanese→jpnLanguage、reply→buyerLanguage） | API仕様との整合 |
| v2.0 | 2026-03-19 | **設計思想を刷新**。ルール積み重ね型→判断力重視型へ。冗長セクション削除 | AIの自律判断を信頼する設計転換 |
| v2.1 | 2026-03-19 | 文脈読解・Stage検知・勝手な判断の3点強化 | v2.0運用で「勝手な判断」問題発見 |
| v2.2 | 2026-03-21 | MUST NOT・SELLER INTENT根本改善。補足なし時・保留禁止・品質基準強化 | テスト環境で品質低下を検出 |
| v2.3 | 2026-03-30 | 補足あり時のバイヤー無視問題解決。保留禁止を「決定vs約束」で再定義。FINAL CHECK新設 | セラー補足優先でバイヤー無視の不具合 |
| **v2.4** | **2026-04-15** | **復唱禁止明文化。BUYER MESSAGE TYPE HANDLING新設（A〜E 5分類）。テンプレート強制緩和。FINAL CHECK拡張** | **テスト環境でテンプレート強制除去で+2.0pt改善** |
| v2.5 | 2026-04-20 | FORCED_TEMPLATE除去前提。GREETING & SIGNATURE POLICY新設。`{buyer_name}/{seller_name}`プレースホルダ追加（当時の内部命名） | +2.0pt改善実装に向けた準備 |
| v2.6 | 2026-04-21 | EMPATHY ENFORCEMENT / MULTILINGUAL HANDLING / COMPLEX CASE HANDLING 新設。Next step具体性強化 | v2.5の40ケーステストで判明した弱点の改善 |
| **v2.6（命名統一）** | **2026-04-23** | **Cowatech prd実装（2026-04-22反映）に合わせてプレースホルダ名を `{buyerAccountEbay}/{sellerAccountEbay}` に統一** | **設計図⇔実装乖離の解消** |

### 📊 設計思想の変遷

**v1.x（ルール積み重ね型）** — 冗長・全シーン網羅不可
  ↓
**v2.0（判断力重視型）** — 短縮化。逆に「勝手な判断」が発生
  ↓
**v2.1-v2.2（ピンポイント修正）** — バランス調整。重要なガードレールのみ追加
  ↓
**v2.3（バイヤー優先化）** — Step 1: バイヤー応答 → Step 2: 補足統合
  ↓
**v2.4（柔軟性の許可）** — メッセージタイプA〜Eで対応スタイル分岐

### v2.4 の BUYER MESSAGE TYPE HANDLING（新設セクション詳細）

| 分類 | 例 | 対応スタイル |
|------|-----|-----------|
| **A** SUBSTANTIVE | "When will it ship?" / "I want to return" | 標準CS返答（ack→answer→next→close） |
| **B** CLOSING/GRATITUDE | "Thanks!" / "Have a great day" | 1〜3文の短く温かい返答 |
| **C** URL-ONLY | リンクのみ | 短いack + 確認質問 |
| **D** COMPLAINT | "The color is lighter" / "damaged" | APOLOGYトーン：共感→セラー意図 |
| **E** AMBIGUOUS | 超短文・多言語混在 | 短い確認質問（推測しない） |

### v2.4 FINAL CHECK の5項目

出力前の自己チェック：
1. 保留表現（will send/will provide/shortly/please wait）なし
2. バイヤーの状況に応答しているか（セラー意図だけじゃないか）
3. 既出情報を復唱していないか
4. フォーマル度はメッセージに合わせているか
5. プレースホルダ（`{buyerAccountEbay}` `{sellerAccountEbay}` `{sellerSetting}` `{toneSetting}`等）残存していないか

**詳細な原文は `services/baychat/ai/prompt_admin_v{version}.md` の各ファイル参照。**

---

## 🧪 品質ベンチマーク（v2.4時点）

| 項目 | 値 |
|------|---|
| 本番同等テストのスコア（FORCED_TEMPLATE ON） | 19.5 / 25（平均、12ケース） |
| 本番同等テストのスコア（FORCED_TEMPLATE OFF） | **21.5 / 25**（平均、12ケース） |
| 評価方法 | AI審判（5項目×5点） |
| テストケース出典 | `testing/test_cases/extracted_20260415_210506.json` |
| 計測ファイル | `testing/results/test_gpt_v2.4_prodON_20260416_173453.xlsx`<br/>`testing/results/test_gpt_v2.4_prodOFF_20260416_173615.xlsx` |

**→ [N+5] FORCED_TEMPLATE除去で+2.0pt改善。admin_prompt v2.4は「状況判断できる設計」なのでテンプレ強制を外した方が力を発揮する。**

---

## 🔧 変更プロセス（社長向け運用手順）

### 日常的な微修正（社長単独で可）
1. 改善したい挙動を特定（例：「短い御礼メッセージに重い形式を被せる問題」）
2. `services/baychat/ai/prompt_admin_v2.4.md` をコピーして `prompt_admin_v2.5.md` を作成
3. Claudeと一緒に変更案を作成
4. `services/baychat/ai/testing/batch_test.py --production-payload --prompt-versions 2.5` でテスト
5. スコア改善を確認
6. BayChat admin画面で本番反映
7. `05_changelog.md` に記録
8. このカードの「現行バージョン」「バージョン履歴」「品質ベンチマーク」を更新

### 構造的な変更（Cowatech協議が必要な変更）
例：新しいセクション（要約モード用など）の追加、プレースホルダの追加

1. このカードの構成要素リストと影響範囲を更新
2. [N+1] / [N+4] / [N+5] のブロックカード間の整合を確認
3. `04_conditional_logic.md` への影響を確認
4. Cowatechに仕様書（このカード＋関連カード）を送って合意形成
5. 実装後、admin画面で本番反映
6. `05_changelog.md` に記録

---

## 🤝 Cowatech合意事項

| 項目 | 合意内容 | 合意日 | 根拠 |
|------|--------|------|------|
| 置換ロジック | `{sellerSetting}` / `{toneSetting}` はBayChat側で置換 | 2026-03-21 | Slack履歴 |
| admin画面編集可能 | 社長がadmin画面から直接編集可能 | プロジェクト開始時 | — |
| AIモデル | `gpt-4.1-mini-2025-04-14` / temperature=0.2 | 2026-04-16 | `gpt_api_payload.txt`の実計測 |
| response_format | `json_schema` strict / name=`multi_language_reply` | 2026-04-16 | 同上 |
| 🆕 **FORCED_TEMPLATE廃止＋本ブロックへのプレースホルダ注入** | **`{buyerAccountEbay}` / `{sellerAccountEbay}` をadmin_prompt内で動的置換。UI signature/receiver選択（ID/氏名/担当者名/なし）に応じて値を注入** | **2026-04-22 23:58（stg+prd反映完了）** | **Slack thread_ts `1776427836.602699` クエットさん返信「対応してstgとprdに反映済み」** |

---

## ⚠️ 未解決の論点（Cowatech確認待ち）

| # | 論点 | 重要度 |
|---|-----|------|
| ~~P1~~ | ~~FORCED_TEMPLATE除去時のTO/FROM値の代替注入経路~~ | ✅ **2026-04-22 解決済み**（admin_promptへプレースホルダ注入方式で決着） |
| P2 | descriptionが空のとき `{sellerSetting}` に何が入るか（空文字？null？なにか文字列？） | 🟡 中 |
| P3 | admin画面に複数バージョン履歴を保存できるか（即ロールバック用） | 🟡 中 |

---

## 📚 関連ドキュメント

| ドキュメント | 役割 |
|----------|------|
| `services/baychat/ai/prompt_admin_v2.4.md` | 現行プロンプトの実物 |
| `services/baychat/ai/handoff_20260416_results.md` | FORCED_TEMPLATE比較テスト結果 |
| `services/baychat/ai/testing/payload_builder.py` | 本番同等テスト環境 |
| `02_ui_injection_matrix.md` | UI→このブロックへの注入経路 |
| `04_conditional_logic.md` | このブロックのON/OFF条件 |

---

*このカードは「admin_prompt の全貌を見開き1枚で把握できる」ことを目指している。情報が不足・過剰なら社長レビューで指摘を。*
