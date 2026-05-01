---
name: eBay 無在庫リサーチツール Ver.1
description: 2026-04-30 完成・5/31 ウェビナー実例デモ用・ライバル日本セラー出品 → 楽天/Yahoo 仕入候補 → 全コスト込み利益計算
type: project
originSessionId: fc475ca5-22e9-41d7-b335-3542505be00e
---
# eBay 無在庫リサーチツール Ver.1

**場所**: `commerce/ebay/tools/research/`
**完成日**: 2026-04-30 早朝（社長帰宅指示で一晩構築）
**目的**: 5/31 Campers ウェビナー実例デモ（70 名のセラー向け「AI×eBay でこんなことができる」の証拠）

## 動作確認済み（2026-04-29 夜）

クイック実行（4 キーワード × 4 件・約 2 分）で 5 件の利益計算済み候補が出た。
- 黒字 3 件・赤字 2 件
- TOP: DH0957-001 Nike Dunk Low Crazy Black Multi → eBay $177 / 楽天 ¥5,918 → **純利益 $86.69 (¥13,849) / マージン 49%**

## 主要ファイル

- `orchestrator.py` — メインエントリ
- `ebay_app_token.py` — Browse API 用 Application Token（client_credentials）
- `ebay_browse.py` — Browse API クライアント
- `rakuten_search.py` — 楽天市場 検索結果スクレイパー（HTML `__INITIAL_STATE__` 抽出）
- `yahoo_shopping.py` — Yahoo!ショッピング 検索結果スクレイパー（HTML `__NEXT_DATA__` 抽出）
- `matcher.py` — 型番抽出 + ブランド検出 + 検索キーワード生成 + 一致スコア
- `pricing.py` — FVF + 送料 + 関税 + 為替 + 国内コスト全部入りの利益計算
- `fx.py` — USD/JPY 自動取得（Frankfurter / open.er-api.com）
- `report.py` — HTML レポート生成

## 2026 年版で重要な前提（リサーチツールに反映済み）

- 米国 De Minimis $800 免税は **2025/8/29 廃止・継続中**
- Section 122 全国 10% 追加関税は **2026/2/24 施行・2026/7/24 失効予定**
- スニーカー $150+ は FVF 8% / per-order 免除（2024 StockX 対抗）
- eBay 検索ページのスクレイピングは User Agreement 違反 → Browse API のみ
- Finding API は 2025/02/05 死亡

## 社長判断待ち（5/31 までに）

- [ ] 楽天 Application ID + Application Key の登録（5 分・無料・即日発行）
- [ ] Yahoo!ショッピング Client ID（appid）の登録（10 分・無料）
- [ ] eBay Marketplace Insights API の Application Growth Check 申請（30 分＋数日 〜 数週間待ち）
- [ ] SpeedPAK 実勢レートカードの取得（Orange Connex ダッシュボードから）

## Ver.2 で改善する項目

- 楽天/Yahoo を公式 API に切替（HTML スクレイピング → API キー使用）
- Marketplace Insights API で「実販売 SOLD データ」エビデンス追加
- Reffort 自社販売実績起点モード（Sell Analytics の Sold 履歴から再出品候補抽出）
- Amazon.co.jp / メルカリ / 駿河屋 / モノタロウ の追加対応
- Claude API による商品マッチング精度向上（英→日翻訳・画像類似性）
- HIROUN 在庫表との連携（毎日メールで届く JAN リスト → 自動精査）
- Streamlit GUI 化（Campers メンバーが GUI で使える）

## 朝の引き継ぎ

`commerce/ebay/tools/research/handoff_20260430_morning.md` を最初に読む。
HTML レポートは `commerce/ebay/tools/research/results/research_<時刻>.html`。
