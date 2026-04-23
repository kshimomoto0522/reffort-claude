# BayChat AI Reply 本番ペイロード再現テスト結果
> 作成日: 2026-04-16（セッション継続中に実行）
> 前提: 2026-04-15引き継ぎ文書で提起された「オフラインテストは本番ペイロード構造と一致していないと無意味」問題への対応

---

## 1. 実施したこと（このセッション）

1. Cowatechスプレッドシート全シートを読み込み、本番ペイロード構造を確定
2. `baychat-ai/testing/payload_builder.py` を新設（本番と同構造のmessages配列を組み立てる）
3. `batch_test.py` に `--production-payload` / `--no-forced-template` オプションを追加
4. 12ケース×GPT-4.1-Mini×プロンプトv2.4 を **本番再現モード** で2回実行：
   - **forced_template=ON**（現行本番と同一構造）
   - **forced_template=OFF**（FORCED TEMPLATEブロック除去）

---

## 2. 本番ペイロード構造（確定）

```
[0]   developer : 商品情報JSON (ItemID, Title, Variations ...)
[1..] system/assistant/user : チャット履歴
[N+1] developer : 補足情報ガイド（descriptionが空でない場合のみ）
[N+2] developer : BASE_PROMPT (PLATFORM COMPLIANCE — Cowatech固定)
[N+3] developer : OUTPUT_FORMAT (JSON strict — Cowatech固定)
[N+4] developer : admin_prompt (下元管理。{toneSetting}/{sellerSetting}置換後)
[N+5] developer : FORCED_TEMPLATE (Hello/Best regards — tone別)  ← 本検証で除去対象
```

- `model`: `gpt-4.1-mini-2025-04-14`
- `temperature`: `0.2`
- `response_format`: `json_schema` strict (`multi_language_reply`)
- 根拠: `cowatech_payloads/gpt_api_payload.txt`（実本番1件）＋`cowatech_payloads/spec_sheets/SUMMARY_PROMT.csv`（公式仕様）

---

## 3. 比較結果（12ケース × GPT-4.1-Mini × v2.4）

| モード | 平均スコア | コスト合計 | ファイル |
|---|---|---|---|
| **ON（現行本番）** | **19.5 / 25** | ¥3.02 | `testing/results/test_gpt_v2.4_prodON_20260416_173453.xlsx` |
| **OFF（テンプレ除去）** | **21.5 / 25** | ¥2.85 | `testing/results/test_gpt_v2.4_prodOFF_20260416_173615.xlsx` |
| **差** | **+2.0 pt** | -¥0.17 | — |

### ケース別スコア差分

| ケース | カテゴリ | ON | OFF | 差 |
|---|---|---|---|---|
| prettypoodle1234 | cancel | 21 | 18 | **−3** |
| antonioto | — | 22 | 25 | +3 |
| ay-1144 | — | 20 | 23 | +3 |
| ca2015_trao | — | 15 | 19 | +4 |
| eduherrer76 | — | 22 | 25 | +3 |
| olja_7021 | — | 21 | 21 | 0 |
| spv332 | — | 25 | 25 | 0 |
| rolanbuen | — | 18 | 20 | +2 |
| nokiafan_blau | — | 17 | 19 | +2 |
| racro_5039 | — | 17 | 20 | +3 |
| abmb59 | — | 17 | 20 | +3 |
| mobirush | — | 19 | 23 | +4 |

→ 10ケースで改善または同点。1ケース（prettypoodle1234）で悪化（−3）。
→ **FORCED TEMPLATE除去は全体として品質を押し上げる**ことが定量的に確認できた。

---

## 4. 考察

### なぜ OFF が良いのか
- v2.4 admin_promptには「RESPONSE STRUCTURE」「BUYER MESSAGE TYPE HANDLING」で
  「短い御礼メッセージ（TypeB）には軽い挨拶で十分」「TypeAなら "Hello {buyer_name},"」と
  状況適応で使い分けるルールが既に実装されている
- FORCED TEMPLATEは状況に関わらず "Hello ... Best regards, ..." を強制するため、
  ちょっとした御礼・確認メッセージにも重い形式を被せてしまい不自然になる
