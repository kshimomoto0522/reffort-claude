# eBay輸出事業 — 部門ドキュメント
> 親ドキュメント: `/reffort/CLAUDE.md` を必ず先に読むこと。
> このフォルダでは「eBay輸出事業の分析・改善・広告・スタッフ指示」に特化して動く。

---

## 事業概要

| 項目 | 内容 |
|------|------|
| 開始年 | 2021年 |
| 販売モデル | 基本：無在庫販売（一部有在庫あり） |
| 主な商材 | スニーカー（ナイキ・オニツカタイガー・ミズノ等）、スポーツ用品全般 |
| 出品数 | 約4,000SKU（大半が売上ゼロ状態） |
| 売上推移 | ピーク時（約2年前）：月$150,000 → 現在：月$60,000程度 |
| 販路 | eBay（メイン）＋ NYの顧客へのダイレクト販売 |

---

## スタッフ体制

| 名前 | 役割 | 主な担当業務 |
|------|------|------------|
| 佐藤 大将 | 運営リーダー | 運営全般・意思決定サポート |
| 須藤 記江 | サポート | 運営サポート・出品補助 |
| 高橋 紗英 | マーケ担当 兼 アシスタント | BayChat/BayPackの広告宣伝・SNS運用 ＋ eBay雑務。2026年3月入社。25歳。SNS・TikTokリテラシーあり。eBay・BayChat・BayPackの業務理解はまだこれから |
| 外注スタッフ | 梱包・発送 | 商品受取・梱包・ラベル発行・発送 |

---

## 仕入先

### メイン仕入先（約20サイト）
在庫管理ツールに登録済み。スクレイピングでeBayに在庫を自動反映。

| 種別 | 具体例 |
|------|--------|
| ブランド系 | ナイキ、オニツカタイガー、ミズノ等 |
| ECモール系 | 楽天、Yahooショッピング等 |
| 合計 | 約20サイト |

### 契約仕入先：HIROUN（活用できていない要改善先）
- スポーツ用品・健康系商材を取り扱う会社
- 仕入れ価格：6掛け程度（条件は良い）
- **現状：ほぼ活用できていない**
- 毎日エクセル（JANコード・単価入り）の在庫表がメールで届く
- 商材は低単価シューズが中心で人気商品が少ない
- 在庫表の精査に時間・気力がなく放置状態
- ヒットすれば在庫化も検討したい
- **Claudeにやってほしいこと：eBayで売れている・売れそうな商品をHIROUN在庫表から自動抽出する仕組みを作る**

---

## 配送・物流

| 項目 | 内容 |
|------|------|
| 主要配送会社 | Orange Connex / SpeedPak（eBayジャパン共同提供） |
| 実際の配送キャリア | FedEx または DHL |
| ラベル発行 | Cpass |
| BayPack在庫 | 返品在庫200品以上。発送依頼はBayPackツールから実施 |

---

## 使用ツール・スプレッドシート一覧

| ツール名 | 種別 | 役割 | 現状・課題 |
|---------|------|------|----------|
| 在庫管理ツール | カスタム開発（Cowatech修正中） | 仕入先サイトをスクレイピングしeBayに在庫反映 | **バグ多数**。在庫ありが出品されない・なしが出品され続ける。売上減の主因のひとつ |
| 仕入管理表 | スプレッドシート | 売れた商品の仕入情報記録。発送担当と共有 | 発送担当は受取日・送料を追記して使用 |
| 在庫管理表 | スプレッドシート | 有在庫（売れ筋・返品等）の管理 | **アナログ管理のためヒューマンエラーが起きやすい。eBay連携の在庫管理システムがほしい** |
| 商品管理リスト | スプレッドシート（スタッフ個別） | リサーチ結果記録。タイトル・価格・出品情報 | スタッフ各自が管理 |
| 収支集計ツール | カスタム開発（前任者作成）＋スプレッドシート | eBay APIでデータ収集→収支表に反映 | **PLG広告費のみ反映。PLP・Offsiteが未反映のため、実際の利益は収支表より少ない** |
| BayChat | SaaS（自社開発） | CS・メッセージ対応 | 通常運用中 |
| Cpass | 外部サービス | 配送ラベル発行 | 通常運用中 |

