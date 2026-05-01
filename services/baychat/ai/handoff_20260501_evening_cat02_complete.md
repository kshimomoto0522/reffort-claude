# BayChat AI Reply — カテゴリ2 完成 / カテゴリ3 引継ぎ（2026-05-01 夕）

> **次セッション冒頭でこのファイルを最初に読んでください。**
> 続いて自動ロード対象 memory:
> - `memory/feedback_baychat_ai_reply_stance.md`（5原則）
> - `memory/feedback_baychat_natural_english.md`（英文自然さ）
> - `memory/feedback_baychat_ai_80point_principle.md`（80点原則）
> - `memory/feedback_role_identity.md`（Reffort 一従業員）

---

## 🟢 今日の到達点（2026-05-01）

カテゴリ2（購入前Q&A）テストを **cat02_03/05/06/07/08（社長指摘5ケース）+ cat02_11〜20（追加10ケース・うち5つは複数メッセージ）= 計15ケース** で完成。社長フィードバック 6点（A〜F）を全解消し、社長OK判定をいただきました。

### 最終プロンプト：`prompt_admin_v2.3_baseline_natural3.md`（iter 8）

iter 1〜8 の試行錯誤の経過：

| iter | 自己評価 | 主要改修 |
|---|---|---|
| iter 1 (natural) | 73% | アイデンティティ駆動・c2 FACT GROUNDING全廃 |
| iter 2 (natural2初版) | 77% | HARD RULE強化＋スリム化 |
| iter 3 | 87% | 状態断言禁止・内部ロジック禁止強化 |
| iter 4 | 93% | メタ発言全面禁止・sweeping判定禁止 |
| iter 5 | 91/93% | **「the listing X」型他人事構文の全面禁止 + 1人称アクション型強制** |
| iter 6 (natural3初版) | 多数改善 | 社長フィードバックABCDEF反映＋スリム化 |
| iter 7 | 96%クリーン | Accessories「写真参照型」強化・物理状態断言禁止強化・negative service 禁止 |
| **iter 8** | **100%クリーン** ⭐ | 内部ロジック暴露の追加禁止例（"I will not use absolute phrases"型） |

### 社長フィードバック ABCDEF → 全解消

| # | 社長指摘 | iter8 状況 |
|---|---|---|
| A | 付属品の有無は「商品画像が唯一の真実」型 | ✅ 全モデル達成 |
| B | Stage 1 では opening phrase **必須** | ✅ "Thank you for your inquiry." を全モデルで挿入 |
| C | ハンドリングタイム vs 配送日数の区別 | ✅ "X business days for handling" + "transit X-Y business days" |
| D | 「ない／できない」決めつけも捏造 | ✅ "may be possible — please tell me which items"型 |
| E | listing data `ShippingService` が唯一の真実 | ✅ 全モデルで正確に引用（テスト環境において） |
| F | 日本語訳の自然さ（4o-Mini対策） | ✅ JAPANESE TRANSLATION QUALITY セクション追加 |

### 速度（社長目標との比較・iter8）

| モデル | iter5 平均 | **iter8 平均** | 標準目標3秒 | 複雑目標6秒 |
|---|---|---|---|---|
| GPT-4.1-Mini | 5.18s | **3.86s** ⭐(-26%) | 🟡 近接 | ✅ |
| GPT-4o-Mini | 4.92s | **3.46s** ⭐(-30%) | 🟡 近接 | ✅ |
| GPT-5-Mini | 6.72s | 7.03s | 🔴 | 🔴 |

プロンプト本体：natural2 (iter5) 26241字 → **natural3 (iter8) 22323字（-15% スリム化）**

---

## 🚫 重要決定：GPT-5-Mini を本番モデル候補から除外（2026-05-01）

社長判断により、**GPT-5-Mini は本番モデル候補から外す**：
- 余計なことを言い過ぎる癖
- コントロールが難しい
- 推論モデル特性で速度も遅い（複雑目標 6秒未達）

### 本番モデル候補（残り）
- **GPT-4.1-Mini**（標準目標近接）
- **GPT-4o-Mini**（標準目標近接）

### 5-Mini 最終確認テスト（cat03 で実施予定）
社長許可：「トラブル・クレーム対応カテゴリ等で念の為一度テストしてみてもいいかと思いますが、外してOK」
→ cat03 で APOLOGY トーンを含むテスト時、5-Mini も走らせて最終挙動確認。それで完全除外。

