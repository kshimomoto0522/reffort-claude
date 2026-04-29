# BayChat AI Reply — テスト方針リセット 引継ぎ（2026-04-29 作成 / 2026-04-30 朝に読む）

> 新セッション冒頭でこのファイルを最初に読むこと。次に `memory/feedback_baychat_ai_reply_stance.md`（5原則）を読む。

---

## 🔴 何が変わったのか（一文）

社長指示で **v2.4 〜 v2.6 のドラフトをすべて破棄**し、**v2.3 + Cowatech プレースホルダ最小反映** をテスト起点（`prompt_admin_v2.3_baseline.md`）として、対応カテゴリ別に 10 ケース → 社長フィードバック → 必要なら +5 → 次カテゴリ、というループでテスト再開する。

社長の根本問題意識：「Claudeが意向を汲まずに改修した結果、プロンプトが複雑化していて、生成結果に対するフィードバックがしづらい（カテゴリが入り交ざっているから）」。

---

## ✅ 2026-04-29 夜までに整備したもの

| 整備物 | 場所 | 内容 |
|---|---|---|
| 🆕 起点プロンプト | [prompt_admin_v2.3_baseline.md](prompt_admin_v2.3_baseline.md) | v2.3 と完全同じ本文に、INPUTS セクションへ `{buyerAccountEbay}` `{sellerAccountEbay}` の入力宣言と「空なら省略」の 2 段落のみ追記 |
| 🆕 カテゴリ分類案 | [testing/category_test_plan.md](testing/category_test_plan.md) | 基本→複雑順に 10 カテゴリ提示（明日朝の社長判断対象） |
| 🆕 カテゴリ 1 の 10 ケース | [testing/test_cases/category_01_post_purchase_thanks.json](testing/test_cases/category_01_post_purchase_thanks.json) | 購入直後の挨拶・感謝・closing 系。STAGE 1 が 3 件 / STAGE 2 が 7 件、商品ジャンル分散、英語ネイティブ＋非ネイティブ、感情も分散 |
| 🛠 payload_builder.py 拡張 | [testing/payload_builder.py](testing/payload_builder.py) | `prompt_version="2.3_baseline"` で v2.5 と同等の挙動（FORCED_TEMPLATE 除去 + `{buyerAccountEbay}`/`{sellerAccountEbay}` 置換）を追加 |

batch_test.py は既存のまま。`load_prompt_from_md("2.3_baseline")` で `prompt_admin_v2.3_baseline.md` を自動的に読む。

---

## 🌅 明日朝、社長と Claude が一緒に確認すること（最小 3 点）

### ① カテゴリ分類は 10 案で良いか

`testing/category_test_plan.md` の表を見て：

- **粒度**は妥当か（細かすぎ／粗すぎ）
- **順序**は基本→複雑になっているか
- **取捨**：要らないカテゴリ・足りないカテゴリは無いか

### ② カテゴリ 1 の 10 ケースを開いて偏りが無いか確認

`testing/test_cases/category_01_post_purchase_thanks.json` の 10 件を社長が一読。

- 同じパターンが続いていないか
- リアルな問い合わせとして無理は無いか
- 商品ジャンルの分散は OK か

### ③ テスト実行のモデル × トーンをどうするか

提案：

| ラウンド | モデル | トーン | ケース | 目的 |
|---|---|---|---|---|
| 1st（必須） | gpt5nano | polite | 10 件 | ベースラインの基本動作確認 |
| 2nd（必要なら） | gpt5nano | friendly | 同 10 件 | トーン切り替え時の挙動確認 |

→ 1st だけで十分なら 1st のみ実行。

---

## 🚀 GO 後のテスト実行ワンライナー

cd は不要（PowerShell からも bash からも動く前提）。

### 1st ラウンド（polite）

