---
name: 意思決定ログ
description: 主要な経営判断とその根拠の記録。将来同じような判断場面でブレない提案をするために使う
type: project
originSessionId: 35eb4679-f28f-4d72-9a30-510e015273e2
---
# 意思決定ログ

## 事業構造に関する判断

### Campers引き継ぎの判断（2025年頃）
- **決定**: 前任者（創始者）の引退に伴い、解散予定だったCampersを引き継いだ
- **背景**: 社長は約5年前に初期生徒として参加 → 実績を出して講師に昇格（ギャラ30万円）。役割はChatworkでの質問回答＋月1回の勉強会
- **根拠**: ①コミュニティに愛着がある（自分も寂しい）②やることは対して変わらない③ギャラが上がる。合理的に判断
- **現状維持の理由**: YouTube・X・SNSでのコンサル募集をやる気がない。いちから育てる気力・時間・興味もない
- **トランプ関税の影響**: 引き継ぎ後にebayセラーが大量脱落。Campersも約30名減少（70名→約40名）。残っている人は細々と続けている
- **今後の方針**: 残存メンバーへの付加価値提供。具体的には「eBay AI運営コース」を追加し、月額+5,000円で単価アップを図る

### Cowatech継続委託の判断
- **決定**: BayChat・BayPackの開発をCowatechに継続委託
- **根拠**: ①付き合いが長い②社長のこと・サービスの多くを理解している③ベトナムのため国内より安い④コントロール・依頼がしやすい
- **他社比較**: したことがない
- **変化の兆し**: Claude Codeで社長自身ができることが増えており、Cowatechへの依頼の一部をClaude Codeで代替することでコストカットにつなげたい意向あり

### BayPack一括納品を非公開にしている理由
- **決定**: 収益性が最も高いモデルだが、公にしていない
- **根拠**: ①現地運営はリプロニーズ（協力会社）に委託②マーケ・プロモーションがほぼ追いついていない③Xでの発信は「依頼紹介＋値下げ告知」のみで戦略性がない
- **収益構造**: リプロニーズの利益の10%がReffortの報酬 → **最優先事項になりにくい構造**
- **本質的な課題**: マーケの問題であり、サービス自体の問題ではない

---

## Claude Code導入に関する判断

### 2026-03-11 Claude Code契約
- **決定**: Claude Code（Max）を契約
- **根拠**: 梶谷健人さんに刺激を受けた。AI活用で事業をアップデートしたい

### 2026-03-12 「急がば回れで基盤を固める」方針
- **決定**: eBay売上低下中だが、場当たり対応より仕組み化（CLAUDE.md整備）を優先
- **根拠**: 土台がないまま走っても結局やり直しになる。社長自身の判断

### 2026-03-19 AI ReplyモデルをGemini 2.5 Flashに決定
- **決定**: GPT-4.1-MiniからGemini 2.5 Flashへ移行方針
- **根拠**: 6モデル比較の結果、コスト↓品質↑速度↑を同時に実現できる唯一の選択肢

### 2026-03-20 ASICSツール Firefox/Selenium移行
- **決定**: Scrapling → Selenium/Firefox（ヘッドレス）
- **根拠**: Scraplingではbot検出で403頻発。Firefoxなら突破可能と確認

### 2026-03-22 APIトークンを.env管理に移行
- **決定**: 全スクリプトのトークン直書きを.envファイルに移行
- **根拠**: GitHubにトークンが含まれた状態でpushされていた。漏洩リスク排除のため

### 2026-03-31 Google Sheetsを週次レポートの推奨出力に決定
- **決定**: ExcelからGoogle Sheetsへ移行。Excel併用は継続するがGoogle Sheets版を「推奨」として配信
- **根拠**: ①スタッフがリアルタイムで閲覧可能②備考の書き込みが次週に引き継がれる③スマホでも見やすい④ExcelはChatwork添付用として残す
- **対応**: send_weekly_report.pyにGoogleスプレッドシートリンクを追加。Chatworkメッセージで「推奨」と明記

