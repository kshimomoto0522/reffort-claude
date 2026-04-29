# AI Reply カテゴリ別反復テスト計画
> 作成日: 2026-04-29
> 起点プロンプト: `prompt_admin_v2.3_baseline.md`（v2.3 + Cowatech プレースホルダ最小反映のみ）
> 目的: 対応カテゴリを基本→複雑の順に絞り、1 カテゴリ 10 ケース → 社長フィードバック → 必要なら +5 → 次カテゴリ、というループで段階的に改修する。

---

## 反復ループの 1 サイクル

```
[A] 1 カテゴリ × 10 ケース合成（同カテゴリ内で偏り出ないように）
       ↓
[B] AI Reply 生成（payload_builder で本番再現・admin_prompt は最新ベースライン）
       ↓
[C] 社長レビュー HTML（カテゴリ単位）→ ケースごとにフィードバック
       ↓
[D] 社長判断
     ├─ 同カテゴリ +5 ケースで再テスト  → [B] に戻る
     └─ 次カテゴリへ進む  → [A] に戻る
       ↓
[E] フィードバックを踏まえてプロンプト派生版を作成
     例: prompt_admin_v2.3_baseline_c1.md（カテゴリ 1 反映後）
```

派生版は **そのカテゴリで合意した最小修正のみ** を加える。複数カテゴリの修正を一度に混ぜない（v2.4-v2.6 で繰り返した複雑化を防ぐため）。

---

## カテゴリ分類案（Claude 提案・社長判断待ち）

eBay CS の実務カテゴリを「シンプル → 複雑」「平和 → トラブル」順で並べた **10 カテゴリ案**。

| # | カテゴリ | バイヤー側のメッセージ例 | 想定 STAGE / TYPE | 期待される対応の難易度 |
|---|---|---|---|---|
| 1 | **購入直後の挨拶・感謝・closing 系** | "Thanks!" / "Just bought, looking forward" / "Have a great day" | STAGE 1 or 2 / 短文 closing 系 | 低（短く温かく返すだけ） |
| 2 | **商品の事前質問（在庫・サイズ・素材・状態）** | "Do you have size 9?" / "Is this real leather?" / "Is this brand new?" | STAGE 1 中心・プリパーチェス | 低〜中 |
| 3 | **配送関連（送料・配送日数・配送可否）** | "Do you ship to Italy?" / "How many days does shipping take?" | STAGE 1 中心・プリパーチェス | 中 |
| 4 | **ベストオファー・価格交渉** | "Would you accept $80?" / "Any chance for a discount?" | STAGE 1 or 2 | 中（「補足なし」のとき判断が分かれる） |
| 5 | **注文後の確認・変更・キャンセル依頼** | "Can you ship to a different address?" / "I want to cancel" | STAGE 1 or 2 / 出荷前 | 中 |
| 6 | **配送中の追跡・遅延問い合わせ** | "Where is my order?" / "Tracking shows nothing" | STAGE 1 or 2 / in-transit | 中 |
| 7 | **関税・税金・到着後の通常質問** | "Customs charged me" / "Is this the right size?" | STAGE 1 or 2 / post-arrival | 中 |
| 8 | **返品リクエスト（理由：サイズ違い・気に入らない等）** | "It doesn't fit, can I return?" / "Wrong size sent?" | STAGE 1 or 2 / post-arrival | 中〜高（補足の有無で対応が変わる） |
| 9 | **不良品・破損・誤発送対応** | "Arrived damaged" / "Wrong item received" / "Defect found" | STAGE 1 or 2 / 謝罪トーン要 | 高（謝罪 + 解決提示） |
| 10 | **ディスピュート・激怒・偽物クレーム等の重対応** | "Opening dispute" / "This is fake!" / "You're a scammer" | STAGE 2 or 3 / 重圧 | 最高 |

### カテゴリ順序の根拠

- **1 → 3** は「平和な問い合わせ・短文返信」が中心で、プロンプトの基本動作を確認する初期段階に最適
- **4 → 7** は「判断が要るが基本トーンは保てる」中間層
- **8 → 10** は「謝罪／重大対応／センシティブ」で、プロンプトの限界が出やすい層

カテゴリ番号は基本→複雑の **テスト順序** とイコール。

---

## 社長明日朝の判断ポイント（最小限）

1. **カテゴリ分類は上の 10 案で良いか？**（粒度・順番・取捨）
2. **ケースは合成 / DB 抽出 のどちらで進めるか？**
   - 合成 ＝ Claude がパターン多様性を担保しやすい・短時間で 10 ケース揃う
   - DB 抽出 ＝ 実会話そのまま・代表性は高いがカテゴリ判定とノイズ除去が必要
   - **推奨：合成スタート（カテゴリ 1）／後でズレを感じたら DB 抽出に切替**
3. **テスト時のモデルは GPT-5-Nano 1 本で良いか？**（admin 切替予定モデル・コスト最小・速度十分）
   - 必要なら後で GPT-4.1-Mini と並走可能

---

## カテゴリ 1 で確認したい点（Claude 仮置き）

カテゴリ 1（購入直後の挨拶・感謝・closing 系）でプロンプトが出すべき挙動：

- STAGE 1 の「Just bought, thank you!」 → 短く・温かく・「Thank you for your message」または「Thank you for your inquiry」始まり
- STAGE 2 の「Thanks again!」 → 「Thank you for your message」を **使わない** ／ 短い acknowledgement
- 過剰なフォーマル化（"Best regards, [seller_name]" のフル装備）にしない
- 既出情報を再説明しない
- 署名は `{sellerAccountEbay}` が空なら省略・あれば 1 行

ここでプロンプトが過剰な定型句を出してくるなら、カテゴリ 1 反映版で「短文 closing 時の振る舞い」を最小限追記する。

---

## ファイル命名規約

| フェーズ | プロンプトファイル名 | テストケースファイル名 | 結果 HTML 名 |
|---|---|---|---|
| 起点 | `prompt_admin_v2.3_baseline.md` | `test_cases/category_01_post_purchase_thanks.json` | `results/category_01_baseline_YYYYMMDD_HHMMSS.html` |
| カテゴリ 1 反映後 | `prompt_admin_v2.3_baseline_c1.md` | `test_cases/category_02_pre_purchase_qa.json` | `results/category_02_after_c1_YYYYMMDD_HHMMSS.html` |
| カテゴリ 2 反映後 | `prompt_admin_v2.3_baseline_c1c2.md` | `test_cases/category_03_shipping.json` | `results/category_03_after_c1c2_YYYYMMDD_HHMMSS.html` |
| ... | ... | ... | ... |

派生版の差分は **追記行数 5-15 行以内** を上限の目安に。それを超える要望が出たら、社長と「カテゴリ分け自体を見直すべきか」を再協議する。
