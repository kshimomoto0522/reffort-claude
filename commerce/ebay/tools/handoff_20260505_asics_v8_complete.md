# 引継ぎ：ASICS在庫管理ツール v8 完成 → adidas適用

> **次セッション冒頭で必ず読むファイル（2026-05-05作成）**
> ASICS v5→v8 の改修が完了。次セッションは **共通する改良点を adidas にも適用する** 作業。

---

## 1. ASICS v5 → v8 で実装した機能（差分まとめ）

| Mod | 内容 | 適用対象 | 備考 |
|---|---|---|---|
| **A** | URL空/非ASICS → エラー情報表示 | scrape_data.py | スキップ理由可視化 |
| **B** | Bot検出 → エラー情報表示 | scrape_data.py | "Bot検出で取得失敗（次回再試行）" |
| **C** | メインパス後のリトライパス（最大5回・進捗ゼロで打ち切り） | scrape_data.py | スキップ救済 |
| **D** | 5件連続Bot検出 → 30分休憩（メイン+リトライ両方で発動） | scrape_data.py | Akamai cool-down |
| **E** | URL空 → eBay情報のみで `0/在Y` 表示 | scrape_data.py | 仕入先在庫切れ・eBay有在庫 対応 |
| **F** | Firefox 画面外配置（`set_window_position(-2000, -2000)`） | scrape_data.py | フォアグラウンド被害なし |
| **G1** | Q列ヘッダー「仕入れフラグ」→「出品削除」 | Sheets API（一回限り） | 既に本番反映済 |
| **G2** | Q列をチェックボックスに変換 | Sheets API（一回限り） | 既に本番反映済 |
| **G3** | GAS連携：チェック商品の一括削除予約 | GAS bound project + Z1 ポーリング | 動作確認済 |
| **その他** | parse_variations None ガード、API厳密化（APIエラー）、Policy違反対応（"Policy違反 (X/在Y)"）、自動再起動（1時間休憩→ループ）、resume機能（resume_state.json + SKUベース検索）、毎件書き込み（write_one_item で4セルbatch_update）、ゾンビガード（3キー全空でスキップ） | scrape_data.py | v6〜v8 で順次追加 |

---

## 2. 現在の本番状態

### スプレッドシート

| 項目 | 値 |
|---|---|
| シート名 | `【ASICS】在庫管理`（旧 `eBay在庫調整` から移行） |
| 構造 | 行1=ステータス行 / 行2=ヘッダー / 行3+=データ |
| Q列 | `出品削除` チェックボックス（行3〜606） |
| SPREADSHEET_KEY | `12SGD4RLze25JC6PWCFCOTxbk2qtL5UGp0D3B_mklK68` |

### ファイル

| 種類 | パス |
|---|---|
| 本番 exe（v8・65MB） | `C:\Users\KEISUKE SHIMOMOTO\Desktop\eBay在庫調整ツール（アシックス）\scrape_data.exe` |
| 本番 ソース（参考） | `eBay在庫調整ツール（アシックス）\scrape_data.py.fixed_v8_*` |
| ビルド作業フォルダ | `C:\Users\KEISUKE SHIMOMOTO\Desktop\asics_master_work\` |
| ビルド venv（Python 3.8.10 + 必要ライブラリ） | `asics_master_work\.venv\` |
| 修正後ソース | `asics_master_work\scrape_data.py` |
| Spec ファイル（PyInstaller） | `asics_master_work\scrape_data.spec` |
| ステージング保管 | `asics_master_work\staged\scrape_data_v8.exe` |

### バックアップ（順次蓄積）

旧 exe バックアップは `eBay在庫調整ツール（アシックス）\scrape_data.exe.bak_*`、不要になったら削除可。

### GAS bound プロジェクト（出品削除予約）

| 項目 | 値 |
|---|---|
| scriptId | `1L_zIKz5yW97qRpOqIAaCKzdrWmCIddowiPAiBvhHga93ELSGUUu-JhR1` |
| GASエディタ | `https://script.google.com/d/<scriptId>/edit` |
| ローカルコード | `commerce/ebay/tools/gas/asics_delete/` |
| 編集後の反映 | `cd commerce/ebay/tools/gas/asics_delete/ && clasp push` |
| Apps Script API | **有効化済**（アカウント設定で「オン」） |

