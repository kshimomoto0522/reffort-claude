# BayChat AI Reply — natural5_lean (iter11) 完成 / 次セッション引継ぎ（2026-05-05 夜）

> **次セッション冒頭でこのファイルを最初に読んでください。**
> 続いて自動ロード対象 memory:
> - `memory/feedback_baychat_ai_reply_stance.md`（5原則）
> - `memory/feedback_baychat_ai_80point_principle.md`（80点原則）
> - `memory/feedback_role_identity.md`（Reffort 一従業員）

> ⚠️ **プロンプト改修する前に必読**: `services/baychat/ai/_reffort_internal/prompt_construction_rules.md`（永続メタルール・本日新設）

---

## 🟢 本日（2026-05-05）の到達点

### 重要な方針転換：**原則ベース**へ抜本書き直し
- 起点: 社長指摘「『この場合こう言え』が強くなり過ぎている／ルール過多はNG／AIに考えさせる」
- 結果: **prompt_admin_v2.3_baseline_natural5_lean.md（iter 11）** 完成

### サイズ圧縮
- natural3_assertive (iter9): 約 660 行
- natural4_principle (iter10): 約 750 行（**レシピ積み上げに戻った失敗版**）
- **natural5_lean (iter11): 約 280 行**（natural4比 -63%）
- input トークン量も比例して削減 → コスト約 -50%

### 構造（natural5_lean）
```
1. ROLE & VOICE
2. CONVERSATION STAGE DETECTION
3. SELLER INTENT
4. CORE PRINCIPLES (10個・思考の軸)
   1: WE ARE THE SELLER
   2: DON'T FABRICATE — both directions
   3: WE INVESTIGATE BEFORE DEFLECTING
   4: DON'T DECREE WITHOUT FACTS
   5: READ THE CONVERSATION HISTORY
   6: APPLY COMMON SENSE — AND DON'T MAKE SELLER DECISIONS
   7: TONE IS VOICE, FACT IS FACT
   8: MATCH AUTHORITY TO TOPIC
   9: CONFIRM OUR OWN ACTIONS
   10: DON'T HEDGE OUR OWN INTENT
5. HARD RULES (5個・絶対禁止)
   (1) AUTHENTICITY
   (2) NO FABRICATION (positive AND negative)
   (3) NO FUTURE PROMISES
   (4) NO FAKE eBay POLICIES（境界線明確化）
   (5) NO DEFAULT EXTRA-WORK
6. SHIPPING DATA SOURCES
7. INVENTORY / QUANTITY
8. TONE GUIDELINES (4トーン・voice 違いのみ)
9. RESPONSE STRUCTURE
10. INPUTS
11. FINAL CHECK (A)〜(M)（原則の再掲のみ）
```

### 失敗の経緯（学び）
1. natural4_principle (iter10) で「原則ベース転換」を宣言したが、cat03 テスト失敗を見るたびに「CONCRETE FORBIDDEN PATTERNS」「TOPIC→AUTHORITY マッピング」「BEFORE/AFTER shipment マトリクス」を追加し続けた
2. 結果として、ラベルだけ「PRINCIPLE」で、中身はレシピ積み上げの失敗版に
3. 社長から「方向性無視してまた改善前のことをやり始めた」と指摘
4. natural5_lean で根本書き直し

**この再発を防ぐため `prompt_construction_rules.md` を新設**（社長指示「プロンプト構成のルールを徹底してくれ」）。次のセッション以降、改修前に必ず読む。

---

## 📊 cat03 テスト結果（natural5_lean / iter11c）

### スコア早見表（POLITE × 全10ケース）

| Case | GPT-4.1 | GPT-4o-Mini | 社長フィードバック対象 |
|---|---|---|---|
| cat03_01 shipped_yet | 23 | 24 | ✅ 確定形（「currently being prepared」） |
| cat03_02 tracking_not_upd | 24 | 23 | - |
| cat03_03 delivery_overdue | 25 | 22 | ✅ 投げやり解消（「I will check with the carrier」） |
| cat03_04 customs_held | 23 | 23 | ✅ 状況確認先行（決めつけ消失） |
| cat03_05 missing_accessory | 19 | 18 | △ 社長指摘外・継続課題 |
| cat03_06 customs_question | 22 | 25 | ✅ TO/FROM/closing 完備 |
| cat03_07 tracking_stuck | 25 | 25 | ✅ eBay公式振り解消 |
| cat03_08 carrier_redirect | 23 | 23 | - |
| cat03_09 box_damaged | 22 | 24 | - |
| cat03_10 address_change | 21 | 19 | ✅ cancel + re-purchase 案内（fake policy 解消） |
| **平均** | **22.7** | **22.6** | |

### 4トーン平均比較

| トーン | iter9 (natural3) | iter10 (natural4) | iter11c (natural5_lean) |
|---|---|---|---|
| POLITE (10ケース) | 21.8 | 22.3 | **22.6** |
| FRIENDLY (10ケース) | 21.0 | 22.2 | 21.3 |
| APOLOGY (4ケース) | 20.5 | 22.0 | 22.8 |
| ASSERTIVE (3ケース) | 18.5 | 19.5 | 18.3 |

