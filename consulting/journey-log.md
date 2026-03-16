# 実践ジャーニーログ
> Claude Code × eBay運営の実践記録。将来のコンサルコミュニティのコンテンツ素材として蓄積する。
> Claudeが日々のセッションから自動的に追記・更新していく。

---

## ログの読み方

| 記号 | 意味 |
|------|------|
| ✅ 実施 | 実際にやったこと |
| 💡 学び | 気づき・発見・ポイント |
| ⚠️ 失敗・迷い | 試行錯誤・上手くいかなかったこと |
| 📦 コンテンツ候補 | 将来の教材として使えるネタ |
| 🔧 仕組み | 作った仕組み・ツール・設定 |

---

## 2026年3月11日（火）〜13日（木） ― 基盤構築フェーズ

### やったこと
✅ Claude Code契約・初回起動
✅ マスタードキュメント（`/reffort/CLAUDE.md`）の設計・作成
✅ 全6部門フォルダ（ebay-analytics・baychat-ai・marketing・staff-ops・management・campers）の作成
✅ 各部門のCLAUDE.mdをQ&A形式でゼロから作成（仮情報ではなく実情報で）
✅ ユーザープロフィール・思考パターン記録ファイル（memory/）の整備

### 学び
💡 **「急がば回れ」の重要性**
最初にClaudeが仮情報でフォルダを作ったが、社長が「それは本当の情報ではない」と指摘。Q&A形式で1部門ずつ正確な情報を収集してから作成する方針に変更。土台がしっかりしていれば、その後のすべての作業精度が上がる。

💡 **CLAUDE.mdの仕組み理解**
フォルダごとにCLAUDE.mdを置くことで「部門専用Claude」として動く。本社（ルート）は経営全体、各部門は実務に特化。セッションをまたいでも記憶が引き継がれる。

💡 **メモリファイルの重要性**
`~/.claude/projects/.../memory/`にユーザー情報・フィードバック・プロジェクト情報を蓄積。これがClaudeの「長期記憶」になる。セッションが重くなったら新セッションを開始するだけでOK。

⚠️ **失敗：ファイル作成順序エラー**
存在しないファイルにいきなりWriteしようとしてエラー。Bashで先にtouchしてからRead→Writeの順序が必要（Windowsでは`New-Item`または`touch`で空ファイル作成）。

📦 **コンテンツ候補**
- Unit 1「CLAUDE.mdの作り方・部門別セッション設計」の実例として使える
- 「なぜ仮情報ではダメなのか」の説明に使える

---

## 2026年3月16日（月） ― eBay分析・自動化フェーズ開始

### やったこと
✅ Chatwork MCP設定（APIトークン取得・room_id確認・送信テスト）
✅ eBay週次レポートの分析スクリプト作成（Python）
   - `analyze_ads.py`：広告レポート分析
   - `analyze_traffic.py`：トラフィック×広告統合分析
   - `create_weekly_report.py`：Excel週次レポート自動生成
✅ 2026年2月13日〜3月15日の実データで分析実施
✅ 週次レポートのChatwork自動投稿をScheduled Taskとして設定（毎週月曜10:00）
✅ Consulting部門フォルダ・本ログファイルの作成

### 分析で判明した重要事実（実数値）
✅ 総出品数：2,856件のうち**売上ゼロが2,647件（92.7%）**
✅ 全体CVR：0.221%（業界平均2〜3%と比べると約1/10）
✅ 総収入$64,600に対し広告費合計$6,336（広告費率約9.8%）
✅ 完全死蔵（Impressionゼロ・Views0・Sales0）：14件をリストアップ

### 学び
💡 **eBayレポートの種類と使い分け**
eBay Seller Hubからダウンロードできるレポートは3種類：
- Traffic Report（CSV）：Impressions・CTR・Views・CVRなど表示系指標
- Advertising Sales Report（CSV）：PLG・PLPの広告効果
- Transaction Report（USD・CSV）：実際の収支・FVF・手数料など

この3つを統合して初めて「実態」が見える。バラバラに見ていると判断を誤る。

💡 **Transaction Reportの落とし穴**
`Transaction currency = USD`のみ使う。`ebaymag`（円建て）が混ざるとドル建て分析が狂う。

💡 **PLPとOffsiteはTransaction Reportに含まれない**
PLG（成果報酬型）はレポートに入るが、PLP・Offsiteは別途Seller Hubの広告管理画面で確認が必要。これを知らずに収支計算すると「利益が多く見える」状態になる。

💡 **「見られているのに売れない」と「そもそも見られていない」は別問題**
- Impressions低い → タイトル・カテゴリの問題（検索に引っかかっていない）
- Impressions高い・CTR低い → サムネイル・価格の問題
- CTR高い・CVR低い → 商品ページ内の問題（写真・説明・価格）
それぞれ打ち手が全く違う。

💡 **Python × Claudeのコンビで「コード不要」の自動化が実現**
Claudeがスクリプトを書き、ユーザーはコマンド1行を打つだけ。プログラミング未経験でも分析を自動化できる。

⚠️ **Scheduled Task（定期タスク）の使い方の学習コスト**
Chatworkへの週次自動投稿をScheduled Taskで設定したが、cronの書き方・タイムゾーン・実行環境の理解が必要。一度設定すれば完全自動になる価値は高い。

🔧 **作った仕組み**
- 毎週月曜10:00に自動でeBay週次レポートをChatwork【AI】eBay運営に投稿
- Excelレポート（5シート：概要・売上ゼロ・売れ筋・広告・育成候補）の自動生成

📦 **コンテンツ候補**
- Unit 2「eBayレポートのダウンロード→Claude分析の流れ」
- Unit 3「CVR・CTR・Impressionsの読み方と改善アクション」
- Unit 4「Pythonスクリプトを使った分析自動化（Claudeが書いてくれる）」
- Unit 4「Chatworkへの自動通知設定（MCP活用）」
- Unit 4「Scheduled Taskで週次自動化する方法」

---

## テンプレート・ツール一覧（作成済み）

| 名称 | 場所 | 概要 |
|------|------|------|
| analyze_ads.py | ebay-analytics/ | 広告レポート分析スクリプト |
| analyze_traffic.py | ebay-analytics/ | トラフィック×広告統合分析スクリプト |
| create_weekly_report.py | ebay-analytics/ | Excel週次レポート自動生成スクリプト |
| Chatwork送信コマンド | ebay-analytics/CLAUDE.md | Pythonワンライナーでのメッセージ送信 |
| 週次自動投稿 | Scheduled Task | 毎週月曜10:00自動実行 |

---

## 今後のログ追加予定

このファイルはClaudeが自動的に追記していく。
新しいセッションで「今日やったこと・学んだことをjourney-log.mdに記録して」と指示するか、
Claudeが自発的に「これはコンテンツになりますね」と提案して追記する。

---

*最終更新: 2026年3月16日*
