# BayChat AI Reply — 新セッション引継ぎ（2026-04-29 夕方 → 翌セッション）

> **新セッション冒頭でこのファイルを最初に読むこと。**
> 続いて以下 memory 2 件を読む（自動ロード対象だが念のため明示）：
> - `memory/feedback_baychat_ai_reply_stance.md`（5 原則）
> - `memory/feedback_baychat_natural_english.md`（**英文自然さは Claude 主体で担保**・2026-04-29 新設）

このセッションは「カテゴリ1 完了 → カテゴリ2 試走済み → 社長フィードバック前」の状態で前セッションが負荷増のため引継ぎ。

---

## 🟢 確定済み事項（次セッションで揺り戻さない）

### モデル選定
- ✅ **本番候補は OpenAI 3 モデル**：GPT-4.1-Mini / GPT-4o-Mini / GPT-5-Mini
- ❌ **GPT-5-Nano 除外確定**（プロンプト指示を素直に読まない・余計発言の癖が直らず）
- ❌ **Gemini 2.5 Flash 除外確定**（JSON 崩壊が複数回発生・本番で致命的）

### プロンプト構造（`services/baychat/ai/prompt_admin_v2.3_baseline.md`）
社長提示の v2.3 を起点に、以下の **追記のみ**：
1. **Cowatech プレースホルダ**：INPUTS に `{buyerAccountEbay}` `{sellerAccountEbay}` を入力宣言
2. **INPUTS 構造ブロック**：greeting → blank → body → blank → closing → signature を MANDATORY 化
3. **GLOBAL CONVENTIONS**（全トーン共通）：
   - 米国英語ベース
   - **"Hey" 全面禁止**（greeting の casual 上限は "Hi {name},"）
   - "Cheers" は **バイヤーが英国/豪州 marker を使ってきた時のみ**ミラーリング
   - **em dash (—) 全面禁止**
4. **TONE GUIDELINES** 書き直し：
   - POLITE = ビジネス標準CS（"Hello," / "Best regards,"）
   - FRIENDLY = ため口/友人口調（"Hi {name},"・米国系close "Thanks!" "Take care," "Best,"・"Hey"禁止・コーポレート語禁止）
   - APOLOGY = 丁寧以上の配慮（"We sincerely apologize" 等）※実走未検証
5. **CLOSING LINE GUIDANCE**（RESPONSE STRUCTURE 末尾）：
   - 商品**到着前**の closing/gratitude → "feel free to reach out" 系の future-availability close
   - 商品**到着後**の closing/gratitude → "Hope to do business with you again" 系の relationship-forward close
6. **FRIENDLY 限定**：`"serve you again"` / `"We look forward to serving you again"` は POLITE 専用に降格。FRIENDLY では `"Thanks again for choosing us"` / `"Hope to do business with you again"` / `"Take care"` を優先

### 運用ルール（必読）
- ✅ **英文プロンプトの中身を社長に見せない**（社長は留学経験あるが英語専門外）
- ✅ **Claude が複数試行を自律で回し、ベストに近づけてから報告**（一回ずつ社長に判断を仰がない）
- ✅ **英文の自然さ・eBay 米国文脈との整合は Claude 主体で担保**（社長指摘を待たず先回り）
- ✅ **プロンプト追記は最小 5-15 行目安・複雑化させない**（v2.4-v2.6 の轍を踏まない）

### モデル × トーン仮マッピング（カテゴリ1 のみのデータ・要追加検証）
| トーン | 仮の最有力モデル | 根拠 |
|---|---|---|
| POLITE | **GPT-4o-Mini** | コスト最安・標準的丁寧・トーン忠実 |
| FRIENDLY | **GPT-4.1-Mini** | "Hi"主体・米国close・ミラーリング能力最強 |
| APOLOGY | **GPT-5-Mini**（仮） | フォーマル + em dash癖がここでは強み・**ただし em dash 残存リスクあり**（カテゴリ8/9 で実走検証要） |

→ Cowatech に「トーン別モデル切替」を発注するかの判断は **全カテゴリ完了後**。短期は 1 モデル運用継続（4.1-Mini が現本番・速度2秒で安定）。

---

## 📋 カテゴリ1 到達点

- 起点プロンプト：`prompt_admin_v2.3_baseline.md`
- 10 ケース：`testing/test_cases/category_01_post_purchase_thanks.json`
- 最終 HTML（社長レビュー済の状態）：
  - POLITE：`testing/results/comparison_20260429_190601.html`
  - FRIENDLY：`testing/results/comparison_20260429_190604.html`
- 社長最終フィードバック反映済（到着前後の締め方分岐 + serve you again FRIENDLY 回避）
- 残「em dash 残存」は 5-Mini 固有（friendly で 6 件・他 2 モデルはゼロ）→ APOLOGY 振り分け時の留保事項

---

## 📝 カテゴリ2 準備状況（次セッション着手地点）

- 10 ケース：`testing/test_cases/category_02_pre_purchase_qa.json`
- 試走済（GPT 3 モデル × polite + friendly = 60 回）：
  - POLITE：`testing/results/comparison_20260429_190606.html`
  - FRIENDLY：`testing/results/comparison_20260429_190609.html`
