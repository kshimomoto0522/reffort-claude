# Decision Log — 意思決定ログ

> 全ての意思決定とその根拠を時系列で記録。セッションを跨いで判断の一貫性を保つための資産。

---

## フォーマット

```
### YYYY-MM-DD | [判断のタイトル]
- 背景：
- 選択肢：
- 決定：
- 根拠：
- 責任者：Claude Code / 社長 / 合意
```

---

## 2026-04-18 | プロジェクト発足

- **背景**：社長から「Claude Code自身で自動運用し、月10万円の収益を得る方法」を徹底調査するよう指示
- **経緯の要点**：
  1. 初期提案（事業関連プラン）→ 社長より「事業無関係で」と軌道修正
  2. 事業無関係の15カテゴリを徹底調査 → TOP3提案（Beehiiv / SEO / Etsy）
  3. 社長より「Etsyが最速・最高利益率なのになぜ3位か」の鋭い指摘
     → 私の評価軸（自動化率偏重）のバイアスを自己修正、Etsyを1位に再配置
  4. 社長より「10万円×10ストリームが簡単ならそれをやりたい」の方針提示
  5. 社長より「責任者としてコミットできるか」の問い
  6. 社長より「頭を下げても意味がない、装備を吸収して毎週強くなれ」の本質指摘
  7. 社長より「勝手に方針を変えず、社長のペースを尊重せよ」の重要制約
- **決定**：
  - 月10万円×10ストリーム＝月100万円を18ヶ月の最終目標とする
  - Month 1〜3は3ストリーム（Etsy / Beehiiv / KDP）に集中
  - Claude Codeは装備吸収を毎週継続する
  - 全ての戦略変更・新装備適用は社長の明示的承認を必要とする
  - 社長の既存事業（eBay/BayChat/BayPack/Campers）には一切介入しない
- **責任者**：合意（社長とClaude Code）

---

## 2026-04-18 | 3ストリーム選定

- **背景**：10ストリーム同時スタートは現実的でない。最初に集中するストリームを決定する必要あり
- **選択肢**：
  - A：Etsy単独集中（即金性最大）
  - B：Beehiiv単独集中（スケール性最大）
  - C：Etsy＋Beehiiv＋KDPの3本並走（分散＋補完性）
- **決定**：C（3本並走）
- **根拠**：
  - Etsy：即金（1〜2ヶ月）、利益率90%、固定費ゼロ
  - Beehiiv：遅延起動だが上限が最も高い、自動化率最高95%
  - KDP：不労所得化、長期の積み上げ、Claude Codeが原稿生成に最適
  - 3本は時間軸が異なるため、キャッシュフローを連続的に作れる
- **責任者**：合意

---

## 2026-04-18 | 初期ニッチの仮決定

- **Stream 1（Etsy）**：「AI Prompts for Solo Entrepreneurs」＋「Claude Prompts for Writers」
  - 根拠：競合が少ない、単価高め（$15〜$39）、Claude Codeが得意な領域
- **Stream 2（Beehiiv）**：「AI × Solo Entrepreneur」ニッチ
  - 根拠：TLDR/The Neuron等の総合AI巨人と直接競合しない、サブニッチで空白地帯
- **Stream 3（KDP）**：「AI Prompt Journal」「Solopreneur's AI Workflow Planner」系ミディアムコンテンツ
  - 根拠：ローコンテンツは飽和、ミディアムコンテンツが長期勝者
- **注意**：各ニッチは競合調査を経て最終確定する（Week 1内に実施）
- **責任者**：Claude Code提案 → 社長仮承認

---

## 2026-04-18 | インフラ構築着手

- **決定**：`/management/monetization-portfolio/` フォルダ構造を構築、CLAUDE.md/portfolio-master.md/decision-log.md/equipment-library.mdを初期化
- **責任者**：Claude Code実行

---

---

## 2026-04-19 | Week 1調査結果の反映（土曜前倒し実行）

- **背景**：社長が土曜日に稼働していたため、Week 1の競合調査4本を並列実行
- **調査内容**：
  1. Etsy AIプロンプト上位20店舗＋ニッチ競合度
  2. Beehiiv AI×Solo Entrepreneur競合＋ギャップ分析
  3. Amazon KDP実売データ（データ取得に制約、方針のみ）
  4. Claude Code最新Changelog（2026年4月分）
- **重大発見**：
  - 🚨 **Etsyが2024年7月以降、AIプロンプト集単体を禁止**。戦略の根本修正必須
  - **Solo Entrepreneurs向けは競合飽和**、代替ニッチ（Claude for Writers等）を選定
  - Cloud Routines等の新機能で社長の負担をさらに減らせる
  - KDPは有料調査ツールなしでは実データ取得困難