---

## 広告戦略

### 広告費の実態（2026/3/26確定・2/13〜3/15期間）

| 広告種別 | 月額費用 | 帰属売上 | ROAS | 備考 |
|---------|---------|---------|------|------|
| PLG | $3,446 | $68,963 | 20.0x（見かけ上） | **帰属率103%＝ほぼ全売上がPLGに帰属（異常）** |
| PLP | $491 | $4,580 | 9.3x | Mexico 66のみ。効果実証済み |
| Offsite | $1,928 | $17,030 | 8.83x | CPC $0.17。商品選択不可が弱点 |
| **合計** | **$5,865** | — | — | **年間$70,380（売上の8.8%）** |

### 重大な問題（2026/3/26発見）

**1. PLGキャンペーン10個重複**
- 全て「ルールベース」（全商品自動登録型）。4%×3 + 5%×5が同一商品に同時適用
- 個別商品のレート変更・削除がAPI不可
- → **「キーベース」キャンペーンへの統合が最優先課題**

**2. 2026年1月の帰属ルール変更（Any Buyer Model）**
- 旧: 広告クリックした本人が買った場合のみ課金
- 新: 誰かがクリック→別の人が買っても30日以内なら課金
- PLG帰属率が103%に（総売上より広告帰属売上が大きい異常状態）
- 実質「売上の5%を無条件で取られる広告税」化

**3. Offsite広告の非効率**
- 2,878商品がGoogleに広告表示。売れたのは58商品（2.0%）
- 1,491商品がクリックだけで売上ゼロ
- 売上ゼロ商品の削除がOffsite効率化に直結

**4. 価格帯と販売力の法則**
- $150-199が最強（販売実績率53%・平均LS 5.3個）
- $200超は38%、$250超は27%まで急落

### 広告最適化アクションプラン（進行中）
1. ⬜ PLGキャンペーン統合（10個→1個キーベース）
2. ⬜ テストA: PLG完全停止 30商品（生涯販売ゼロ）
3. ⬜ テストB: PLG 5%→2% 7商品（期間中PLG売上あり）
4. ⬜ テストC: PLP追加 6商品（V0298, S00444, V0299, H01399, V0347, H01258）※Mexico 66とは別キャンペーン
5. ⬜ 削除候補×Offsiteクリック浪費リストをスタッフ向け出力

### Marketing API
- OAuth認証: ✅ sell.marketingスコープ追加済み
- キャンペーン管理: ✅ 動作確認
- キーベースキャンペーン統合後は全操作API自動化可能

---

## 現在の緊急課題

| 優先度 | 課題 | 状況 |
|--------|------|------|
| 最高 | 在庫管理ツールのバグ | Cowatechに修正依頼中。在庫ありが出品されない・なしが出品され続ける |
| 高 | 売上構造の崩壊（CVR低下・売上ゼロSKUの大量存在） | 手動で大掃除中 |
| 高 | 収支計算の不正確さ（PLP・Offsite広告費が未反映） | API推定で一部対応済み |
| 中 | 不良在庫の処理（赤字オークション等） | 国内販売（ヤフオク・スニーカーダンク）も検討中 |
| 中 | 在庫管理表のヒューマンエラー | eBay連携システム化が必要 |

---

## 構造改革の方針

売上は以下の構造で決まる：
```
Impressions → CTR → Page Views → CVR → Sold
```
現在はCVRが低く、売上ゼロ比率が高い状態。問題は「出品数不足」ではなく「構造の崩れ」。

### 商品の4分類モデル

| 分類 | 内容 | アクション |
|------|------|----------|
| 🗑 削除 | 売れていない・改善見込みなし | End（取り下げ） |
| 🌱 育成 | 見られているが売れていない | 価格・タイトル・写真等を改善 |
| ⭐ 準売れ筋 | 少し売れている | 価格微調整してコア化 |
| 🔥 コア売れ筋 | よく売れている | 在庫確保・広告維持・集中強化 |

### 運営ルール
- 在庫0放置禁止
- 価格放置禁止
- 売れない商品は削除
- 毎週KPI確認
- 出品数より構造改善を評価する

---

## 通常業務フロー