---

## 🚢 shipping policy 反映の現状認識と将来課題

### 現状（社長確認済み）

| 環境 | `ShippingService` の値 | 備考 |
|---|---|---|
| **本番**（gpt_api_payload.txt） | `"US_ExpeditedSppedPAK"` 等 eBay 内部コード | 出品時設定の shipping policy がそのまま反映 |
| **テスト環境**（私が仮設定） | `"FedEx International Priority"` `"DHL Express"` `"EMS International"` 等 human-readable | 仮設定。AI は人間可読の値を見て返答できる |

社長判断：**「本番ではポリシー通りの内容が反映される、テストは仮設定でOK。一旦OK」**。

### 将来課題：SpeedPAK の業者特定（社長提案）

eBay SpeedPAK は eBay の独自配送サービスブランド名で、実体は eBay が契約している業者。社長提供情報：

| SpeedPAK サービス | 実体の業者 | AI回答方針 |
|---|---|---|
| **eBay SpeedPAK Expedited** | FedEx または DHL | 「FedEx か DHL のいずれかで発送します」と回答 |
| **eBay SpeedPAK Standard** | FedEx または DHL | 同上 |
| **eBay SpeedPAK Economy** | 日本郵便 | 「日本郵便で発送します」と回答 |

実装案：
- (A) Cowatech 側で eBay コード → human-readable 名へ変換してから AI に渡す
- (B) admin_prompt に SpeedPAK 業者対応辞書を埋め込む（プロンプト膨張するが Cowatech 改修不要）

cat03（配送関連）で **Bが適切**と判断する場合、admin_prompt にこの辞書を組み込む方向。社長判断あり。

### DispatchTimeMax の本番未配置

本番ペイロードに `DispatchTimeMax` フィールドは含まれていない（gpt_api_payload.txt で 0 件）。テスト環境にだけある。
本番で AI に handling time を答えさせる場合、Cowatech 側で listing データに含めるよう仕様追加が必要。

---

## ⏱ 速度・補足情報テストの課題

社長指摘：「補足情報を入れると 10秒以上かかる場合がある」

### 原因
- **3モデル順次実行**（並列化していない）→ 補足情報なしでも合計 10-20秒
- 補足情報でプロンプト容量増 → 各モデル個別の生成時間も延びる

### 改善案（将来）
1. **3モデル並列化**（`asyncio.gather` または ThreadPoolExecutor で同時実行）
2. **5-Mini 除外で 3モデル → 2モデル化**（合計時間 -33%）
3. **プロンプトさらにスリム化**（今 22323字 → 17000字目標は可能）
4. **補足情報自体の長さ短縮ガイド**（社長運用側）

優先度：**(2) 5-Mini 除外**は決定済 → 即適用可能。次セッション以降のテストは 4.1-Mini と 4o-Mini のみで走らせれば 2モデル並列実行で 3-5秒台に収まる見込み。

---

## 📂 関連ファイル

### 最新プロンプト
- 起点：`services/baychat/ai/prompt_admin_v2.3_baseline.md`
- 中間派生：`services/baychat/ai/prompt_admin_v2.3_baseline_natural.md` (iter1)
- 中間派生：`services/baychat/ai/prompt_admin_v2.3_baseline_natural2.md` (iter2-5)
- **最新**：`services/baychat/ai/prompt_admin_v2.3_baseline_natural3.md` (iter6-8) ⭐

### テストインフラ
- バッチテスト：`services/baychat/ai/testing/batch_test.py`（xlsx_safe sanitizer 追加済）
- ペイロードビルダー：`services/baychat/ai/testing/payload_builder.py`
- 比較HTMLレンダラー：`services/baychat/ai/testing/render_reply_comparison.py`（補足情報UI + 再生成ボタン搭載）
- 再生成APIサーバー：`services/baychat/ai/testing/result_server.py`（Flask, port 8765）
- サーバー起動：`services/baychat/ai/testing/start_result_server.bat`

### cat02 テストデータ
- 旧5ケース（社長最初の指摘）：`testing/test_cases/category_02_natural5_subset.json`
- 追加10ケース（5 single + 5 multi-message）：`testing/test_cases/category_02_additional10.json`

