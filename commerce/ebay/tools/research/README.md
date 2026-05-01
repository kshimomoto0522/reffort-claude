# eBay 無在庫リサーチツール（Ver.1）

> 2026-04-29 夜 / Claude が一晩で構築した Ver.1。5/31 Campers ウェビナー実例デモ用。

## ひとことで

「eBay で **日本セラーが米国向けに売っている商品** を見つけ、その商品が **楽天/Yahoo!ショッピングで仕入れられるか** を自動チェックし、**全コスト（FVF・送料・関税・為替）を入れた純利益** を計算するツール」。

「ライバルが売れている商品 = 確実に売れる商品」「日本にしかない商品 = 米国側で価格優位」を起点に、無在庫転売の判断材料を 1 商品あたり数秒で出す。

## 5/31 デモで見せたい流れ

```
1. ターミナルで `python orchestrator.py --quick`（4 キーワード × 4 件 = 1 〜 2 分）
2. 結果 HTML が `results/research_<時刻>.html` に出る
3. ブラウザで開く → 利益順に並んだカード一覧
4. 1 件ずつ「eBay 売価 / 仕入先リンク / コスト内訳 / 純利益」を解説
5. 黒字候補の中から「これなら出品候補に登録すべき」を 1 〜 2 件選ぶ
```

「手作業なら 1 商品で 15 分かかる作業を、AI と公式 API で 5 〜 10 秒」がメッセージ。

## アーキテクチャ

```
┌──────────────────────┐
│ orchestrator.py      │  キーワード一覧 × 件数で eBay 検索
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐    ┌──────────────────────┐
│ ebay_browse.py       │ ── │ ebay_app_token.py    │  client_credentials grant
│  Browse API          │    │  Application Token   │  Browse API 用 token 自動更新
└──────────┬───────────┘    └──────────────────────┘
           │ 日本セラー商品（itemLocationCountry=JP）
           ▼
┌──────────────────────┐
│ matcher.py           │  タイトル → 型番抽出 → 検索キーワード生成
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐    ┌──────────────────────┐
│ rakuten_search.py    │    │ yahoo_shopping.py    │  公式 API キー登録待ちの間
│  HTML __INITIAL_STATE│    │  HTML __NEXT_DATA__  │  HTML スクレイピングで暫定動作
└──────────┬───────────┘    └──────────┬───────────┘
           └──────┬──────────────────────┘
                  ▼
        ┌──────────────────────┐
        │ matcher.match_score  │  GTIN・型番・ブランド・タイトル類似度で 0-100 採点
        └──────────┬───────────┘
                   │ 一致スコア >= 45 の最安候補
                   ▼
        ┌──────────────────────┐    ┌──────────────────────┐
        │ pricing.py           │ ── │ fx.py                │  USD/JPY 自動取得
        │  全コスト計算        │    │  Frankfurter / ECB    │
        └──────────┬───────────┘    └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ report.py            │  CSV / JSON / HTML を `results/` に保存
        └──────────────────────┘
```

## 何が「2026 年版」として正確か

リサーチエージェントが公式ソース横断で確認した最新事実を反映済み:

- **米国 De Minimis $800 免税は 2025/8/29 廃止・2026/4 現在も継続中** → $1 でも関税申告必須
- **Section 122 全国 10% 追加関税は 2026/2/24 施行・2026/7/24 失効予定**
- **eBay スニーカー $150 以上は FVF 8% / per-order 免除**（2024 年 StockX 対抗）
- **eBay 検索ページのスクレイピングは User Agreement 違反**（Anthropic robots.txt block）→ Browse API のみ使用
- **Finding API は 2025/02/05 死亡** → 旧ツールの引用ソースは無効
- 為替 USD/JPY = 159 〜 160 円台 / 自動取得（`fx.py`）

## ファイル構成

| ファイル | 役割 |
|---------|------|
| `orchestrator.py` | メインエントリ。キーワード × 件数を回して結果を出す |
| `ebay_app_token.py` | Browse API 用 Application Token 取得（client_credentials grant） |
| `ebay_browse.py` | Browse API クライアント（item_summary/search） |
| `rakuten_search.py` | 楽天市場 検索結果スクレイパー（`__INITIAL_STATE__` JSON 抽出） |
| `yahoo_shopping.py` | Yahoo!ショッピング 検索結果スクレイパー（`__NEXT_DATA__` JSON 抽出） |
| `matcher.py` | 型番抽出・ブランド検出・検索キーワード生成・一致スコア計算 |
| `pricing.py` | FVF・送料・関税・為替・国内コスト全部入りの利益計算 |
| `fx.py` | USD/JPY 為替レート自動取得（30 分キャッシュ） |
| `report.py` | HTML レポート生成（紫テーマ・カード形式・社長指定の UI ルール準拠） |
| `cache/` | App Token・FX レートのローカルキャッシュ |
| `results/` | 実行結果（CSV / JSON / HTML） |