- カテゴリ2 内訳：在庫サイズ / 素材 / 新品確認 / カラバリ / 真贋 / 中古状態 / 製造年 / 付属品 / スペック互換 / 追加写真依頼

### カテゴリ2 の特徴的論点（次セッションで検証してほしい）
- **答えるべき情報がプロンプトに無いケース** が多い（在庫・素材・真贋・スペックは商品情報JSON に含まれない）
- AI が **幻覚を起こさない** か（"yes, this is 100% authentic" と勝手に断言しないか等）
- AI が **"確認して折り返します" 系の deferral** に逃げていないか（v2.3 ROLE で禁止済みだが要確認）
- 真贋確認（cat02_05）・中古状態詳細（cat02_06）・非ネイティブ（cat02_09）の **難所3点** の挙動

---

## 🚀 新セッション冒頭の手順

1. このファイル読了
2. memory 2 件読了（feedback_baychat_ai_reply_stance.md / feedback_baychat_natural_english.md）
3. 社長に「カテゴリ2 のレビュー結果（comparison_20260429_190606.html / 190609.html）のフィードバックをお聞かせください」と聞く
4. 社長フィードバック → **Claude 自律で複数試行ループ** → ベストに近づけて HTML 4 枚（cat1 + cat2 / polite + friendly）を社長に提示
5. cat2 完了したら → カテゴリ3（配送関連）へ進める

### テスト実行コマンドテンプレ
```bash
cd services/baychat/ai/testing && python batch_test.py \
  --models gpt gpt4omini gpt5mini \
  --prompt-versions 2.3_baseline \
  --cases test_cases/category_02_pre_purchase_qa.json \
  --production-payload --no-forced-template \
  --tone polite \
  --seller-name rioxxrinaxjapan --description "" --no-judge
# tone=friendly でもう1セット
```

### HTML 化＋オープン
```bash
python render_reply_comparison.py \
  --excel results/test_gpt_gpt4omini_gpt5mini_v2.3_baseline_prodOFF_<タイムスタンプ>.xlsx \
  --cases test_cases/category_02_pre_purchase_qa.json
# render は秒単位タイムスタンプ衝突するので 2 秒間隔で叩く
# 生成された HTML を `start ""` で開く
```

---

## 🟡 留保事項（カテゴリ8/9 直前で再評価）

APOLOGY セクションに以下の eBay 個人セラー文脈での違和感候補があります。**カテゴリ8/9（返品・不良品）実走直前にまとめて社長判断**：

| 箇所 | 現状 | 違和感 | 代替案 |
|---|---|---|---|
| POLITE | "Kindly" 推奨 | 米国eBay では古め | "Please" 主 |
| APOLOGY | "We sincerely apologize" / "We deeply regret" | 法人っぽく重い | "I'm so sorry" / "I really apologize" 主 |
| APOLOGY | "We can only imagine your frustration" | 文学的・スピーチ的 | "I understand how frustrating this must be" |
| APOLOGY | "Yours sincerely," | 英国フォーマル | 米国 "Sincerely," |
| 主語 | "We" 固定 | 個人セラーなら "I" のほうが温かい | 仕様判断 |

---

## 📂 関連ファイル

- 起点プロンプト：[prompt_admin_v2.3_baseline.md](prompt_admin_v2.3_baseline.md)
- カテゴリ1 ケース：[testing/test_cases/category_01_post_purchase_thanks.json](testing/test_cases/category_01_post_purchase_thanks.json)
- カテゴリ2 ケース：[testing/test_cases/category_02_pre_purchase_qa.json](testing/test_cases/category_02_pre_purchase_qa.json)
- カテゴリ全体計画：[testing/category_test_plan.md](testing/category_test_plan.md)
- batch_test：[testing/batch_test.py](testing/batch_test.py)（GPT-4o-Mini を AVAILABLE_MODELS に追加済）
- payload_builder：[testing/payload_builder.py](testing/payload_builder.py)（prompt_version="2.3_baseline" 対応済）
- render_reply_comparison：[testing/render_reply_comparison.py](testing/render_reply_comparison.py)（縦並び `.bilingual { 1fr }` 修正済）
- 旧ハンドオフ（テストリセット時）：[handoff_20260429_test_reset.md](handoff_20260429_test_reset.md)

---

## ⚠️ 後で更新が必要な「ズレ」（次セッションで余裕があれば）

設計図リファクタ後の以下 3 ファイルが古い記述のまま：
- `services/baychat/ai/CLAUDE.md`（v2.6 ドラフト前提）
- `services/baychat/ai/ai-reply-status.md`（v2.6 ドラフト前提）
- `services/baychat/ai/index.md`（22 ファイル前提）

カテゴリ2-3 完了後あたりでまとめて最新化推奨。

---

*作成: 2026-04-29 夕方（カテゴリ1 完了・カテゴリ2 試走済・社長フィードバック前）*
*目的: 新セッションで社長が「続き」と言うだけでカテゴリ2 のフィードバックループに即着手できる状態にすること*
