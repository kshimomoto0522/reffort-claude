# 2026年 Q1 分析スナップショット（2026/2/13〜3/15）

> 一時点の実績データ。時間が経つと鮮度が落ちるため archive/ 配下に退避。
> Claudeは通常このファイルを参照しない。必要な際は社長が明示的に指示。
> archive/ 移動日: 2026-04-24（竹案T2実施時）

---

## 収支サマリー（USD・341注文）

| 項目 | 金額 |
|------|------|
| 総収入（商品+送料） | $64,600 |
| FVF | -$5,455 |
| International fee | -$525 |
| PLG広告費 | -$3,446 |
| PLP広告費 | -$491 |
| Offsite広告費 | -$2,399 |
| **eBay控除後手取り** | **$52,284** |

## パフォーマンス指標

| 指標 | 数値 |
|------|------|
| 総出品数 | 2,856件 |
| 売上ゼロ | 2,647件（92.7%） |
| 全体CTR | 0.491% |
| 全体CVR | 0.221% |
| 完全死蔵（削除済み候補） | 14件 |

## 売れ筋TOP3

1. Onitsuka Tiger MEXICO 66 Kill Bill YELLOW BLACK（13件・CVR1.1%）
2. Onitsuka Tiger MEXICO 66 BIRCH PEACOAT（8件・CVR0.6%）
3. PUMA Speed Cat Wedge Totally Taupe（8件・CVR0.2%※サイズ在庫問題）

---

## 2026/3/31時点の「次にやること」一覧（現在は完了済みが大半）

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
4. ~~半自動化(API取得 → Excel生成 → Chatwork配信)~~ ✅ 完了
5. ~~Googleスプレッドシート対応(ExcelからGoogleスプレッドシートへの移行)~~ ✅ 完了（2026/3/31）
6. ~~eBay Sell Analytics API（OAuth2.0）~~ ✅ 完了（Traffic API自動取得済み）
7. **完全自動化**（Ads CSVも不要にする）← **← 次はここ**

### 次回レポート時の注意

- Transaction CSVは不要（GetOrders APIで自動取得済み）
- **Traffic Report・Advertising Report CSVは引き続き手動ダウンロードが必要**
- PLP費用は手動確認が必要（Seller Hub広告管理画面で確認し `PLP_FEE_TOTAL` 変数に入力）
- International/PLG/Offsite費用はAPIで取得できないため売上比率推定（Intl 0.8%, PLG 5.3%, Offsite 3.7%）

---

*スナップショット作成: 2026-03-31*
*archive/ 移動: 2026-04-24（竹案T2実施時）*
