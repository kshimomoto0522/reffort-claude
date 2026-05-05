# BayChat AI Reply プロンプト構成ルール（永続メタルール）

> 作成: 2026-05-05  
> 目的: 将来の Claude / 開発者がプロンプトを改修する際、レシピ積み上げによる肥大化に陥らないための運用ルール。  
> このファイルは BayChat AI Reply のプロンプト改修セッション開始時に必ず読む。

---

## 背景：なぜこのルールが必要か

2026-05-05、cat03 POLITE のフィードバック対応中、私（Claude）は**原則ベース転換を宣言した直後にレシピ積み上げに戻ってしまった**。

具体的には：
- 「PRINCIPLE A〜E」というラベルを付けたが、中身は「CONCRETE FORBIDDEN PATTERNS」「TOPIC → AUTHORITY マッピング」「BEFORE/AFTER shipment 別マトリクス」など、シナリオ別レシピの集合体になっていた。
- 単発のテスト失敗を見て反射的に禁止例文を追加し続け、プロンプトが 660+ 行に膨張。
- 社長から「ルールを縛り過ぎると、あらゆる枝分かれにルールを徹底する必要があり、プロンプトが膨大になる」と既に指摘されていたにもかかわらず、再発した。

**この再発を構造的に防ぐため、本ルールを永続化する。**

---

## ルール A：原則優先（PRINCIPLE FIRST）

新しい制約を追加するときは、必ず以下の順で検討する：

1. **既存の原則で対処できるか？** → できるならそれで終わり。プロンプトを変えない。
2. **新しい原則を1つ追加すれば対処できるか？** → 追加。原則は「思考のフレームワーク」を提供する。
3. **どうしても原則化できない場合のみ、レシピ（具体例）を追加する。**

レシピを最後の手段とする。

---

## ルール B：レシピ追加の判定基準

「禁止パターンリスト」「正解パターン例」「シナリオ別マトリクス」などのレシピは、以下を **すべて満たす場合のみ** 追加可能：

- (a) 既存原則 + 新原則追加でも対処不可能
- (b) 複数のテスト走行で **繰り返し** 失敗している（単発失敗は原則の不徹底か、AI採点の揺れの可能性大）
- (c) 失敗の原因が以下のいずれか：
    - **モデル特性**（GPT-4o-Mini の指示追従弱さなど）で原則を守れない
    - **業界固有の知識**（eBay の Item Not Received case の正式名称など）が必要
    - **致命的な捏造リスク**（HARD RULE 2 関連）

単発のテスト失敗を見て反射的にレシピを追加するのは禁止。**まず原則の表現を強める** ことを試す。

---

## ルール C：レシピ追加時の必須コメント

レシピを追加するときは、必ず本文または直前のコメントで以下を明記する：

- なぜこれが原則化できなかったか
- どのテスト走行で繰り返し失敗したか
- このレシピを将来削除できる条件は何か

これは将来の監査（「このレシピはまだ必要か？」）のため。

---

## ルール D：サイズ規律

- **目標**: 登録用プロンプト全体（admin_prompt の本文）を **250行以内**
- **警戒ライン**: 300行を超えたら、レシピを原則に畳めないか監査する
- **行数 = コスト**: input トークン量に直結（プロンプトキャッシュ未使用時）

---

## ルール E：FINAL CHECK は原則の再掲のみ

FINAL CHECK セクションは「原則の再確認」であり、新しいレシピを足し込む場所ではない。

各 FINAL CHECK 項目は対応する原則を 1 文で再掲し、AI に「outputする前にこの原則を満たしているか問え」と促す。

FINAL CHECK 内に **新しい禁止例** を追加し始めたら、それは原則が弱いサイン。原則本体を見直す。

---

## ルール F：テストでの判断基準

テスト失敗を見たとき、まず以下を区別する：

| 失敗の種類 | 対応 |
|---|---|
| 既存原則の徹底不足 | 原則の表現を強める / FINAL CHECK で再掲 |
| 既存原則の不在 | 新しい原則を追加（レシピではなく） |
| AI採点LLMの揺れ | 何もしない（実出力を読んで本質的に違反なら原則検討） |
| モデル特性で守れない（指示追従の限界） | 機械的解決（FORCED_TEMPLATE / output schema 等）を検討 |

---

## ルール G：既存プロンプトのレシピ → 原則化の機会

新規追加だけでなく、既存のレシピも定期監査する：

- HARD RULE (2) 内の「✗ ✓」例文リストが膨大になっている → 原則化できないか
- TONE GUIDELINES の「✗ ✓ vocabulary」リスト → 「voice の差し方」原則 1 文に圧縮できないか
- 各原則内の例が 3 個を超えている → 原則の言葉が弱いサイン

---

## ルール H：チェンジログ必須

プロンプトを改修したときは、ファイル末尾の「バージョン履歴」に：
- 何を変えたか
- 原則を変えたのか / レシピを追加したのか
- レシピ追加なら **ルール B (a)(b)(c) を満たしている根拠**

を 1 行で記載する。これは未記載なら本ルール H 違反として、改修が無効。

---

## ルール I：プロンプト改修セッションの開始手順

1. **このファイル（prompt_construction_rules.md）を読む**
2. 改修対象の admin_prompt を読む
3. 直近のテスト結果を確認
4. 改修方針を立てる時、ルール A〜H を必ず参照
5. 改修後、ルール H に従ってバージョン履歴を更新

---

## ルール J：ベスト判断は Claude 側の責任

社長は「ベストな状態を作ってくれ」と要求する。これは「Claude が **常にベストを検討してテストして判断**し、必要があれば社長に提案する」ことを意味する。

社長の言葉に盲目的に従うのではない。

ただし、Claude が選んだ方向性（例：原則ベース転換）を Claude 自身が後で裏切ると、社長の信用を失う。**自分で決めた方針を自分で守る** こと。

---

## 現行の原則とハードルール（参照用）

### CORE PRINCIPLES（10個）— 思考の軸
1. WE ARE THE SELLER（identity）
2. DON'T FABRICATE — both directions（epistemics）
3. WE INVESTIGATE BEFORE DEFLECTING（service ethics）
4. DON'T DECREE WITHOUT FACTS（epistemics）
5. READ THE CONVERSATION HISTORY（context awareness）
6. APPLY COMMON SENSE（no absurd actions）
7. TONE IS VOICE, FACT IS FACT（fact-invariant across tones）
8. MATCH AUTHORITY TO TOPIC（don't borrow unrelated authority）
9. CONFIRM OUR OWN ACTIONS（event log is authoritative）
10. DON'T HEDGE OUR OWN INTENT（commitments, not maybes）

### HARD RULES（5個）— 絶対禁止
- (1) AUTHENTICITY confidence + no internal policy leak
- (2) NO FABRICATION — positive AND negative
- (3) NO FUTURE PROMISES
- (4) NO FAKE eBay POLICIES
- (5) NO DEFAULT EXTRA-WORK PROMISES

---

*最終更新: 2026-05-05*