- v2.4は「状況判断できる設計」なので、FORCED TEMPLATEを外した方が v2.4 の力を発揮できる

### 唯一の悪化ケース（prettypoodle1234）について
- カテゴリ: cancel（税関トラブル → 返品リクエスト → 返金待ち）
- ON版は FORCED TEMPLATE により「Hello prettypoodle1234, ... Best regards, rioxxrinaxjapan」で署名まできちんと書かれ、AI審判が丁寧さを評価した可能性
- OFF版は「Best regards,」のあとのseller名がない、または簡略化されて減点
- → **TO/FROM選択機能との整合性を取る必要あり**（後述）

---

## 5. ⚠️ 重要論点：TO/FROM選択機能との関係

BayChat AI Reply画面には **TO（宛先）** と **FROM（署名）** のプルダウンがある：
- TO: バイヤーID / バイヤー氏名 / なし
- FROM: セラーID / セラー氏名 / 担当者名 / なし

現行本番では、FORCED TEMPLATEの最下部に：
```
seller_name: {UI側でFROMに選ばれた値}
buyer_name: {UI側でTOに選ばれた値}
```
として注入されている。

**FORCED TEMPLATEを除去する場合、TO/FROMの値の受け渡し方を設計し直す必要がある。**

### 選択肢

| 案 | 方法 | 利点 | 課題 |
|---|---|---|---|
| A | admin_promptに `{buyerAddress}` `{sellerSignature}` プレースホルダを追加し、末尾に値を差し込む | admin_prompt側で柔軟にハンドリング可能 | Cowatech側の実装変更が必要 |
| B | FORCED TEMPLATEを「軽量ヒント」に書き直す（「形式強制」→「参考ヒント」） | Cowatech変更は最小 | 「強制」でなくなることでAIが無視する可能性 |
| C | ベースプロンプトに `Greeting target: {buyerAddress}, Signature: {sellerSignature}` を注入 | admin_promptと分離できる | ベースプロンプト=Cowatech管理のため変更が必要 |

→ **社長判断＋Cowatech相談が必要**（次の「Slack草案」参照）

---

## 6. 次のアクション

### 即やること
- [x] 本番ペイロード再現インフラ構築（`payload_builder.py`）
- [x] 12ケース baseline 実施（prodON / prodOFF）
- [ ] **社長レビュー**: prodON vs prodOFF の返信本文を実際に比較（`test_gpt_v2.4_prodOFF_20260416_173615.xlsx` の「返信比較」シート）
- [ ] **TO/FROM問題**: 上記A/B/Cのどれで行くかの方針決定
- [ ] **Cowatech相談**: 決定した方針をSlackで共有・実装依頼（草案は `slack_draft_20260416.md` に保存済み）

### 中期
- [ ] 同一テストを **Gemini 2.5 Flash** でも実行（CLAUDE.mdで次期採用方針のため）
- [ ] 謝罪トーン（apologetic）・フレンドリートーン（friendly）での追加検証
- [ ] 補足情報（description）ありパターンの検証

---

## 7. 技術メモ

### 実行コマンド
```bash
# 本番再現モード・FORCED TEMPLATE ON
cd baychat-ai/testing
python batch_test.py --models gpt --prompt-versions 2.4 \
  --cases test_cases/extracted_20260415_210506.json \
  --production-payload --judge openai

# 本番再現モード・FORCED TEMPLATE OFF
python batch_test.py --models gpt --prompt-versions 2.4 \
  --cases test_cases/extracted_20260415_210506.json \
  --production-payload --no-forced-template --judge openai
```

### 新規ファイル
- `baychat-ai/testing/payload_builder.py` — 本番ペイロード組み立てロジック
- `baychat-ai/handoff_20260416_results.md` — 本ドキュメント
- `baychat-ai/slack_draft_20260416.md` — Cowatech向けSlack草案（社長承認後送信）

### 変更ファイル
- `baychat-ai/testing/batch_test.py` — `--production-payload` 他のフラグ追加

---

*社長の出先からの復帰後、まずこのドキュメントを読んで、その後 `test_gpt_v2.4_prodOFF_20260416_173615.xlsx` の「返信比較」シートで本文レベルの差を見ていただくと効率的です。*