### 運用中の動作（v8）

```
[起動]
  60秒カウントダウン (5秒ごとA1更新)
[空欄整理]
  compact_blank_rows（batch_update API で1コール削除）
[シート再読込]
  resume_state.json があれば SKU検索で再開位置決定
[フェーズ1: メインパス]
  各item処理直前に Z1='PENDING' チェック → 該当時GAS削除キュー実行
  process_one_item:
    1. ゾンビガード（3キー全空ならスキップ）
    2. Mod E: URL空 → eBayのみで 0/在Y 表示・在庫処理スキップ
    3. Mod A: 非ASICS → "ASICS以外..." エラー表示
    4. driver.get + Access Denied リトライ
    5. Mod B: Bot失敗 → エラー表示 + 連続カウント
    6. Mod D: 5件連続 → 30分休憩（休憩中もZ1ポーリング）
    7. 在庫処理停止 軽量チェック
    8. eBay GetItem (APIエラー / Policy違反 / Active で分岐)
    9. compute_inventory_status
   10. adjust_inventory（在庫処理）
   11. write_one_item（4セルbatch_update）
   12. save_resume
[フェーズ2: リトライパス（最大5回）]
  identify_retry_targets で救済対象抽出
  対象: 空 / APIエラー / Bot検出残
  対象外: 永続エラー / 正常済 / Policy違反 / 在庫処理停止 / 出品無し
[完了]
  clear_resume()
  A1: "処理完了 | 終了: ... | 編集OK"
[1時間休憩]
  30秒ごとにZ1ポーリング（GAS削除予約検知 → 即実行）
[次の周回]
  60秒カウントダウンから再開（先頭から）
```

---

## 3. 次セッション：adidas 共通化作業

### 対象ファイル

`C:\Users\KEISUKE SHIMOMOTO\Desktop\eBay在庫調整ツール（アシックス）\scrape_adidas_v1.py`

- **Python 3.14 直実行**（exe ビルド不要・編集即反映）
- 起動: `run_adidas.bat` / Windowsタスクスケジューラ `ASICS_adidas_*ji`
- シート名: `【adidas】在庫管理`（既に行1=status, 行2=header, 行3+=data 構造）

### adidas に未適用の v8 機能（チェックリスト）

| Mod | adidas 適用 | 備考 |
|---|---|---|
| ✅ **既に5/1適用済** 「出品無し」スキップ解除 | 適用済 | 確認のみ |
| ✅ **既に5/1適用済** redirect→リトライ強化 | 適用済 | 確認のみ |
| **A** URL空/非adidas → エラー情報表示 | **要適用** | adidas専用URLチェック（adidas.jp以外を除外） |
| **B** Bot検出 → エラー情報表示 | **要適用** | "Bot検出で取得失敗（次回再試行）" |
| **C** リトライパス（最大5回） | **要適用** | identify_retry_targets を adidas 用にも |
| **D** 5件連続Bot検出 → 30分休憩 | **要適用** | adidas は遅延が短い（10〜15秒）ので閾値は要検討 |
| **E** URL空 → eBayのみ表示 | **要適用** | 共通仕様 |
| **F** Firefox画面外配置 | **不要or任意** | adidas は既にヘッドレスモード（画面表示なし） |
| **G** Q列「出品削除」+ GAS削除予約 | **要適用（要協議）** | adidasシートにも同等の機能を入れるか？社長判断必要 |
| その他: APIエラー厳密化, Policy違反対応, 毎件書き込み, resume, 自動再起動, ゾンビガード, parse_variations Noneガード | **要適用** | ASICS と同じパターン |

### 注意点（ASICS との違い）

| 項目 | ASICS | adidas |
|---|---|---|
| 処理速度 | 遅延240秒 = 1件4分 = 605件40時間 | 遅延10〜15秒 = 1件0.5分 = 9件5分（現在9件のみ） |
| Firefox | visible（v8で画面外配置）| headless（変更不要） |
| Akamai | サイト側 | サイト側（同じ） |
| 商品数 | 605件 | 9件（CLAUDE.md記載・現状） |
| 1周時間 | 約40時間 | 約5分 |
| 自動再起動の必要性 | 1時間休憩 → ループ | 短時間で1周なので休憩短くてOK or 不要かも |