### 2026-04-20 BayChat AI Reply：プロンプト微修正ループを停止し、設計図整備を優先する
- **決定**: プロンプトv2.5以降の本格開発・新機能（要約モード等）のCowatech依頼・FORCED TEMPLATE除去の本番適用判断を一時停止。代わりに「社長・Claude・Cowatechが共通で使える設計図」の整備プロジェクトを立ち上げる
- **背景（1週間の経緯）**: 4/14〜4/20にかけて、①60件バッチテスト、②Cowatech本番ペイロード入手、③スプレッドシート19枚のリバースエンジニアリング、④Cowatech質問4件送信、⑤質問が噛み合わず手元資料で自己解決、という流れを辿った。毎回インフラ解析で時間を消費し、プロンプト改善に到達できないパターンが反復
- **根拠**: ①Cowatechの既存仕様書（CSV19枚）は「参考資料」レベルで設計図として破綻（単一参照源なし・条件分岐が暗黙・UI連動明記なし・変更履歴なし・後処理不明）②このまま微修正・新機能を重ねると管理不能になる未来が見える③設計図の質が開発スピードの上限を決める④社長が1週間の実体験から料理の比喩（マニュアルを作る前に調味料・機器設定が狂っている）で根本問題を直感的に抽出⑤設計図の構造化・見える化はClaudeが最も得意な領域
- **ゴール**: 社長・Claude・Cowatech の3者が完璧に意思疎通でき、継続的に管理できる設計図を作る。社長の理想イメージ「左側にコード、右側に機能・影響範囲」を実現
- **並行継続する業務**: eBay関連業務（広告・週次レポート）、BayChat既存運営、v2.4での本番運用（品質担保済み）
- **次セッション**: `services/baychat/ai/handoff_20260420_design_doc_project.md` を冒頭で参照し、論点A（フォーマット）・B（ツール）・C（Cowatech役割分担）から議論スタート

---

### 2026-04-22 BayChat AI Reply：次期モデルを GPT-5-Nano に仮決定（Gemini 2.5 Flash を除外）
- **決定**:
  1. 次期採用モデルは **GPT-5-Nano**（`gpt-5-nano`）
  2. 以前の方針（Gemini 2.5 Flash）は**優先度最低に降格**
  3. モデル切替は Cowatech依頼不要（**admin画面で社長が直接変更可能**）
  4. プロンプト改善（v2.6→v2.7...）で品質を満点に近づける戦略
- **背景**: 2026-04-21 に 18ケース本格テスト実施（3モデル × 18ケース）
  - Gemini 2.5 Flash: 23.22点 / 6.7秒 / ¥0.25/件
  - GPT-4.1-Mini（現行）: 22.72点 / 2.4秒 / ¥0.28/件
  - GPT-5-Nano: 22.33点 / 2.8秒 / **¥0.04/件**
- **根拠**:
  1. **速度**: Gemini の6.7秒はセラー体感NG（4秒超）
  2. **コスト**: GPT-5-Nano は Gemini の 1/6 / GPT-4.1-Mini の 1/7（月額¥6 vs ¥42）
  3. **Cowatech実装負担**: Gemini採用なら Google AI API 実装が必要。GPT系内切替なら admin画面で即変更可能
  4. **品質差は誤差範囲**: 0.4〜0.9pt はプロンプト改善で埋められる（社長の戦略：コスト・速度で仮決定してプロンプトで品質向上）
  5. 2026-04-22 合成40ケーステストでも 同順位（Gemini 19.85 / GPT-5-Nano 19.05 / GPT-4.1-Mini 18.77）で傾向確認済み
- **実装方針**:
  - admin_prompt v2.6 以降で本格テスト → 品質確認 → admin画面で `gpt-5-nano` に切替
  - Cowatech実装作業は不要（モデル名変更のみ）
  - 将来 Gemini を再評価する場合は Google AI API の Cowatech実装依頼が必要になる
- **次ステップ**:
  - 2026-04-23: 社長フィードバック → v2.7 改善 → 再テスト
  - 改善幅が十分なら admin画面で v2.7 登録 + モデル切替
