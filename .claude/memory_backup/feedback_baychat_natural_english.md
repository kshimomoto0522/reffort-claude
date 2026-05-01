---
name: BayChat AI Reply の英文自然さは Claude 主体で担保（社長英語スキル前提にしない）
description: プロンプトに反映する英語表現は Claude が責任を持って eBay 文化・米国英語の慣習に照らして自然か検証する。社長の英語チェックに頼らない。
type: feedback
originSessionId: 2026-04-29-tone-review
---
# BayChat AI Reply 英文自然さの担保ルール

## 背景（2026-04-29 社長指摘）

> 「わたしは留学経験があり多少の英語がわかるのでこのような違和感に気づきますが完璧にわかるわけではありません。なのであなたが反映しましたと言われたらその英語が適切だと基本的に思わざるを得ません。
> わたしに突っ込まれなくても eBay の自然なトーンに合わせた英文になるようにプロンプト作成を徹底してください。」

社長は留学経験があり一定の英語感覚はあるが、ネイティブの違和感まで完全には拾えない。Claude が「反映しました」と報告すると、社長はその英語表現が適切だと信じざるを得ない構造になっている。

## 違反例（同日に社長から指摘を受けた事例）

| Claude が反映した表現 | 社長指摘の違和感 | 真の問題 |
|---|---|---|
| "Hey {name}!" を FRIENDLY の greeting 候補に | 「Heyを使うCSはあるか？」 | "Hey" は CS としては失礼に響くため業務範囲外。"Hi" が casual の上限 |
| "Cheers,"を FRIENDLY の close 候補に | 「Cheersはアメリカ英語でよく使われる？」 | "Cheers" は英国/豪州英語。米国eBayでは違和感 |
| "We look forward to serving you again" | 「serve you/serving you は一般的？」 | ホスピタリティ業界の定番だが、eBay 個人セラー文脈ではフォーマル過ぎ |

すべて Claude が **反映前に自主検証していれば気付けたはず** の違和感。社長に指摘されてから直す動きを繰り返した。

## ルール（厳守）

### 1. プロンプトに英語表現を入れる前の自主チェックリスト

- [ ] **米国英語ベース**になっているか（英国/豪州 marker は明示条件のみ）
- [ ] **eBay の個人セラー文化** に合った register か（ホスピタリティ業界・大企業 CS のフォーマル過ぎではないか）
- [ ] **業務外のカジュアル度** に踏み込んでいないか（"Hey", "Hiya", "What's up", スラング等）
- [ ] **古めかしい表現** が混ざっていないか（"Kindly", "We are pleased to inform you", "Please be advised that", "Pursuant to" 等）
- [ ] **学術/文学的な表現** が混ざっていないか（em dash の多用、"We can only imagine your frustration" のような書き言葉、"Yours faithfully" 等）
- [ ] **企業っぽさが過剰** になっていないか（個人セラーとしてのリアリティを保てているか・"We sincerely regret to inform you" 等）

### 2. 反映前に「違和感候補」を社長に列挙する義務

- 新規追加・修正する英語フレーズは、反映前に **「これは違和感ある可能性があります」** として社長に提示
- 社長から「OK」「修正して」の判断を得てから反映
- 「いきなり反映完了」を避ける

### 3. 反映後の自主検証義務

- テスト結果に **想定外の英語表現** が出たら、社長指摘を待たずに **Claude から報告**
- 「この語彙はeBay文脈で違和感あるかもしれません」を **先回りで** 言う

## 既存プロンプトの再点検候補（2026-04-29時点・要社長判断）

`prompt_admin_v2.3_baseline.md` の以下は要再評価：

- POLITE の `"Kindly"` 推奨 → 米国eBayでは古め・"Please" のほうが自然な可能性
- APOLOGY の `"We sincerely apologize"` `"We deeply regret"` `"We can only imagine your frustration"` `"Yours sincerely,"` → 法人/英国寄り。eBay 個人セラーは `"I'm so sorry"` `"I really apologize"` のほうが温かい可能性（カテゴリ8/9 の APOLOGY 実走時に検証）
- 主語 `"We"` 固定 → 個人セラー一人運営の場合 `"I"` のほうが自然なケースもある（仕様判断）

これらは **次回 APOLOGY を実走するタイミング（カテゴリ8/9）で実出力を見ながら判断**。

## 違反したらどうなるか

社長の貴重なテスト時間が、本来 Claude が自主検証すべき英語の違和感確認に費やされる。
1日の内に複数回（"Hey" "Cheers" "serving you"）指摘が出たら、それは Claude の自主チェック不足。

## 関連

- `memory/feedback_baychat_ai_reply_stance.md`（5原則）の延長ルール
- `services/baychat/ai/prompt_admin_v2.3_baseline.md`（カテゴリ別段階改修中）
