# Equipment Library — 吸収装備の資産化

> Claude Codeが外部から吸収した知識・ツール・事例を資産として蓄積。
> **これがなければ私は凡庸なClaude Codeのままで終わる。**
> 毎週必ず更新する。

---

## 吸収ルール

1. 装備の追加時は、必ず **日付 / ソース / カテゴリ / 要約 / 適用先 / 社長への説明済み?** を記録
2. 適用前に必ず社長に「提案」として提示（勝手に実装しない）
3. 社長の「よくわからない」には敏感に対応し、簡素化して再提示
4. 四半期ごとに棚卸しし、陳腐化した装備を廃棄

---

## カテゴリ

- **L1：Claude Code マスタリー**（Hooks / Skills / MCP / Plugins / Scheduled Tasks）
- **L2：ドメイン実践知**（Etsy / Beehiiv / KDP / note / SUZURI）
- **L3：ツール・API・自動化**（画像生成 / n8n / 新MCP）
- **L4：戦略・経営**（Indie Hackers事例 / 失敗事例 / 冪乗則）
- **L5：社長の意思決定パターン**（過去のフィードバック内部化）

---

## 初期装備（2026-04-18 調査時点の取り込み）

### L4-001：冪乗則と目標設定の関係
- **日付**：2026-04-18
- **ソース**：micro-SaaS Ideas統計, Beehiiv State of Newsletters 2026
- **要約**：オンライン収益は正規分布ではなく冪乗則に従う。月$1K（約10万円）までは上位25-35%の達成域。月$10K以上は上位5%。**10個の10万円ストリームは数学的に、1個の100万ストリームより実現確率が高い**
- **適用先**：プロジェクト全体の目標設定ロジック
- **社長への説明済み?**：✅ はい（「10万×10戦略の数学的妥当性」プレゼンにて）