- **関連**: `services/baychat/ai/design-doc/11_model_selection.md` / `services/baychat/ai/prompt_admin_v2.6.md` / `services/baychat/ai/handoff_20260422_v2.6_test_complete.md`

---

### 2026-04-20 夜 BayChat AI Reply：FORCED_TEMPLATE除去・TO/FROM機能継続・admin_prompt v2.5 方針確定
- **決定**:
  1. **FORCED_TEMPLATE除去を確定**（本番反映はCowatech実装工数確認後）
  2. **TO/FROM UI機能は残す**（セラーの明示選択機能として継続）
  3. **挨拶・結句の制御を admin_prompt 側に移行**（`{buyer_name}` `{seller_name}` プレースホルダを新設）
  4. **AI が状況判断で挨拶・結句を省略する仕様**（連続チャット・カジュアル応答・クロージング等）
  5. **FROMなし時の `Best regards,` は残す**（案β：ユースケース少数・AIの状況判断で省略ケースは既にカバー）
- **背景**: 2026-04-16テストでFORCED_TEMPLATE除去が +2.0pt品質改善（19.5→21.5/25・12ケース平均）を定量確認。設計図 v0.2 完成後、社長と Q1（TO/FROM機能設計）・Q3（空/なし判定）を議論し仕様確定
- **根拠**:
  1. 品質改善効果が定量的に明確
  2. UI機能廃止はセラー体験を奪う（社長の仕様要件として「TO/FROM機能は残す」が明示された）
  3. admin_prompt v2.4 は既に「状況判断で柔軟に」の設計思想を内包しており、GREETING & SIGNATURE POLICY の追加で省略ロジックを明示化できる
  4. 既存のCowatech側 TO/FROM 参照ロジック（UI値→DB解決）は再利用可能。変更は「FORCED_TEMPLATE生成削除」+「admin_prompt注入先追加」の2点のみ
  5. FROMなし選択時に `Best regards,` を省略する追加ロジックはユースケース少数（大半のセラーは署名を入れる）に対してオーバーエンジニアリング
- **実装方針**:
  - Reffort側：`prompt_admin_v2.5.md` ドラフト作成済み（GREETING & SIGNATURE POLICY新設・tone別基本形・省略ケース5つ・空値処理）
  - Cowatech側：FORCED_TEMPLATEブロック生成削除 + admin_prompt 内プレースホルダへの注入（2026-04-20 Slack送信済・返信待ち）
- **次ステップ**: Cowatech返信→実装工数確認→`testing/payload_builder.py` v2.5対応→12ケース×v2.4(OFF) vs v2.5 比較テスト→本番反映
- **除外した論点**: Q4（履歴件数）・Q5（schema名参照）・Q6（Gemini実装）・Q7（whoPaysShipping）・Q9（CSV依存）は今の作業に不要と判断し Cowatech への質問から除外。必要になったタイミングで個別に確認
- **関連**: `services/baychat/ai/design-doc/09_open_questions.md` / `services/baychat/ai/prompt_admin_v2.5.md` / Slack thread_ts: 1776427836.602699

---

### Claude Code Routines 採用見送りの判断（2026-04-20）
- **決定**: Anthropicが2026-04に発表した Claude Code Routines（クラウド実行サービス）の採用を現時点で見送り
- **背景**: 社長から「PCオフでも動くクラウド実行サービスがあるなら使うべきか」と相談
- **判断根拠**:
  1. **技術要件の不一致**: 現状のアクティブタスク6件のほぼ全てがローカル依存（Chrome拡張・ローカルPython・MCPサーバー・ローカルファイル）。Routinesはクラウド実行でローカルMCP不可
  2. **無料枠が現状運用に全く足りない**: Maxプラン無料枠は月15回だが、`chatwork-ai-reply`月約500回、`baychat-slack-hourly-check`月720回、`daily-x-digest`月30回、`campers-member-removal-goto`月30回。1週間で超過する
  3. **移行コストの高さ**: クラウドで動く形に書き換える労力・動作検証のやり直し・月額コストが必要