### 社長フィードバック・クリア状況（cat03 POLITE）

| 指摘 | iter11c 状況 |
|---|---|
| cat03_01「発送準備中かもしれません」NG | ✅ 「currently being prepared」 |
| cat03_03 投げやり禁止 | ✅ 「I will check with the carrier and get back」 |
| cat03_04 状況確認なしの決めつけNG | ✅ 「Could you share what the customs notice says?」 |
| cat03_06 TO/FROM/署名フォーマット | ✅ 全 closing/signature 完備（FORCED_TEMPLATE と併用） |
| cat03_07 eBay公式振りNG | ✅ 「I will check with the carrier」 |
| cat03_10 キャンセル→再購入の標準対応 | ✅ 「cancel the current order and place a new one」 |
| cat03_13 ASSERTIVE「international shipping framework」誤用 | ✅ FACTUAL ORDER HISTORY ベース |
| cat03_13 「eBayの公式手続き」抽象表現 | ✅ Item Not Received case 等具体名 |
| cat03_13 配送済み案件のキャンセル提案 | ✅ 全トーンでキャンセル提案ゼロ |

---

## 📂 開く HTML（次セッション最初に確認）

| ファイル | 内容 |
|---|---|
| `testing/results/comparison_polite_20260505_211104.html` | cat03 全10ケース POLITE（iter11c） |
| `testing/results/compare_3tone_20260505_211103.html` | cat03_11/12/13 × 3トーン横並び（POLITE/APOLOGY/ASSERTIVE） |

---

## ⚠️ 残課題（次セッションで対応・優先度順）

### 🔴 高: cat03_05 保証書欠品ケース
- 全トーンで低スコア（13-20）
- 社長フィードバック明示外
- 構造的問題：「写真の保証書が箱にない、確認してくれ」に対し AI が決定的回答を出せない
- 検討案: 「写真と異なる場合は写真の通り再送/返金で対応」型ロジック検討

### 🟡 中: cat03 FRIENDLY/ASSERTIVE のスコア低下
- FRIENDLY: 22.2 → 21.3（-0.9）
- ASSERTIVE: 19.5 → 18.3（-1.2）
- 原因: prompt 圧縮により voice の違いが薄れた可能性
- 検討案: TONE GUIDELINES の voice 例文を最小限追加（**ただし prompt_construction_rules.md ルール B 適用 = レシピ追加判定基準を満たすか吟味**）

### 🟡 中: cat02_05 / cat02_10 の negative denial
- 「we do not have extra photos」「I cannot provide」が残る
- iter9 でも同じ表現があった可能性（社長 OK 判定の許容範囲）
- 検討案: 原則 2 の言葉を強める（レシピ追加ではない）

---

## 📋 自動ロード対象の更新（CLAUDE.md 参照）

### 新規ファイル
- `services/baychat/ai/prompt_admin_v2.3_baseline_natural5_lean.md` — **本日採用版（iter11c）**
- `services/baychat/ai/_reffort_internal/prompt_construction_rules.md` — **永続メタルール（プロンプト改修前必読）**
- `services/baychat/ai/handoff_20260505_natural5_lean_complete.md` — **本ファイル**

### 旧版（archive 候補）
- `prompt_admin_v2.3_baseline_natural3_assertive.md` (iter9)
- `prompt_admin_v2.3_baseline_natural4_principle.md` (iter10 失敗版)
- `handoff_20260505_assertive_complete.md`（朝の引継ぎ・上書きされた）

→ 次セッション初頭で archive 移動 or 削除判断。

---

## 🟡 進行中・継続事項

### Cowatech 主張トーン実装
- 工数・コスト見積を Slack で受領待ち
- 次セッションで Cowatech 側の admin_prompt を natural5_lean に差し替える依頼検討

### eBay Shipment history API 取込（社長「絶対必要」判定済み）
- 本ファイル `Phase C: Cowatech向け仕様書「eBay Shipment history API取込」` として骨子作成予定だったが、natural5_lean の改修が優先されたため未完了
- 次セッションで仕様書骨子作成 → Cowatech 送付検討

### 保留タスク
- SpeedPAK 業者対応辞書（cat03 完了後再着手・社長Q1〜Q4回答待ち）
- 補足欄プリセットボタン（実運用テスト中に再検討）
- 要約モード仕様検討（cat03 完了後の課題）

---

## 🎯 次セッション冒頭の流れ（推奨）

1. **このファイル**を読んで本日の状況把握
2. `services/baychat/ai/_reffort_internal/prompt_construction_rules.md` を読む（プロンプト構成永続ルール）
3. 開いている HTML 2つを社長と一緒に確認
4. 社長判定 → 残課題のうち優先度を決定
5. cat03_05 / cat03 FRIENDLY/ASSERTIVE / Cowatech 仕様書 のいずれから着手するか確認

### 改修する場合の手順
- prompt_construction_rules.md ルール A〜J を必ず参照
- レシピ追加は最後の手段。まず原則の言葉を強める
- 改修したら natural5_lean ファイル末尾のバージョン履歴に記載

---

*作成: 2026-05-05 21:11（natural5_lean 完成・社長指摘 6 ケース全クリア・280 行に圧縮・原則ベース転換成功）*