### L2-001：Etsy AIデジタル商品 — Alex事例
- **日付**：2026-04-18
- **ソース**：[How Creators Make $5K/Month Selling AI Art on Etsy](https://blog.republiclabs.ai/2026/03/how-creators-make-5kmonth-selling-ai.html)
- **要約**：45日で68出品 → 売上$4,872 → 3ヶ月目に月$5,800安定（週5時間以下）。ベストセラーはボタニカルラインアートバンドル（187販売×$9.99）
- **適用先**：Stream 1 Etsy戦略のベンチマーク
- **社長への説明済み?**：✅ はい

### L2-002：Beehiiv — Cyber Corsairs / Mindstream / The Neuron
- **日付**：2026-04-18
- **ソース**：beehiiv Case Studies
- **要約**：
  - Cyber Corsairs：7ヶ月で月$16,600（AI×プロダクティビティ）
  - Mindstream：17ヶ月で21万人、3人チーム＋15種AIツールで運営、HubSpot買収
  - The Neuron：24ヶ月で50万人、年$1M+、LinkedIn有機＋Meta広告
- **適用先**：Stream 2 Beehiiv戦略の上限イメージと成長パスの参考
- **社長への説明済み?**：✅ はい

### L2-003：Beehiiv収益チャネル4本の具体CPM
- **日付**：2026-04-18
- **ソース**：beehiiv State of Newsletters 2026, InfluencersKit
- **要約**：
  - Ad Network（1,000購読者+20%開封率で参加可）：ニッチ別CPM $5-150
  - Boosts：$1-3/購読者、beehiiv手数料20%
  - 有料サブスク：手数料0%（Substackは10%）
  - ニッチ別CPMトップ3：B2B SaaS $100-150、金融$90-140、仮想通貨$80-120
- **適用先**：Stream 2のニッチ最終選定、収益モデル計算
- **社長への説明済み?**：✅ はい

### L2-004：KDP AIコンテンツポリシーとミディアムコンテンツ戦略
- **日付**：2026-04-18
- **ソース**：Amazon KDP AI Disclosure Policy 2026, Naomi Jane Substack
- **要約**：AI生成コンテンツは許可、ただしKDP内部での開示必須（商品ページには表示されない）。**ローコンテンツは競争激化、ミディアムコンテンツが長期勝者**
- **適用先**：Stream 3 KDP戦略の方向性
- **社長への説明済み?**：✅ はい

### L1-001：Claude Code スケジュールタスクの3階層
- **日付**：2026-04-18
- **ソース**：Claude Code Docs, Claude Code Scheduled Tasks Guide
- **要約**：
  - CLI /loop：セッション内のみ
  - Desktop Scheduled Tasks：PC起動中に永続実行
  - Cloud Routines：Anthropicクラウド24/7、PC電源不要
- **適用先**：週次PDCAの実行環境選定
- **社長への説明済み?**：❌ まだ → 来週の週次レビューで提案

### L3-001：Beehiiv API機能
- **日付**：2026-04-18
- **ソース**：beehiiv API Reference
- **要約**：投稿作成・スケジュール・購読者管理・オートメーション全てAPI対応。ただしCreate Post APIは現在Enterprise限定（ベータ）
- **適用先**：Stream 2の自動化パイプライン
- **注意**：Enterprise限定なので、初期はZapier/Make経由orマニュアル投稿を検討
- **社長への説明済み?**：❌ まだ

### L3-002：Slidebean の自動化ニュースレター事例
- **日付**：2026-04-18
- **ソース**：[Slidebean Medium記事](https://slidebean.medium.com/i-built-a-fully-automated-newsletter-with-gpt-and-zapier-b3e0896a352d)
- **要約**：Zapier + GPT(Humanloop) + Google Sheets + HubSpotで構築。週1時間で1週間分をスケジュール。画像生成のみMidjourney手動
- **適用先**：Stream 2の自動化アーキテクチャ参考
- **社長への説明済み?**：❌ まだ

---

## 吸収キュー（次に取り込むべき装備）

Week 1で取り込む予定：

- [x] **L1**：Claude Code の最新Changelog（直近2ヶ月分）← 2026-04-19 完了（L1-002〜L1-008参照）
- [x] **L1**：Cloud Routines の具体的な使い方と料金 ← 2026-04-19 完了
- [x] **L2**：Etsy「AI Prompts」検索で上位20店舗のタイトル・タグ・価格分析 ← 2026-04-19 完了（L2-005〜L2-010）
- [x] **L2**：Beehiiv「AI for Solo Entrepreneurs」類似ニッチの既存ニュースレター5〜10件調査 ← 2026-04-19 完了（L2-011〜L2-013）
- [ ] **L2**：Amazon KDP「AI Prompt Journal」上位10冊の実売データ ← 要Publisher Rocket or 手動調査
- [ ] **L3**：Midjourney / Ideogram / Nano Banana Pro の2026年時点ベストプラクティス
- [ ] **L4**：Indie Hackers の月$1K MRR到達事例3件（AI関連）

## 2026-04-19 土曜日 追加吸収（Week 1前倒し）

### 🚨 L2-005：Etsy AIプロンプト規約の重大制約
- **日付**：2026-04-19
- **ソース**：Etsy Seller Handbook, Etsy Creativity Standards, eRank blog
- **要約**：**Etsyは2024年7月以降、AIプロンプト集単体の販売を禁止**。2025年6月にPLR/MRR再販も禁止。違反=ショップ閉鎖。回避策：Notionシステム/ワークフローツールキットとして再構成、プロンプト+生成物セット、自作プロンプトのみ
- **適用先**：Stream 1戦略を根本修正（プロンプト集→Notionシステム型）
- **社長への説明済み?**：✅ はい（2026-04-19プレゼン）
- **🔴 重要度：最高**

### L2-006：Etsy AIカテゴリの上位ショップ分析
- **日付**：2026-04-19
- **ソース**：promptstodollars.com, Etsy観察
- **要約**：MyDigitalDarling（4,600+レビュー）、LynnReesedesigns（1,500+）、AIcreativeTools（627）が上位。共通点：Notion+PDF+CSV型、$9〜$29価格帯、13タグ全使用、ロングテール、8〜10画像、Pinterest流入
- **適用先**：Stream 1の商品設計・出品作業
- **社長への説明済み?**：✅ はい

### L2-007：Etsyニッチ別競合度マップ
- **日付**：2026-04-19
- **ソース**：promptstodollars.com eRank data
- **要約**：
  - Claude Prompts for Writers = **極低競合**（狙い目）
  - ChatGPT for Realtors = 中競合（買い手層強い）
  - AI for Coaches = 低〜中競合
  - AI Prompts for Solo Entrepreneurs = **超高競合**（避ける）
  - ChatGPT for Teachers = 高競合（ただしESL等サブニッチなら可）
- **適用先**：Stream 1ニッチ選定の根拠
- **社長への説明済み?**：✅ はい

### L2-008：Etsy価格ラダーの勝ちパターン
- **日付**：2026-04-19
- **ソース**：MyDesigns, ZenEarner, 複数事例
- **要約**：$9（トリップワイヤー）→ $19（コア）→ $29（特化）→ $49（コンプリート）の4段階が新ショップに最適。$7以下はEtsy手数料で利益消失、$49超は権威性必要
- **適用先**：Stream 1価格設計
- **社長への説明済み?**：✅ はい

### L2-009：Etsy新ショップの出品戦略
- **日付**：2026-04-19
- **ソース**：Marmalead, Printify SEO guides
- **要約**：初日から20〜30商品が必須（5商品以下は埋もれる）。13タグ全使用・ロングテール優先。Pinterest流入が初期のエンゲージメント信号に効く。初売上まで3〜6週間、Month6で月$500射程
- **適用先**：Stream 1の段取り
- **社長への説明済み?**：✅ はい

### L2-010：Etsy失敗パターン10選
- **日付**：2026-04-19
- **ソース**：Dynamic Mockups, Craft Industry Alliance
- **要約**：規約違反>汎用ニッチ>PLR再販>出品数不足>質の低いカバー>AI非開示>キーワード詰め込み>低すぎる価格>レビュー対応放置>更新停止
- **適用先**：Stream 1運営ルール
- **社長への説明済み?**：✅ はい

### L2-011：Beehiiv AI系の実競合マップ
- **日付**：2026-04-19
- **ソース**：Beehiiv observations, Twitter/LinkedIn分析
- **要約**：
  - メガ級（避ける）：Rundown AI(100万+), Superhuman AI(70万), The Neuron(55万), Mindstream(20万+)
  - ソロ起業家向け直接競合：**Zarak Khan「The AI Solopreneur」(5〜8万)**← 最大脅威
  - ニッチ未開拓：$20以下スタック/失敗事例/非英語圏視点
- **適用先**：Stream 2ポジショニング
- **社長への説明済み?**：✅ はい

### L2-012：Beehiiv成長戦術ROIランキング
- **日付**：2026-04-19
- **ソース**：Beehiiv case studies, 2026年観察
- **要約**：
  1. Beehiiv Boosts（最強）：$1.5〜$4/購読者、Superhuman AIは30日で1万人
  2. X build-in-public（Codie/Greg/Shaan全員ここ）
  3. LinkedInカルーセル（Zarak Khanの主戦場）
  4. Indie Hackers/Reddit r/SaaS投稿
  5. Product Hunt ローンチ
  - Meta広告は2026年CPA悪化（$8〜$15）、小規模には非推奨
- **適用先**：Stream 2のMarket-In戦略
- **社長への説明済み?**：✅ はい

### L2-013：Beehiiv AI系ニュースレターのフォーマット勝ちパターン
- **日付**：2026-04-19
- **ソース**：Beehiiv analytics, 2025-2026業界データ
- **要約**：
  - オープン率：AI系平均35〜45%（一般20-25%）
  - 最適文字数：400〜800語（読了3〜5分）
  - 頻度：**週2回（火金）が1人運営の黄金律**
  - 送信時間：B2B向けは火水木朝6〜8時（現地時間）
  - 構成：TL;DR冒頭→箇条書き→数字1点以上→最後に読者への問い
- **適用先**：Stream 2コンテンツ設計
- **社長への説明済み?**：✅ はい

### ⭐ L1-002：Claude Code Cloud Routines（2026年4月リリース）
- **日付**：2026-04-19
- **ソース**：Claude Code Docs, Winbuzzer, The New Stack
- **要約**：**PCが起動していなくてもAnthropicクラウドで自動実行される**。Pro:5回/日、Max:15回/日まで。Cron/Webhook/GitHubトリガー対応。**社長の週次PDCAを土日でも実行可能にする装備**
- **適用先**：週次/月次PDCAの実行環境（デスクトップSchedulerから移行検討）
- **社長への説明済み?**：✅ はい
- **🟢 重要度：高**

### ⭐ L3-003：e-commerce/content MCPサーバー群（2026年4月現在）
- **日付**：2026-04-19
- **ソース**：Claude Code MCP registry
- **要約**：
  - Etsy MCP：出品管理（審査通れば自動出品も可能）
  - Beehiiv MCP：記事投稿・購読者管理
  - Substack MCP：同
  - WordPress MCP：ブログ投稿
  - Notion MCP：テンプレート生成
  - Shopify/BigCommerce MCP：将来拡張用
  - Stripe/PayPal MCP：決済追跡
- **適用先**：全ストリームの自動化パイプライン
- **社長への説明済み?**：✅ はい
- **🟢 重要度：高**

### L1-003：Effort Level xhigh（Opus 4.7）
- **日付**：2026-04-19
- **要約**：highとmaxの中間。複雑なオーケストレーションでMax予算を節約できる
- **適用先**：装備吸収タスク等でxhighを使い分け
- **社長への説明済み?**：✅ はい

### L1-004：Sub-agent + Haikuでトークンコスト70%削減
- **日付**：2026-04-19
- **要約**：調査タスクはHaikuサブエージェント、最終判断だけOpus本体という構成でコスト激減
- **適用先**：週次装備スキャン、競合調査の定常運用
- **社長への説明済み?**：✅ はい

### L1-005：PostToolUse hook で出力書き換え可能に
- **日付**：2026-04-19
- **要約**：MCPツールの結果をhookで書き換え可能。機密情報の自動マスク等に有用
- **適用先**：将来の自動化ガードレール
- **社長への説明済み?**：❌ まだ（必要時に提案）

### L4-001：KDP調査の限界とPublisher Rocket判断
- **日付**：2026-04-19
- **要約**：KDP実データは有料ツール（Publisher Rocket $199買い切り、K-lytics $47/レポート）なしには正確に取得困難。架空データで戦略立案すると失敗する。**Stream 3は着手前にPublisher Rocket導入 or 手動調査を判断必要**
- **適用先**：Stream 3着手タイミングの再検討
- **社長への説明済み?**：✅ はい
- **🟡 要社長判断**

---

*このファイルは週次PDCAのたびに更新される*