### cat02 最終比較HTML（社長OK判定済）
- POLITE subset5: `testing/results/comparison_polite_20260501_170121.html`
- FRIENDLY subset5: `testing/results/comparison_friendly_20260501_170122.html`
- POLITE add10: `testing/results/comparison_polite_20260501_170122.html`
- FRIENDLY add10: `testing/results/comparison_friendly_20260501_170123.html`

---

## 🚀 次セッション（cat03）で着手すべきこと

### A. cat03 設計
カテゴリ3 = **配送関連 / 購入後質問**（categori_03_post_purchase_shipping_qa 想定）
- 出荷確認・トラッキング問い合わせ
- 配送遅延・到着前不安
- 受け取り後の付属品/状態相違指摘（軽微）
- 関税・通関問題

10ケース新規作成：
- single message 5 + multi-message 5 の構成（cat02 と同じ）
- 商材バラエティ確保
- 必要に応じて Stage 2/3 を混ぜる

### B. cat03 テストの本番モデルを 4.1-Mini と 4o-Mini に絞る
- batch_test の `--models gpt gpt4omini` で実行
- **5-Mini は最初の1ラウンド（POLITE）でだけ参考実行 → APOLOGY 系で挙動確認 → その後完全除外**
- 速度がほぼ目標達成見込み

### C. SpeedPAK 業者対応辞書の admin_prompt 組み込み判断
- cat03 = 配送なので shipping 関連の質問が多い
- 「お客様、SpeedPAK で出荷されました」だけだと業者不明 → バイヤー混乱
- admin_prompt SHIPPING DATA SOURCES セクションに辞書を追加するか、事前 Cowatech 仕様書追加か社長判断

### D. APOLOGY トーンの最終確認
cat02 では POLITE と FRIENDLY のみテスト。cat03 では APOLOGY も走らせる：
- 配送遅延での謝罪
- 商品破損での謝罪
- 5-Mini 含めて参考挙動も見る（cat03 で 5-Mini 完全除外判断）

### E. 速度改善の検討
- batch_test の並列化（3モデル → asyncio で同時実行）
- 5-Mini 除外で 2モデル化
- admin_prompt 更なるスリム化（natural3 22323字 → 17000字目標）

---

## 🟡 進行中・継続事項

### 補足情報テスト（社長運用）
- 比較HTMLには「🎯 補足情報（sellerSetting）」枠 + 「🔁 補足込みで再生成（3モデル）」ボタンあり
- result_server.py を起動すれば動作（次セッションで社長が「テストする」と言ったら起動）
- 起動コマンド：`python services/baychat/ai/testing/result_server.py`

### Cowatech 反映
- 現在本番で動いているのは v2.4
- natural3 系の改修を本番反映するには Cowatech に admin_prompt 更新依頼が必要
- 反映タイミングは社長判断（cat03 まで詰めてから一括反映 or cat02 完了で先行反映）

### 数量関連2ケース（Cowatech 修正待ち）
- cat02_01（サイズ availability）/ cat02_04（カラー variant）
- `Item.Quantity` / `Variations[].Quantity` が累計販売数を返している問題
- Slack スレッド：`https://reffort.slack.com/archives/C09KXK26J8G/p1777463205330029`
- Cowatech 修正反映後に再走

---

## 💴 cat02 全試行のコストサマリ

| iter | テスト走行数 | コスト |
|---|---|---|
| iter 1〜5（natural→natural2）| 約8回 | 約 ¥45 |
| iter 6〜8（natural3）| 8回（subset5 + add10 × 2tone × 2 iter） | 約 ¥38 |
| **合計** | | **約 ¥83** |

iter1〜5 で社長指摘5ケース（subset5）試行錯誤、iter6〜8 で 15ケース全体テスト。

---

## ✏️ memory / CLAUDE.md 更新（このセッション中に実施済）

- `memory/decisions_log.md` ：「5-Mini 本番除外決定」追記済
- `services/baychat/ai/CLAUDE.md` ：モデル仮決定セクション更新済（4.1/4o-Mini 候補・5-Mini 除外）
- `/CLAUDE.md` トップ：次セッション冒頭読むファイル指定を本ハンドオフに更新済
- `education/consulting/journey-log.md` ：今日の作業記録追記済

---

*作成: 2026-05-01 夕（cat02 全15ケース完成・社長OK判定・iter8 で品質100%・5-Mini 本番除外決定）*
*目的: 翌セッションで社長が「cat03 始めよう」と言うだけで即着手できる状態*
