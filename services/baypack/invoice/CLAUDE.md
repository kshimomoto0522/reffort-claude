# BayPack請求書自動化 — ユニット層ルール
> 親: `/reffort/CLAUDE.md` → `/services/CLAUDE.md` → `/services/baypack/CLAUDE.md` を先に読むこと。

---

## このユニットの役割

BayPackの**共同運営費請求書**を月次で自動発行する仕組み。

- 請求先: リプロニーズ株式会社（Reproneeds Corporation）
- 請求内容: BayPack共同運営費（月1回、金額は月によって変動）
- 発行頻度: 月1回（タイミングは不定・だいたい毎月上旬）

---

## データフロー

```
[まとめシート row14 K列]
 共同運営費 支払額 ¥262,735
        │
        ▼ gspread 読取
[generate_invoice.py]
        │
        ├─ 請求書テンプレスプレッドシートの最新シート（請求書(2602)）を複製
        ├─ 新シート「請求書(2603)」を先頭に配置
        ├─ N1/N3/B9/I16 を更新
        │   N1  = RF04-03-05（物件番号：期-月-05）
        │   N3  = 発行日（デフォルト今日）
        │   B9  = BayPack共同運営費（3月）
        │   I16 = 262735
        └─ Google Drive API で PDF エクスポート
                │
                ▼
     [Desktop/請求書/【BayPack】共同運営費_請求書（2603）.pdf]
```

---

## 使い方

```bash
# 基本（最新月を自動検出・今日の発行日）
cd services/baypack/invoice
python generate_invoice.py

# dry-run（変更なしで計画のみ表示）
python generate_invoice.py --dry-run

# 月を指定
python generate_invoice.py --month 2026-04

# 発行日を指定（10日固定運用等）
python generate_invoice.py --issue-date 2026-05-10

# 金額を手動指定（まとめシートに反映前に先行発行したい等）
python generate_invoice.py --amount 150000 --month 2026-04
```

---

## 関連リソース

| 項目 | 値 |
|------|-----|
| ソーススプレッドシート | BayPack売上表_まとめ (ID: `1pnW_NcHdFmiTj0O9a7gwL79CaFt2ZUNEjUFqSQcvtx4`) |
| ソースシート名 | `まとめ` |
| ソース金額行 | Row 14「共同運営費 支払額」 |
| ソース月ヘッダー行 | Row 2 (形式: `YYYY年M月`) |
| ターゲットスプレッドシート | 【BayPack】Reffort請求書（川合さん用） (ID: `1e0axm3HzbQY1_a1nJQ5kKbtmozCt2NfF82nFfPaDHJQ`) |
| サービスアカウント | `reffort-claude@reffort-sheets.iam.gserviceaccount.com` |
| サービスアカウント鍵 | `commerce/ebay/analytics/reffort-sheets-fcbca5a4bbc2.json`（流用） |
| PDF出力先 | `C:\Users\KEISUKE SHIMOMOTO\Desktop\請求書\` |

---

## 重要ルール

- **実行は手動起動**（月の上旬にまとめシート確定後、社長が起動）。スケジュール化しない（確定タイミング不定のため）
- **発行済み月の再生成**はできない（既に同名シートがあるとエラー）→ 再生成は手動で Google Sheets から該当シートを削除してから再実行
- **期（決算6月基準）**: 1-6月 → 年-2022、7-12月 → 年-2021。例: 2026-03 → 4期、2026-07 → 5期
- **サービスアカウント権限**: ソース=閲覧、ターゲット=編集（Reffort側で付与済み）
- 本番データを扱うため、初回実行時は必ず `--dry-run` で確認してから実行

---

## トラブルシューティング

| 症状 | 原因 | 対応 |
|------|------|------|
| 認証エラー | サービスアカウント鍵のパスがずれた | `commerce/ebay/analytics/reffort-sheets-fcbca5a4bbc2.json` の存在確認 |
| ソース読取り失敗 | ソーススプレッドシートの権限剥奪 | 川合さんに閲覧権限の再付与を依頼 |
| ターゲット書込み失敗 | ターゲットスプレッドシートの権限剥奪 | サービスアカウントに編集権限を再付与 |
| 「既に存在しています」エラー | 同月の請求書シートを既に生成済み | Google Sheets から該当シートを手動削除してから再実行 |
| PDFのレイアウトが崩れる | `export_sheet_pdf()` のパラメータ調整が必要 | `portrait` / `fitw` / マージン等を変更 |
| 月ヘッダーをパースできない | まとめシートのフォーマット変更 | Row 2 の月ヘッダーが `YYYY年M月` 形式か確認 |

---

*最終更新: 2026年4月22日 初版作成・2026年3月分請求書生成テスト成功*