### 1. 商品リサーチ（全員）
- eBay Product Researchで日本国内仕入れ可能な商品を検索
- 過去に売れたモデルの新作・類似モデル
- ライバルが出品してウォッチ数が多い商品・売れている商品
- 各自の『商品管理リスト』にタイトル・出品価格・情報を登録

### 2. 出品（出品担当）
- 商品管理リストをもとに毎日手動でeBayに出品

### 3. 仕入れ（商品が売れたら）
- 『仕入管理表』に発送日・SKU・型番・仕入先・URL・仕入日・仕入値・備考を入力
- 発送担当と共有

### 4. 発送
- 届いたら受取日・送料を入力
- CpassでFedEx/DHLラベル発行 → 梱包 → 発送

### 5. 有在庫の処理
- 売れたら『在庫管理表』でSOLD処理
- BayPack在庫の場合はBayPackツールから発送依頼

### 6. CS対応
- BayChatでメッセージ対応
- トラブル対応：リターン・INR（未着）・Dispute・Footware Sheet提出等

---

## ライバル・競合状況

- 2021年当時は先駆者としてトップセラーだったが、現在はパクリセラーに価格競争で負けている
- 無在庫販売のため参入障壁が低く、ライバルが増えやすい構造
- **Claudeにやってほしいこと：ライバルセラーの出品情報・売れ筋データを収集してリサーチに活用できる仕組みを作る**

---

## 理想の状態（段階別）

### 短期目標（手動でもまず実現する）
- 毎週eBayからレポートをダウンロード・集計してスタッフへ展開
- 過去データと比較しながら目標を追う
- 「今週何をすべきか」がスタッフ全員に明確になる

### 中長期目標（AI化）
- 在庫管理ツールの安定稼働（Cowatech対応完了後）
- HIROUN在庫表の自動精査・出品候補の自動抽出
- ライバルセラーの自動分析
- 広告のPDCAをAIが補助
- 収支をPLP・Offsite広告費含めて正確に自動集計
- 在庫管理表のeBay連携システム化
- **最終形：半分AI自動・半分スタッフがAIの結果をもとにアクション、という分業体制**

---

## 会社の基本情報

| 項目 | 内容 |
|------|------|
| 始業時刻 | **毎日10:00スタート**（スタッフへの通知・リマインダーは10:00以降に送ること） |
| 週次リマインダー | 毎週月曜10:00（Chatwork【AI】eBay運営 自動送信済み） |

---

## Claudeへの重要ルール（eBay部門専用）

- スタッフへの指示は佐藤・須藤・高橋の役割を踏まえて内容を分けること
- **スタッフへの自動通知は始業時刻の10:00以降に送ること**
- eBay APIのレート制限に注意。過剰なAPIコールを避ける
- 収支計算には必ずPLP・Offsiteの広告費を含めること
- 現状の収支表は実際の利益より高く見えていることを常に意識する
- 提案は「今すぐ手動でできること」と「将来の自動化」を分けて提示する
- 数字が出たら「だから何をすべきか」まで踏み込んで提言する
- 本番の顧客・注文データを扱う処理は必ず社長に確認を取ること
- レポートの出力形式は**Googleスプレッドシート優先**（Excelも可）

---

## Chatwork連携設定

| 項目 | 内容 |
|------|------|
| 送信アカウント | REFFORT AI（keishimomoto0522@gmail.com） |
| APIトークン保存場所 | `~/.claude.json`（MCP設定内） |
| 送信先ルーム | 【AI】eBay運営（room_id: **426169912**） |
| 送信方法 | `curl` または Chatwork MCP経由 |
| 設定日 | 2026年3月16日 |

### Chatworkへのメッセージ送信コマンド（テンプレート）
```bash
python -c "
import urllib.request, urllib.parse
token = 'bab3f1fbb9c63cb4e06abff11b4f2857'
room_id = '426169912'
msg = '【メッセージ内容】'
data = urllib.parse.urlencode({'body': msg}).encode()
req = urllib.request.Request(f'https://api.chatwork.com/v2/rooms/{room_id}/messages', data=data, method='POST')
req.add_header('X-ChatWorkToken', token)
with urllib.request.urlopen(req) as res:
    print('送信完了:', res.read().decode())
"
```