- **再評価のタイミング**:
  - 旅行・出張中にPC閉じたい場面が増えたとき（特定タスクのみ軽量化してRoutines移行）
  - GitHubイベントでトリガーしたい自動化（push/PR時の処理）が出てきたとき
  - ノートPC1台体制へ移行（常時起動サーバー的な使い方ができなくなった）とき
- **現在の運用**: ローカル `scheduled-tasks` MCP（デスクトップ常時起動前提）で継続

---

---

## フォルダ構成3事業階層リファクタ（2026-04-21）

### 決定
フラット13フォルダ構成 → 3事業階層（`commerce/` `services/` `education/` `management/`）に再編成した。

### 背景
- BayPack請求書自動化を作ろうとした際、BayPack専用フォルダが存在しないことに気づいた
- 社長の頭の中は「物販・サービス・コンサルの3事業」なのに、フォルダはフラット13個で一致していなかった
- `marketing/` `staff-ops/` のような所属不明フォルダが増えていた

### 根拠（調査した原則）
- **DDD（Eric Evans）**：事業ドメインごとに境界を引く
- **PARA法**：Projects / Areas / Resources / Archives
- **Spotify Squad / Amazon 2-pizza teams**：事業単位でチームとフォルダを切る
- **Claude Code の CLAUDE.md カスケード読込**：階層そのものがAIへの指示階層になる
- 事業構造とAIワークスペース構造を一致させることがAI精度に直結する

### 失敗ゼロで完遂した方法
1. **3重の保険**：物理バックアップ（83MB）＋ gitバックアップブランチ ＋ スケジュールタスク一時停止
2. **3エージェント並列事前調査**：ハードコードパス29ファイル / ドキュメント20+ / スケジュールタスク6 を事前に全部洗い出し
3. **相対パス化投資**：29スクリプトを `__file__` 基準の相対パスに変換（次回の構造変更でも壊れない）
4. **git mv / robocopy /MOVE の併用**：未コミットの進行中作業を巻き込まずに物理移動

### 新構造
- `commerce/` ← 物販：eBay + direct-sales
- `services/` ← SaaS：BayChat + BayPack
- `education/` ← コンサル/教育：Campers + 将来コンサル
- `management/` ← 経営横断：dashboards + x-digest + monetization-portfolio

### 再評価のタイミング
- 事業が5つ以上に増えた時（現構造は3〜4事業向け）
- BayChat・BayPackが独立会社化した時
- Campersから派生するコンサル事業が本格化した時

---

## Claude Code運用の根本リファクタ（2026-04-24）

### 決定
1. Claude Code運用を Anthropic公式ベストプラクティス準拠に再構築（Progressive Disclosure徹底・CLAUDE.md 200行以下・archive/ 新設）
2. 隔週メンテサイクル（第1・第3月曜 10:00）で肥大化監視＋最新情報取り込み＋松竹梅提案を自動化
3. 持続可能性4点セット（archive/・biweekly-claude-maintenance・index.md・/隔週メンテナンス スラッシュコマンド）導入
4. effort_booster.py の COMPLEX_KEYWORDS を厳選し、日常語（分析・検証・判断・バグ・エラー等）による誤爆ブーストを防止
5. 全作業を Campers コンテンツ素材として `education/campers/content-projects/` に蓄積（配信計画は別途社長判断・勝手に公開しない）

### 背景
社長から「最近Claude Codeが一度言った通りにやらない／嘘／遅い／トークン消費激しい／バカ過ぎる」と強い不満表明。当初社長はフォルダ再編成（2026-04-21）の影響を疑ったが、3エージェント並列（設定監査・ノイズ調査・ベストプラクティス調査）で徹底診断した結果、「再編成は9割クリーン・真因は再編成前から蓄積してきた肥大化」と判明。