- **決定事項**：
  1. **Stream 1のコンセプトを「Notionシステム/ワークフローツールキット」に修正**（strategy.md更新済）
  2. **Stream 1のメインニッチを「Claude Prompts for Writers」、サブを「ChatGPT for Realtors」に変更**
  3. **Stream 2のポジショニング候補を「The $20 Stack」「The AI Operator」「The Bootstrap AI」の3案に絞り、社長に最終選択を委ねる**
  4. **Stream 3着手前にPublisher Rocket($199買い切り)導入判断を社長に仰ぐ**
  5. equipment-library.mdに12件の新装備を記録
- **責任者**：Claude Code主導、社長承認待ち（下記3点）

---

## 🟡 社長の判断待ち（2026-04-19時点）

1. **Stream 2のニュースレター名**：3案（The $20 Stack / The AI Operator / The Bootstrap AI）からの選択
2. **Stream 3（KDP）の着手タイミング**：Publisher Rocket $199を買うか、手動調査でいくか、Stream 3を後ろにずらすか
3. **Beehiiv Scale Plan契約タイミング**：Week 2に入ってもいいか、もう少し準備期間を取るか

---

---

## 2026-04-19 | 多視点プロセス導入＋初回発動結果

- **背景**：社長のご指示「考える・ファクトチェックする人がいる・疑う人がいる・それらを持って判断するプロセスを作れないか」を受けて、4ロール体制を構築
- **作成ファイル**：`multi-perspective-process.md`
- **4ロール**：Proposer / Skeptic / Fact-Checker / Judge
- **CLAUDE.mdに原則6として追加**：重要判断は多視点プロセス必須

### 初回発動：The $20 Stack検証
- 結果：**不採用**（広告主TAM問題で構造的に弱い）
- 代替：The AI Operator を推奨
- 社長の当初の指摘「競合ゼロは需要ゼロの可能性」が完全に正しかった
- **多視点プロセス初日で実効性を証明**

### 初回発動：Publisher Rocket検証
- 結果：**情報鮮度問題なし**（データはリアルタイム取得）
- 社長推奨C（Month 2後ろ倒し）で進行、Month 2時点で再判断

---

## 2026-04-19 | 原則7：Cloud Routines 優先活用を追加

- **背景**：社長のご指示「PCが落ちていたりしてうまく実行できないスケジュールタスクがあるため、Cloud Routinesを全体で使えるよう記録」
- **変更**：CLAUDE.mdに原則7として追加
- **運用方針**：
  - Desktop Scheduled TasksはPC起動前提の作業のみ
  - Cloud Routinesは全週次PDCAで優先使用
  - 既存の事業系タスク（daily-github-backup, monday-ebay-report-delivery）はCloud化検討リストに

---

## 2026-04-19 | Stream 2戦略修正

- **決定**：ニュースレター名候補を「The $20 Stack/AI Operator/Bootstrap AI」から「The AI Operator/AI for Small Business/The Solo SaaS Stack」に変更
- **根拠**：多視点プロセスでブートストラッパー層ポジショニングが否認された
- **社長の判断待ち**：3案からの最終選択

---

---

## 2026-04-19 | 全重要決定の一括確定（社長「ベストに任せる」指示を受けて）

### 1. Stream 2 ニュースレター名：**The AI Operator**
- 3候補（The AI Operator / AI for Small Business / The Solo SaaS Stack）から選定
- 根拠：多視点プロセスで残存、"operator"が権威性と差別化の軸
- タグライン：**"No hype, just numbers. Real AI implementation stories from operators."**
- 週2回配信（火・金）、固定3本柱：
  1. 🧱 Stack Teardown（実事業のAIスタック分解）
  2. 📊 Real Numbers（ツールコスト・ROI・時間削減の実数字）
  3. 🔥 What Failed（AIで失敗した実例の分析）

### 2. Stream 1 Etsy店舗名：**QuillStack**
- Claude Prompts for Writers のニッチに合致
- 覚えやすく、SEOで他と競合しない
- ブランディング：作家向けの静謐で品のある世界観

### 3. アカウント名義（デフォルト方針）
- Etsy：社長個人名義（立ち上げ速度優先、将来法人移管可能）
- Beehiiv：ペンネーム運用（個人ブランドと分離）
- Stripe：社長個人（初期）→ 月商安定後に法人に移管検討
- **社長からの修正指示があれば即変更**

### 4. Stream 3（KDP）
- 社長推奨C（Month 2後ろ倒し）で確定
- Month 2時点でPublisher Rocket $199 or KDSPY $47 を再判断

### 5. Stream 1 商品ラインナップ
- `products/product-concepts-v1.md` の10商品で確定
- 製作優先順：C1 → C2 → C7 → R1 → C3 → 残り5

---

*次の意思決定がここに追記される*