### 主要Chatworkルーム一覧
| ルーム名 | room_id | 用途 |
|---------|---------|------|
| 【AI】eBay運営 | 426169912 | AI通達・週次レポート（メイン） |
| ebay業務連絡 | 271411089 | スタッフ日常業務連絡 |
| 【KeiS】発送 | 289258037 | 発送業務 |
| 【KeiS】スニーカー | 319685466 | スニーカー商品関連 |
| 【Reffort】業務連絡 | 395343446 | 全社業務連絡 |

---

## 週次レポート分析スクリプト

| ファイル | 場所 | 役割 | バージョン |
|---------|------|------|-----------|
| `analyze_ads.py` | ebay-analytics/ | 広告レポート単体分析 | 旧 |
| `analyze_traffic.py` | ebay-analytics/ | Traffic×広告統合分析・result_traffic.txt出力 | 旧 |
| `create_weekly_report.py` | ebay-analytics/ | Excelレポート初版（5シート） | 旧 |
| `create_weekly_report_v2.py` | ebay-analytics/ | Excelレポート改訂版（7シート） | 旧 |
| **`create_weekly_report_v3.py`** | ebay-analytics/ | **Excel＋Google Sheets レポート最新版（12シート）** | **現行** |
| **`write_gsheets.py`** | ebay-analytics/ | **Google Sheets直接書き込みモジュール（v3から呼び出し）** | **現行** |
| **`send_weekly_report.py`** | ebay-analytics/ | **Chatworkへの自動配信（Excel＋Googleスプレッドシートリンク＋前週比コメント）** | **現行** |
| `weekly_history.json` | ebay-analytics/ | **週次履歴データ（前週比較の元データ・価格/在庫含む）絶対に削除しないこと** | 自動生成 |
| `weekly_notes.json` | ebay-analytics/ | **備考永続化ファイル（スタッフの書き込みを次週に引き継ぐ）** | 自動生成 |
| `reffort-sheets-*.json` | ebay-analytics/ | **Google Sheetsサービスアカウントキー（.gitignoreで除外）** | 秘密 |

### Google Sheets 連携設定
| 項目 | 内容 |
|------|------|
| スプレッドシート | eBay週次レポート_v3 |
| URL | https://docs.google.com/spreadsheets/d/1AT4x_qyohYiEs08RSHs5uFgqBAm51IRsY1ajybsJe0s |
| SPREADSHEET_ID | `1AT4x_qyohYiEs08RSHs5uFgqBAm51IRsY1ajybsJe0s` |
| サービスアカウント | reffort-claude@reffort-sheets.iam.gserviceaccount.com |
| プロジェクト | reffort-sheets（Google Cloud Console） |
| 認証方式 | サービスアカウントJSON鍵ファイル |
| 出力形式 | Excel（openpyxl）＋ Google Sheets（gspread）の両方を毎回出力 |

### 週次レポートの配信フロー（自動化済み）
**スケジュールタスク `monday-ebay-report-delivery` が毎週月曜10:00に自動実行:**
1. `create_weekly_report_v3.py` が実行される
   - GetOrders APIで最新トランザクション取得（CSVダウンロード不要）
   - WEEKS自動計算（月〜日の4週間）
   - Traffic Report・Ads Report CSVは手動ダウンロードが必要（APIなし）
   - Excel版を生成（openpyxl）
   - **Google Sheets版を直接書き込み（write_gsheets.py / gspread）**
2. `send_weekly_report.py` がExcelをChatwork【AI】eBay運営グループにアップロード
   - 挨拶＋前週比コメント（受注数・売上・CVR）付き
   - **Googleスプレッドシートリンクも配信メッセージに含む**

### 手動でレポートを再生成する場合
1. Traffic Report・Ads Report CSVをダウンロードして`create_weekly_report_v3.py`の先頭パスを更新
2. `py create_weekly_report_v3.py` を実行
3. テスト送信: `send_weekly_report.py` の `TEST_MODE = True` にして社長DM宛確認

### レポート構成（v3・12シート・Google Sheets対応）