```bash
cd services/baychat/ai/testing && python batch_test.py \
  --models gpt5nano \
  --prompt-versions 2.3_baseline \
  --cases test_cases/category_01_post_purchase_thanks.json \
  --production-payload \
  --no-forced-template \
  --tone polite \
  --seller-name rioxxrinaxjapan \
  --description "" \
  --no-judge
```

`--no-judge` はAI採点をスキップ（社長フィードバック中心の運用なので採点ノイズを排除）。判断材料に欲しければ `--no-judge` を外す。

### 2nd ラウンド（friendly・必要なら）

`--tone polite` を `--tone friendly` に変更して再実行。

### 結果 → 社長レビュー HTML

```bash
python render_reply_comparison.py \
  --excel results/test_gpt5nano_v2.3_baseline_prodOFF_<タイムスタンプ>.xlsx \
  --cases test_cases/category_01_post_purchase_thanks.json
```

→ `results/comparison_<タイムスタンプ>.html` がブラウザで開ける状態になる（**Claude が `start ""` で自動オープン**するルール）。

### 社長フィードバック → 次サイクルへ

- HTML 内の textarea に各ケースのフィードバックを記入
- 「全フィードバックをJSONダウンロード」ボタンで JSON を保存
- そのJSONを Claude に渡せば、`prompt_admin_v2.3_baseline_c1.md`（カテゴリ 1 反映版）の **最小修正案** を Claude が起こす

---

## ⚠️ Claude が絶対に守ること（5原則 + 今回の追加 1 点）

memory `feedback_baychat_ai_reply_stance.md` の **5原則** に加えて、今回限定で：

> **6. プロンプト修正は「そのカテゴリで合意した最小行（5-15 行以内目安）」だけ。複数カテゴリの修正を一度に混ぜない。**

これが破られた瞬間、また「複雑化していて何のテストかわからない」状態に逆戻りする。社長から「複雑になり過ぎ」と指摘されたら即停止して相談。

---

## 📂 関連ファイル（このハンドオフから到達できるもの）

- 起点プロンプト: [prompt_admin_v2.3_baseline.md](prompt_admin_v2.3_baseline.md)
- v2.3 原本（参照用）: [prompt_admin_v2.3.md](prompt_admin_v2.3.md)
- 破棄したドラフト（参考のみ・採用しない）: `prompt_admin_v2.4.md` / `v2.5.md` / `v2.6.md` / `.html` / `.json`
- カテゴリ計画: [testing/category_test_plan.md](testing/category_test_plan.md)
- カテゴリ 1 ケース: [testing/test_cases/category_01_post_purchase_thanks.json](testing/test_cases/category_01_post_purchase_thanks.json)
- ペイロードビルダー: [testing/payload_builder.py](testing/payload_builder.py)
- バッチ実行: [testing/batch_test.py](testing/batch_test.py)
- レビュー HTML 生成: [testing/render_reply_comparison.py](testing/render_reply_comparison.py)
- Cowatech プレースホルダ実装の経緯: [handoff_20260423_cowatech_prd_sync.md](handoff_20260423_cowatech_prd_sync.md)
- 前ハンドオフ（v2.6 テスト完了時点）: [handoff_20260422_v2.6_test_complete.md](handoff_20260422_v2.6_test_complete.md)

---

## 📝 後で更新が必要な「ズレ」（今回は意図的に放置）

明日のテスト着手を最優先したため、以下 3 ファイルの記述が **古い 22 ファイル設計図前提のまま** になっている。テスト 1 周（カテゴリ 1〜2 完了）後に最新化する：

- `services/baychat/ai/CLAUDE.md`（v2.6 ドラフト前提・要更新）
- `services/baychat/ai/ai-reply-status.md`（v2.6 ドラフト前提・要更新）
- `services/baychat/ai/index.md`（22 ファイル前提・要更新）

---

*作成: 2026-04-29 夜（社長帰宅前 / 翌朝のテスト開始用）*
*目的: 2026-04-30 朝、社長が起きたら即「カテゴリ確認 → テスト実行 → フィードバック」へ進める状態にしておくこと。*