### 実装方針案

**保守的アプローチ（推奨）**：
1. adidasの現コードを読み込む（変更ポイント特定）
2. ASICS の v8 ロジックから「**adidas に必要な部分だけ**」コピー
3. テスト実行（9件しかないので素早く検証可能）
4. デプロイ（exe不要なのでファイル差し替えだけ）

**G（出品削除）について**：
- adidasの Q列も「出品削除」+ チェックボックスに変換可能
- adidas専用の GAS bound プロジェクト作成が必要（ASICSの GAS は ASICSシートのみに紐づく）
- ただし adidasは商品が9件と少ないので、社長作業で手動でeBay削除するのが現実的かも → 要協議

### 作業順序（次セッション）

1. このファイルを読んでコンテキスト把握
2. `scrape_adidas_v1.py` を読み込み（現状把握）
3. ASICS v8 と diff を作成（手動 or 機械的に）
4. 「adidas に適用すべき変更」リストを社長確認
5. 順次実装 → テスト
6. デプロイ
7. memory・development-history 更新

---

## 4. 技術メモ・落とし穴

### gspread 引数順問題（重要）

`ws.update([[val]], 'A1')` 形式は古い API で、**新シート構造で機能しない**ケースあり。  
v8 から **`ws.update_acell('A1', val)`** に統一済（write_status・他）。

### Apps Script API 経由で bound project を作成する方法

ユーザーが「拡張機能 → Apps Script」を手動で押す代わりに、以下の方法で完全自動化済（参考スクリプト残存）：

1. アカウント設定で Apps Script API を「オン」（一回限り、ブラウザ自動操作で実施済み）
2. clasp の OAuth トークン (`~/.clasprc.json`) を使ってアクセストークン更新
3. POST https://script.googleapis.com/v1/projects with `{title, parentId: <SHEET_ID>}` で bound project 作成
4. PUT https://script.googleapis.com/v1/projects/{scriptId}/content でコード push
5. `.clasp.json` に scriptId 反映

参考: `asics_master_work/create_gas_project.py`

### PyInstaller ビルド時の hidden imports

PyInstaller 4.6 で requests/charset_normalizer/certifi 等の隠れ依存を見落とすので、**spec の hiddenimports に collect_all を使って明示**する必要あり。  
参考: `asics_master_work/scrape_data.spec`

### Policy違反商品（IPR violation）の挙動

- GetItem: Failure ack だが Item要素は含まれる → root をそのまま返して処理続行可能
- ReviseFixedPriceItem: Warning ack（成功扱い）で在庫更新できる
- EndItem: 同上（5/5検証済）
- 検出: ErrorParameters の Value に `ON_HOLD_FIXABLE` 含まれる or ErrorCode `21920397` / `21920396`

---

## 5. テスト類（次セッションで活用可能）

| ファイル | 用途 |
|---|---|
| `asics_master_work/test_new_classes.py` | 11テスト・全通過済（次回も流用可能） |
| `asics_master_work/test_policy_violation.py` | Policy違反商品の挙動テスト |
| `asics_master_work/test_revise_on_policy.py` | ReviseFixedPriceItem on Policy違反 |
| `asics_master_work/test_end_policy.py` | EndItem on Policy違反 |
| `asics_master_work/diag_*.py` | スプレッドシート診断スクリプト群 |
| `asics_master_work/create_gas_project.py` | GAS bound project 作成（再利用可能・adidas でも使える） |

---

## 6. Memory 関連で更新したいフィードバック（次セッションで実施）

- `feedback_test_before_handoff.md`: v3/v5/v6 の見落としエピソード追記（safe_write_check のオフセットバグ等）
- 新規（任意）: `feedback_gspread_args.md`：gspread の引数順問題・update_acell 推奨

---

*作成: 2026-05-05 / 次セッション冒頭でこのファイルを最初に読む*