| シート | 内容 | 主な目的 |
|--------|------|---------|
| 💬 AI総評 | 具体的商品名入りの要因分析・サイト別動向・今週やるべきこと | 全体方針・スタッフ共有 |
| 📊 サマリー | KPIブロック・週別サイト別売上（US/UK/EU/AU/CA）・売上ゼロ比率・収支サマリー | 全体把握・経営判断 |
| 🔥 コア売れ筋TOP15 | W4販売数ランキング・前週比Δ・CVR・PV・インプ・価格・PLP経由✅ | 在庫確保・広告強化 |
| 🚨 コア落ち | W3→W4でTOP15から外れた商品・価格・原因自動推測 | 異常検知・即対応 |
| ⭐ 準売れ筋 | sold>0・TOP15外・ポテンシャルスコア順・価格・備考 | 伸びしろ候補の育成 |
| 🌱 育成候補 | PV50以上・売上ゼロ・TOP20・価格・備考 | 購入障壁の発見・改善 |
| ⚠️ 要調査 | インプ500以上・売上ゼロ・掲載90日以上・価格・備考 | 在庫ツールバグ・仕入先URL切れの特定 |
| 🗑 削除候補 | L1:即削除 / L2:要確認・価格・削除判定（自動）・備考 | 断捨離・整理 |
| 🔥 コア売れ筋（月間） | 4週間合計のTOP15・価格 | 月間トレンド確認 |
| 🗑 削除候補（月間） | 4週間売上ゼロ・掲載90日以上・価格 | 確実な死蔵の特定 |
| 📈 改善追跡 | 前週「要調査・削除候補」→今週sold>0の改善成功商品・前週/今週の価格・在庫・PV・インプ比較 | スタッフのモチベーション |
| 📋 週次履歴 | weekly_history.jsonから自動蓄積 | 前週比較の基礎データ |

### v3の主な機能（2026/3/31更新）
- **💬 AI総評シート**：具体的商品名（【SKU】タイトル形式）で伸び・落ち・コア落ち原因を分析。「今週やるべきこと」を提示
- **通貨ベースサイト分類**：USD=US, GBP=UK, EUR=EU, AUD=Australia, CAD=Canada（TransactionSiteIDではなく通貨で判定）
- **サイト別売上をサマリーに統合**：【US】【UK】【EU】【AU】【CA】の注文数・売上を交互色で一覧表示
- **売上ゼロ比率（週次KPI）**：W1-W4ごとに売上ゼロSKU比率を表示（減少=改善）
- **前週カテゴリ正確化**：HISTORY_DATE_KEYをW4終了日（日曜）に変更。同一週の複数実行で上書き。6日以上前のデータのみ前週として参照
- **コア落ちシートに前週/今週カテゴリ2列**：カテゴリ変遷が一目でわかる
- **PLP経由列**：コア売れ筋にPLP広告経由の売上があれば✅表示
- **前週比表示を「110%/90%」形式に統一**（▲▼記号廃止）
- **Δ販売数は+3/-2形式**（記号なしの直感的表示）
- **Sell Analytics API（OAuth 2.0）完全対応**：Traffic CSV不要。日別・週別・商品別データを自動取得
- **CVR単位自動変換**：API（ratio 0.001）→ 表示（% 0.1%）を正しく変換
- **在庫数・掲載日数をseller_cacheから取得**：GetMyeBaySelling APIでQuantityAvailable/StartTimeを取得
- **全カウントSKUベース**：バリエーション数ではなくユニークSKU数を商品数として使用
- **weekly_history.json**：W4終了日をキーとして自動保存。テスト実行のゴミが溜まらない設計
- **GetOrders APIでトランザクション自動取得**：FVFはAPIから正確取得、International/PLG/Offsiteは売上比率推定
- **WEEKS自動計算**：今日基準で直近4週（月〜日）を自動生成
- **Chatwork自動配信**（`send_weekly_report.py`）：挨拶＋前週比コメント＋Excelアップロード＋Googleスプレッドシートリンク
- **Google Sheets直接書き込み**（`write_gsheets.py`）：gspread経由で全12シートをスプレッドシートに直接出力
- **2段ヘッダー**：3行目にカテゴリ（販売数・PV等）、4行目に詳細（W3・W4・Δ）。6シート対象
- **全シートに価格列**：seller_cacheから現在価格を取得。改善追跡では前週価格・前週在庫も表示
- **備考永続化**：weekly_notes.json ＋ スプレッドシートの備考セルから読み取り→次週に引き継ぎ
- **Item IDハイパーリンク**：全データシートのItem IDクリックでeBay出品ページに直接遷移
- **終了済み商品フィルター**：seller_cache不在 or 在庫0＆トラフィック0の商品を除外
- **CVR再計算**：Traffic API TOP200制限でCVR=0の商品をsold/pvから再計算
- **総出品数の週別表示**：weekly_history.jsonから各週末時点の値を参照（蓄積で精度向上）

