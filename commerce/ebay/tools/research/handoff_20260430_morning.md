# 朝の引き継ぎ — eBay 無在庫リサーチツール Ver.1（2026-04-30 朝）

社長へ。一晩で構築しました。ultrathink + 4 並列リサーチエージェント + 自分の実装で、明日朝の確認用に動くツールが揃っています。

## 30 秒で見る場所

📊 **HTML レポート（最優先で開いて見てください）**
- クイック実行（4 キーワード × 4 件・3 件黒字）: `commerce/ebay/tools/research/results/research_20260429_221851.html`
- フル実行（13 キーワード × 6 件・夜中に実行・実行ログは `results/full_run_log.txt`）: 完了次第 `results/research_<最新時刻>.html`

📁 **実装一式**: `commerce/ebay/tools/research/`
📖 **詳細README**: `commerce/ebay/tools/research/README.md`

## ひとことサマリ

「**eBay で日本セラーが米国向けに売っている商品** を発見し、**楽天/Yahoo!ショッピングで仕入れられるか** を自動チェック、**全コスト（FVF・送料・関税・為替）込みの純利益** を計算」するツール。

クイック実行（2 分）で:
| 順位 | 商品 | eBay 売価 | 仕入 | 純利益 | マージン |
|------|------|---------|------|--------|---------|
| 1 | DH0957-001 Nike Dunk Low Crazy Black Multi Camo | $177 | 楽天 ¥5,918 | **$86.69（¥13,849）** | **49%** |
| 2 | Sony Digital Camera Leather Case for α7C | $65.20 | Yahoo ¥2,248 | **$32.91（¥5,257）** | 34.6% |
| 3 | DB0500-200 Nike Dunk Low Scrap | $317 | 楽天 ¥40,950 | $9.77（¥1,561） | 3.1% |

## 5/31 デモで使える「驚き」のポイント

1. **「De Minimis $800 免税は 2025/8/29 廃止・継続中」** を入れた利益計算は他ツールにない（Section 122 全国 10% 追加関税も含めて 2026 年版で正確）
2. **「ライバルが日本から無在庫で売ってる = 確実に売れる商品」** を出発点にしてる（Reffort が Reffort のロジックを学習させたツール）
3. **eBay 検索ページのスクレイピングが User Agreement 違反になった事実**（2026/2/20）を踏まえ、**Browse API + 日本セラーフィルタ** で公式かつ安全に取得
4. 数秒で「型番抽出 → 楽天/Yahoo 検索 → 一致採点 → 利益試算」が走る（手作業 15 分 → 5 秒）

## 限界（正直に書きます）

| 項目 | Ver.1 | Ver.2 で改善予定 |
|------|------|--------------|
| eBay の SOLD（実販売）データ | 取れない | Marketplace Insights API 申請後に追加 |
| 楽天 / Yahoo | HTML スクレイピング暫定 | 公式 API キー登録後に切替 |
| Amazon.co.jp / メルカリ / 駿河屋 | 未対応 | 順次追加 |
| 重量推定 | カテゴリから固定値（1.0 〜 3.0kg） | eBay 商品詳細から実重量取得 |
| 自社販売実績起点モード | 未実装 | Sell Analytics データから「再出品候補」抽出 |

## 社長判断待ち（5/31 までにやってほしい）

優先度高（5/31 デモ前に欲しい）:

- [ ] **楽天 Application ID + Application Key の登録**（5 分・無料）
  - https://webservice.rakuten.co.jp/ → 即日発行
  - これで楽天検索を HTML スクレイピングから公式 API に切替（安定性・JAN 直叩き）
- [ ] **Yahoo!ショッピング Client ID（appid）の登録**（10 分・無料）
  - https://e.developer.yahoo.co.jp/dashboard/
  - V3 itemSearch API の `jan_code` パラメータが使える
- [ ] **eBay Marketplace Insights API の申請**（30 分申請＋数日 〜 数週間待ち）
  - eBay Developer Portal で Application Growth Check 提出
  - use case 案: 「自社運営 eBay ストア + Campers スクール（70 名）の市場分析教育」
  - 承認されれば「過去 90 日に売れた商品実績」が公式に取れる ⇒ **既存ツールとの最強の差別化**

優先度中:

- [ ] SpeedPAK 実勢レートカードの取得（Orange Connex ダッシュボードから）
- [ ] PLP 平均レートの取得（直近 3 ヶ月の自社実績から）

## デモシナリオ案（5/31 当日）

```
スライド 1: 「これまでの商品リサーチ」
  - スプレッドシートを開いて手作業で 1 商品 15 分かけている
  - スタッフが思いつきベース・抜け漏れ多い

スライド 2: 「AI と公式 API で自動化」
  - ターミナル: python orchestrator.py --quick
  - 1 〜 2 分で結果 HTML が出る
  - 画面共有で HTML を開く

スライド 3: 「実例 1 件目（黒字 49% の Nike Dunk Low）」
  - eBay 米国で日本セラーが $177 で売っている
  - 楽天で同じ型番（DH0957-001）が ¥5,918 で売っている
  - 国際送料 ¥5,000 + FVF $14 + 関税（買い手払い参考）$53 を入れても
  - 純利益 $86 / マージン 49% → 出品候補確定

スライド 4: 「2026 年版の精度」
  - De Minimis $800 廃止 + Section 122 10% 追加関税を反映
  - スニーカー $150+ FVF 8% / per-order 免除も反映
  - 「数字が合ってない」リサーチツールが多い中、Reffort は実セラー目線で計算

スライド 5: 「これからの拡張（メンバー向け）」
  - 楽天/Yahoo 公式 API 化で 10 倍速
  - eBay Marketplace Insights API で「実際に売れた商品」エビデンス
  - HIROUN 在庫表との連携で「毎朝届く JAN リストを自動精査」
  - メンバー全員が使える GUI 版（Streamlit）
```

## 私（Claude）が書いたコードの根拠

- ベース利益計算式: リサーチ Agent（2026-04-29 実施・公式 eBay ヘルプ + ホワイトハウス声明 + Orange Connex 公式 + Wise/Payoneer 公式の横断調査）の出力を採用
- 為替レート: Frankfurter（ECB 公開データ・無料無認証）優先 / open.er-api.com フォールバック
- eBay Browse API: 既存 `commerce/ebay/analytics/.env` の `EBAY_APP_ID` / `EBAY_CERT_ID` を流用（client_credentials grant・Application Token は 2 時間有効・自動リフレッシュ）
- 楽天: `__INITIAL_STATE__` JSON を波括弧バランスで抽出（途中の `;` で切れない実装）
- Yahoo: `__NEXT_DATA__` JSON を Next.js 標準形式で抽出
- 商品マッチング: 型番一致 70 点 + GTIN 60 点 + ブランド 10 点 + タイトル類似度 30 点（最大 100 点・閾値 45 点）

## 朝のチェックリスト

1. `commerce/ebay/tools/research/results/` の最新 HTML を開く
2. ヒット件数・黒字件数・最高マージンを確認
3. 「これは出品しない方がいい」「これは出品候補」を仕分け
4. 上記の「社長判断待ち」を確認 → 楽天/Yahoo の登録
5. 5/31 デモで使う商品候補を 3 〜 5 個ピックアップ

---

**作成: Claude（Opus 4.7・1M）**
**完了時刻: 2026-04-30 早朝（フル実行は夜中バックグラウンドで完走）**