### 根拠
1. **コンテキスト爆発**: ルートCLAUDE.md 136行＋`.claude/rules/` 6ファイル＋MEMORY.md＋子CLAUDE.md最大488行＋settings.local.json 298行 で毎セッション 5,000〜8,000トークン消費が起点
2. **Anthropic公式 / Boris Cherny推奨「200行以下・Progressive Disclosure」からの大幅逸脱**: 子CLAUDE.md 20ファイル中6ファイル（30%）が200行超、最大488行は推奨の2.4倍
3. **effort_booster.py の誤爆**: COMPLEX_KEYWORDS に「分析・検証・判断・バグ・エラー・方針」等の日常語が含まれ、社長の普通の発話で ultrathink が自動注入される状態（トークン倍増・レイテンシ増）
4. **ノイズ氾濫**: `commerce/ebay/tools/` 配下77個の中間生成物・`scrape_data.exe_extracted/` 190MB がgit追跡下にあり、Claudeのファイル探索コスト増・誤ヒット発生
5. **受動監視では追随不能**: Claude Code は急進化中（Skills・Effort・Hooks等）。肥大化監視だけでは新機能を取り込めず停滞 → 能動的な隔週サイクルが必要
6. **本診断〜復活の全過程は Campers 受講生向けに極めて価値あるコンテンツ素材**（今後「AIで戦うeBayセラー」ブランド構築の核にできる）

### 実装
- **梅案（本セッションで完了・commit eef37ab）**:
  - effort_booster厳選（20+語→16語）
  - tools/ ノイズ66ファイル削除・scrape_data.exe_extracted 190MB・pyinstxtractor.py・CLAUDE.md.backup・error.log・空ebay-tools/削除
  - .gitignore 11パターン追加・direct-sales旧パス修正
- **竹案（新セッションで実施予定）**:
  - `.claude/handoff_20260423_claude_code_refactor.md` にタスク14個を記載
  - 継続ルール25項目（feedback/user memory参照リスト）を冒頭明記
  - 新セッション起動プロンプト: `@.claude/handoff_20260423_claude_code_refactor.md を読んで、竹案を実行してください`

### 期待効果
- トークン消費 **40〜50%削減**
- レイテンシ **30〜40%改善**
- 社長の体感「元のパフォーマンス回復」
- 隔週サイクルで今後10年間の持続可能性確保
- Campers素材蓄積で将来のコンテンツ展開基盤

### 再評価のタイミング
- 隔週メンテで「竹案の効果が数字で出ていない」と判明した時
- Anthropic が Skills/Hooks の大幅仕様変更を発表した時
- Campersの「eBay×AI運営コース」正式開講時（素材を記事/動画化するタイミングで別途判断）

### 関連
- `.claude/handoff_20260423_claude_code_refactor.md`（竹案引き継ぎ）
- `memory/feedback_claude_code_persistent_maintenance.md`（運用ルール・新規）
- 参照元: Anthropic公式ベストプラクティス（`C:\Users\KEISUKE SHIMOMOTO\Downloads\claude-code-best-practices.md`）

---

## 更新ログ
| 日付 | 内容 |
|------|------|
| 2026-04-24 | **Claude Code運用の根本リファクタ実施**（梅案即効解毒＋竹案ハンドオフ作成）。肥大化診断・4点セット設計・隔週メンテサイクル導入・Campers素材化 |
| 2026-04-21 深夜 | **フォルダ構成を3事業階層に大規模リファクタ**（commerce/services/education/management）。失敗ゼロで完遂 |
| 2026-04-22 | BayChat AI Reply：次期モデルを **GPT-5-Nano** に仮決定（Gemini 2.5 Flash除外）・admin画面でGPTモデル変更可能を確認・Cowatech依頼不要 |
| 2026-04-20 夜 | BayChat AI Reply：FORCED_TEMPLATE除去・TO/FROM機能継続・admin_prompt v2.5方針確定（Slack送信済） |
| 2026-04-20 | Claude Code Routines採用見送り判断を追加 |
| 2026-04-20 | BayChat AI Replyの方針転換（プロンプト微修正→設計図整備優先）を記録 |
| 2026-03-31 | Google Sheets推奨出力の意思決定を追加 |
| 2026-03-22 | 初回作成。Campers・Cowatech・BayPack・Claude Code関連の判断根拠を社長から聴取し記録 |