### 商品分類の定義

| 分類 | 基準 | アクション |
|------|------|-----------|
| 🔥 コア売れ筋 | 販売数TOP15 | 在庫確保・広告維持 |
| ⭐ 準売れ筋 | sold>0・TOP15外 | 価格微調整でコア化を狙う |
| 🌱 育成候補 | sold=0・PV>=20 | 価格・タイトル・競合調査 |
| ⚠️ 要調査 | sold=0・imps>=500・掲載90日以上 | 在庫ツール確認・仕入先URL確認 |
| 🗑 削除L1（即削除） | imps=0・PV=0・sold=0 | eBayでウォッチ・累計販売数確認後に取り下げ |
| 🗑 削除L2（要確認） | imps<50・PV<5・sold=0・掲載180日以上 | 同上 |

### 削除判断の重要ルール
**削除候補シートのAPI自動判定を参考に最終確認すること：**
- **✅ 削除OK**：ウォッチ数10以下 & 生涯販売数0 → 削除推奨
- **⚠️ 要確認**：ウォッチ数11〜50 または 生涯販売数1以上 → 慎重に判断
- **🚫 削除NG**：ウォッチ数50超 または 生涯販売数4以上 → 削除禁止
- これらはGetMyeBaySelling APIで自動取得済み（Traffic CSVには含まれない情報）

### Traffic Report CSVの列構成（重要・パース参考）
- 0: Listing title / 1: eBay item ID / 2: Item Start Date / 3: Category
- 4: Current promoted listings status / 5: Quantity available
- 6: Total impressions / 7: CTR / 8: Quantity sold
- 9: % Top 20 Search Impressions / 10: CVR
- 21: Total Promoted Listings impressions（eBayサイト）
- 22: Total Promoted Offsite impressions（eBay外）
- 23: Total organic impressions on eBay site
- 24: Total page views
- ヘッダー行はindex=5（先頭5行がメタ情報）

### Transaction Report CSVの列構成（重要・パース参考）
- ヘッダー行はindex=11（先頭11行がメタ情報）
- 0: Transaction creation date（"Mar 15, 2026"形式）/ 1: Type
- 10: Net amount / 11: Payout currency / 17: Item ID / 21: Quantity
- 22: Item subtotal / 26: Final Value Fee - fixed / 27: Final Value Fee - variable
- 31: International fee / 34: Gross transaction amount / 35: Transaction currency / 38: Description
- **除外ルール**: Transaction currency = USD のみ集計（ebaymag = AUD/GBP/EUR/CAD）
- PLG費用: Type="Other fee", Description="Promoted Listings - General fee"
- Offsite費用: Type="Other fee", Description="Promoted Offsite fee"
- PLP費用: **Transaction Reportに含まれない** → 手入力（`PLP_FEE_TOTAL` 変数に設定）

### 分析で判明した重要な知識
- **Transaction Reportの除外ルール**: `Transaction currency = USD` のみ使用（ebaymag除外）
- **FVF率**: $150以上〜約8-9%、$150未満〜15-20%（eBay標準）
- **PLP費用**: Transaction Reportに**含まれない**（Seller Hub広告管理画面で別途確認し手入力）
- **Offsite費用**: Transaction Reportの「Promoted Offsite fee」に記載（クリック課金・CPC）
- **PLG**: 成果報酬型（売れた時のみ課金・CPS）
- **要調査1831件問題**: 全出品2856件の64%がインプあり売上ゼロ → 在庫ツールのバグが広範囲に影響している可能性が非常に高い。Cowatechへの修正依頼が最優先。

