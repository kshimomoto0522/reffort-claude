# ASICSツール v8+補正版 詳細仕様（2026-05-06 現行）

> 親ドキュメント: `commerce/ebay/tools/CLAUDE.md`
> このファイルはASICSツール v8+補正版の詳細仕様。日常運用は親ドキュメントの要点ブロックで十分。

---

## 主要仕様
- **方式**: Firefox/Selenium（visible だが画面外配置 = `set_window_position(-2000, -2000)`）
- **ビルド**: PyInstaller 4.6 + Python 3.8.10（venv: `asics_master_work\.venv`）・5/6 13:47ビルド
- **シート名**: `【ASICS】在庫管理`（旧 `eBay在庫調整` から移行）
- **シート構造**: 行1=ステータス / 行2=ヘッダー / 行3+=データ
- **SPREADSHEET_KEY**: `12SGD4RLze25JC6PWCFCOTxbk2qtL5UGp0D3B_mklK68`
- **待機時間**: **210秒**（Akamai対策・5/6 240→210秒に短縮試行中）
- **書き込み**: 毎件書き込み（write_one_item で4セルbatch_update API）
- **1周時間**: 約35時間（605件 × 3.5分）
- **自動再起動**: 1周完了後 1時間休憩 → 自動ループ

## v8+補正版の機能一覧
- ✅ Mod A: URL空/非ASICS → エラー情報表示
- ✅ Mod B: Bot検出 → エラー情報表示
- ✅ Mod C: メインパス後のリトライパス（最大5回）
- ✅ Mod D: 5件連続Bot検出 → 30分休憩
- ✅ Mod E: URL空 → eBay情報のみで `0/在Y` 表示
- ✅ Mod F: Firefox 画面外配置
- ✅ Mod G: GAS連携 出品削除予約（Q列チェックボックス + Z1ポーリング）
- ✅ Policy違反対応・APIエラー厳密化・resume機能・ゾンビガード 他
- 🆕 **論点①**（5/6）: identify_retry_targets で URL空+ItemIDあり+未処理行を Mod E 対象に追加（過去exeで素通り→永遠に未処理放置の構造的問題を解消）
- 🆕 **論点②**（5/6）: Policy違反表示を在庫状況（X/在Y）とエラー情報（Policy違反）に分離（compute_inventory_status の戻り値を3要素タプルに拡張）
- 🆕 **論点③**（5/6）: EndItem ErrorCode 1047（auction has been closed）を成功扱いに分岐 → eBay側End済の出品も自動クリーンアップ

## 待機時間の戻し条件（210秒試行）
- 5件連続Bot検出（30分休憩）が **2回以上/周** 発生 → config.xlsx の遅延秒数を 240 に戻す
- 戻し方:
  ```bash
  python -c "import pandas as pd; df=pd.read_excel('config.xlsx'); df.loc[0,'遅延秒数']=240; df.to_excel('config.xlsx',index=False)"
  ```
  → exe再起動

## タスクスケジューラ
v8 は自動再起動するので、**スケジューラタスクは不要**（旧 ASICS_v2_*ji は無効化推奨）。
過去の登録: ASICS_v2_01ji / 09ji / 17ji（残してOKだが2重起動リスクあり）

## 運用ルール
| 操作 | タイミング |
|------|----------|
| 行削除・追加 | いつでもOK（次回起動時の compact が空行を物理削除） |
| Q列チェック → 削除予約 | いつでもOK（**最大4分以内**にツールが検知して削除実行） |
| ItemID/SKU/URL のセル削除 | OK（compact が物理削除） |

## GAS bound プロジェクト（出品削除予約）
- scriptId: `1L_zIKz5yW97qRpOqIAaCKzdrWmCIddowiPAiBvhHga93ELSGUUu-JhR1`
- ローカルコード: `commerce/ebay/tools/gas/asics_delete/`
- 編集後: `cd commerce/ebay/tools/gas/asics_delete/ && clasp push`

---

*最終更新: 2026-05-06午後（隔週メンテで親 CLAUDE.md から本ファイルに分離）*