## 使い方

```bash
# クイックテスト（4 キーワード × 4 件・約 2 分）
python orchestrator.py --quick

# 本番実行（13 キーワード × 6 件・約 30 分）
python orchestrator.py

# キーワードあたり件数を増やす
python orchestrator.py --items 10

# 価格帯を絞る
python orchestrator.py --min-price 100 --max-price 400
```

実行後の HTML は `results/research_<タイムスタンプ>.html`。 ブラウザで開けば即見られる構造。

## 限界・注意点（2026-04-29 Ver.1 時点）

| 項目 | Ver.1 の状態 | Ver.2 で改善 |
|------|------------|-------------|
| eBay の SOLD（実販売）データ | × 取れない（公式 Marketplace Insights API は申請承認制・新規受付停止状態の報告あり） | 申請通れば「過去 90 日に売れた商品」の確実なエビデンスに切替 |
| 楽天 / Yahoo | △ HTML スクレイピング暫定動作（robots.txt 範囲内・rate limit 1.2 秒） | 公式 API キー登録後（楽天 Application ID / Yahoo Client ID）に切替 |
| 商品マッチング | ○ 型番・ブランド・タイトル類似度（regex + difflib） | Claude API で英→日タイトル翻訳・画像類似性追加 |
| Amazon.co.jp | × Ver.1 では除外（PA-API は 2026/5/15 廃止 + 10 件売上要件） | keepa 有料 API で代替検討 |
| メルカリ・ヤフオク・駿河屋・モノタロウ | × 未対応 | カテゴリ別に追加（特に駿河屋: コレクター系で強い） |
| 重量推定 | △ カテゴリから固定値（1.0 / 1.2 / 1.5 / 3.0 kg） | eBay 商品詳細 API で実重量取得 |
| 関税分類 | △ 簡易マッピング（スニーカー革底/合成・カメラ・楽器・衣類等） | HTS コード自動判定 + Reffort カテゴリ別実勢関税の蓄積 |
| 自社販売実績起点モード | × 未実装 | Reffort の Sell Analytics データから「過去に売れた商品」を起点にする |

## 5/31 デモまでの追加要望（社長判断必要）

優先度高:

1. **楽天 Application ID / Application Key の登録**（5 分・無料・即日発行）
   - https://webservice.rakuten.co.jp/ から登録
   - これで HTML スクレイピングを公式 API に切替（安定性 ↑、JAN 直叩き可）
2. **Yahoo!ショッピング Client ID（appid）の登録**（10 分・無料・Yahoo JAPAN ID 必要）
   - https://e.developer.yahoo.co.jp/dashboard/
   - V3 itemSearch API で `jan_code` 直叩き可能になる
3. **eBay Marketplace Insights API の Application Growth Check 申請**（30 分申請＋数日〜数週間待ち）
   - https://developer.ebay.com/ で自社アプリの settings から
   - 承認されれば「過去 90 日に売れた商品実績」が公式に取れる ⇒ 圧倒的差別化
   - 申請 use case: 「自社運営 eBay ストア + Campers スクール（70 名のセラー教育）の市場分析」

優先度中:

4. SpeedPAK 実勢レートカードの取得 → `pricing.SHIPPING_TABLE` 上書き
5. eBay Promoted Listings 平均レートの取得 → `pricing.ProfitInputs.promoted_listing_rate` 反映
6. Reffort 自社販売実績（過去 6 ヶ月の Sold 商品）を起点に「再出品候補」を出すモード追加

## 既知の改善点（コード側）

- `matcher.MODEL_CODE_PATTERNS` は対応するブランドが増えれば随時追加（現在: Nike / Mizuno / Onitsuka / Tamiya / Sony / Canon / Nikon / 一般）
- `pricing.CATEGORY_HINTS` のキーワード正規表現はカテゴリが増えれば追加
- `yahoo_shopping._find_search_items` の動的キーパスは Yahoo の Next.js 構造変更で追従が必要になる可能性

## ストレッチゴール（Ver.3 以降）

- Streamlit でブラウザ UI 化（社長 / Campers メンバーが GUI で使える）
- 「定点監視」モード（同じ商品を毎日価格チェックして、仕入価格が下がったら通知）
- HIROUN エクセル在庫表（毎日メールで届く JAN リスト）と連携 → 自動で eBay 売価予測 + 利益計算
- Claude API でタイトル/写真の出品最適化提案

---

**作成: 2026-04-29 夜（社長帰宅後）／ Claude Opus 4.7 (1M)**
**5/31 ウェビナーまでに Ver.2 完成・本番運用可能化が目標**