---

## 分析済みデータ（2026年2月13日〜3月15日）

### 収支サマリー（USD・341注文）
| 項目 | 金額 |
|------|------|
| 総収入（商品+送料） | $64,600 |
| FVF | -$5,455 |
| International fee | -$525 |
| PLG広告費 | -$3,446 |
| PLP広告費 | -$491 |
| Offsite広告費 | -$2,399 |
| **eBay控除後手取り** | **$52,284** |

### パフォーマンス指標
| 指標 | 数値 |
|------|------|
| 総出品数 | 2,856件 |
| 売上ゼロ | 2,647件（92.7%） |
| 全体CTR | 0.491% |
| 全体CVR | 0.221% |
| 完全死蔵（削除済み候補） | 14件 |

### 売れ筋TOP3
1. Onitsuka Tiger MEXICO 66 Kill Bill YELLOW BLACK（13件・CVR1.1%）
2. Onitsuka Tiger MEXICO 66 BIRCH PEACOAT（8件・CVR0.6%）
3. PUMA Speed Cat Wedge Totally Taupe（8件・CVR0.2%※サイズ在庫問題）

---

## 関連ファイル

| ファイル | 状態 |
|---------|------|
| eBay週次レポート_20260315.xlsx | ✅ 作成済み（5シート構成・旧版） |
| **eBay週次レポート_v2_20260315.xlsx** | **✅ 作成済み（7シート構成・現行版）** |
| result_traffic.txt | ✅ 作成済み（テキスト版レポート） |
| 週次レビューテンプレート | 未作成 |
| スタッフ向け商品管理マニュアル | 未作成 |

---

## 🚀 次のセッションで最初にやること

> このセクションは次回eBay専用セッション開始直後に確認すること。

### 継続タスク（優先順）
1. **完全死蔵14件の削除確認**（佐藤さんに実施依頼 or 確認）
2. **収支表にPLP・Offsite費用を追加**（毎月の実態把握のため）
3. ~~Googleスプレッドシート対応~~ ✅ 完了（2026/3/31・12シート・2段ヘッダー・備考永続化）
4. ~~eBay API連携（GetMyeBaySelling・SKU・ウォッチ数・生涯販売数・現在価格）~~ ✅ 完了（2026/3/18）
5. ~~週次レポート自動配信（Chatworkグループ）~~ ✅ 完了（2026/3/20）
6. ~~GetOrders APIでTransaction CSV不要化~~ ✅ 完了（2026/3/20）
7. ~~WEEKS自動計算（月〜日）~~ ✅ 完了（2026/3/20）
8. ~~要調査・削除候補にチェックボックス（DataValidation）~~ ✅ 完了（2026/3/20）

### 中期ロードマップ（今後取り組む順）
1. ~~資料の精度アップ~~ ✅ 完了
2. ~~週次・月次報告書の仕様定義~~ ✅ 完了
3. ~~eBay API活用（GetMyeBaySelling + GetOrders）~~ ✅ 完了
4. ~~半自動化（API取得 → Excel生成 → Chatwork配信）~~ ✅ 完了
5. ~~Googleスプレッドシート対応（ExcelからGoogleスプレッドシートへの移行）~~ ✅ 完了（2026/3/31）
6. ~~eBay Sell Analytics API（OAuth2.0）~~ ✅ 完了（Traffic API自動取得済み）
7. **完全自動化**（Ads CSVも不要にする）← **← 次はここ**

### 次回レポート時の注意
- Transaction CSVは不要（GetOrders APIで自動取得済み）
- **Traffic Report・Advertising Report CSVは引き続き手動ダウンロードが必要**
- PLP費用は手動確認が必要（Seller Hub広告管理画面で確認し `PLP_FEE_TOTAL` 変数に入力）
- International/PLG/Offsite費用はAPIで取得できないため売上比率推定（Intl 0.8%, PLG 5.3%, Offsite 3.7%）

---

*最終更新: 2026年3月31日（Google Sheets対応完了・2段ヘッダー・全シート価格列・改善追跡に前週価格/在庫・備考永続化）*
*変更があれば随時更新すること*
