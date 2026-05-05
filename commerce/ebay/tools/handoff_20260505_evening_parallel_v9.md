# 引継ぎ：ASICS v9 並列ワーカー実装中（PoC成功・本体改修完了・テスト未実施）

> **次セッション冒頭で必ず読むファイル**（2026-05-05 夜・社長帰宅で中断）
> ASICS v8 → v9（並列ワーカー対応）への改修途中。**コード改修は完了**しているが、**実機テストは未実施**。
> 次セッションは「テスト → exe再ビルド → 本番デプロイ」の流れ。

---

## 0. 直前の判断：スピード課題への対策

**課題**: ASICS v8 は1周40時間以上かかり遅すぎる。

**社長案・採用**: ローカル1ワーカー + AdsPower(Onitsuka) 1ワーカー の並列構成で半分の時間に短縮。

**選定の理由**:
- ローカルは既に240秒で安定稼働している実績を温存（worker1）
- AdsPowerは別IP・別指紋なので待機120秒でもBot検出されない（PoC実証済）
- DECODO日本住宅IPで国境越え警戒も回避
- 比率分割で「パイ（総件数）が変わっても両ワーカーが同時刻に終わる」設計

**期待スピード**: 605件で 40時間 → **15.9時間（2.5倍速）**

---

## 1. PoC 結果（2026-05-05 夜実施・成功）

### 1.1 環境疎通確認 ✅
- AdsPower Local API（v6+ Bearer 認証）疎通OK
- プロファイル「Onitsuka」（user_id=`k1c60dgp`）のChrome に Selenium debuggerAddress 経由で接続成功
- 外向きIP: `124.210.45.52`（DECODO 日本住宅IP・期待通り）

### 1.2 ASICS 5件連続取得テスト（120秒待機） ✅
- スプレッドシート行3〜7（METASPEED系・NETBURNER系）のURL使用
- **Bot検出ゼロ** / サイズ要素・在庫数値もすべて正しくパース可能
- 取得時間平均: **31秒/件**
- 1件のみ DECODO瞬断（`ERR_TUNNEL_CONNECTION_FAILED`） → 短時間リトライで救済可能

### 1.3 比率分割の検証 ✅

| パイ（総件数） | worker1（240+14秒） | worker2（120+31秒） | 全体所要 |
|---|---|---|---|
| 500件 | 186件 (13.1h) | 314件 (13.2h) | 13.2時間 |
| **605件** | **226件 (15.9h)** | **379件 (15.9h)** | **15.9時間** |
| 700件 | 261件 (18.4h) | 439件 (18.4h) | 18.4時間 |

両ワーカーがほぼ同時刻に終わる（差0.1時間以内）。

---

## 2. 完了した実装

### 2.1 新規ファイル（`asics_master_work/`）

| ファイル | 役割 | 状態 |
|---|---|---|
| `worker_split.py` | 比率分割ロジック・WORKER_CONFIG | 単体テスト通過 |
| `adspower_driver.py` | AdsPower Local API + Selenium接続 + safe_get（DECODO瞬断対策） | 単体テスト通過 |
| `poc_adspower.py` | PoC: 1件取得テスト | PoC使用済 |
| `poc_5items.py` | PoC: 5件連続テスト | PoC使用済 |
| `poc_get_test_url.py` | スプレッドシートからURL取得 | ヘルパー |
| `run_parallel.bat` | 2ワーカー並列起動ランチャー | 未実行 |

### 2.2 `scrape_data.py` 改修内容（v8 → v9）

バックアップ: `scrape_data.py.bak_v8_pre_parallel_*` で復元可能。

| 改修箇所 | 内容 |
|---|---|
| 冒頭 | `argparse` import / `worker_split` `adspower_driver` の try-import / `WORKER_ID=1` `NUM_WORKERS=1` グローバル変数 |
| `_resume_file()` 新規 | NUM_WORKERS>1 時は `resume_state_w{N}.json` ・単独モード時は従来の `resume_state.json` で互換 |
| `save_resume / load_resume / clear_resume` | `_resume_file()` 経由に変更 |
| `init_driver(worker_id, firefox_service)` 新規 | worker1=Firefox+画面外配置・worker2=AdsPower Chrome を返す |
| `close_driver(driver, worker_id)` 新規 | worker1=Firefoxクローズ・worker2=セッション切断のみ（ブラウザは閉じない） |
| `get_worker_wait_seconds(worker_id)` 新規 | WORKER_CONFIG から待機秒数取得 |
| `SpreadsheetClass.write_status` | NUM_WORKERS>1 かつ WORKER_ID!=1 ならno-op（worker1のみマスター書き込み） |
| `run_one_lap()` | ▼ ワーカー固有の待機秒数を override<br>▼ worker1のみが60秒カウントダウン・compact 実行<br>▼ worker2は30秒待機（worker1のcompact完了待ち）<br>▼ 担当範囲を `get_my_range()` で動的計算<br>▼ メインパスの range を `range(resume_idx, end_idx)` に<br>▼ リトライパスのターゲットを担当範囲フィルタ<br>▼ check_pending_delete・process_delete_queue は worker1限定<br>▼ driver初期化を `init_driver()` 経由<br>▼ driver終了を `close_driver()` 経由<br>▼ 完走後 `worker_done_w{N}.txt` 作成 |
| エントリポイント | `argparse` で `--worker` `--total-workers` 受け取り |

### 2.3 検証済み
- ✅ syntax チェック（`ast.parse`）
- ✅ import チェック（`import scrape_data` でモジュール読み込み + デフォルト値確認）
- ✅ PARALLEL_AVAILABLE = True（worker_split / adspower_driver が同フォルダから読める）
- ❌ **実機テスト未実施**

---

## 3. 残作業（次セッション）

### 3.1 必須① 単独モード互換確認（10分）
**前提**: 既存 v8 互換であることを確認 → 仮に並列がうまく動かなくても本番が壊れないことを保証

```bash
cd C:\Users\KEISUKE SHIMOMOTO\Desktop\asics_master_work
.venv\Scripts\python.exe scrape_data.py
```
- 引数なし = `WORKER_ID=1, NUM_WORKERS=1` (デフォルト)
- 60秒カウントダウン → compact → 通常処理が始まればOK
- 1〜2件処理させて Ctrl+C で停止 → 異常なし確認

### 3.2 必須② worker2 単独動作確認（30分）
**前提**: AdsPower(Onitsuka) を起動した状態で実行

```bash
.venv\Scripts\python.exe scrape_data.py --worker 2 --total-workers 2
```
- AdsPower Chrome を Selenium で掴むことを確認
- 担当範囲（後半 379件）から処理が始まることを確認
- 1〜2件処理させて停止 → 動作OKなら次へ

### 3.3 必須③ 2ワーカー並列テスト（30分）
```bash
run_parallel.bat
```
- 別ウィンドウで2プロセスが立ち上がる
- worker1 の compact 完了 → worker2 も処理開始
- 各々が担当範囲のデータを書き込む（A1 ステータスは worker1 のみ更新）

### 3.4 推奨④ DECODO 瞬断リトライの追加実装（1時間）
**現状**: `process_one_item` 内の `driver.get(link)` は v8 のまま。
**追加実装**:
- WORKER_ID >= 2 の時は `adspower_driver.safe_get()` を使うように分岐
- 改修箇所: `process_one_item` 内の `driver.get(link)` 周辺（行1094付近・1105付近）

または、`process_one_item` の冒頭で driver にmonkey-patch して driver.get を上書き。

### 3.5 必須⑤ exe 再ビルド（30分）
PyInstaller spec の `hiddenimports` に追加:
```python
hiddenimports = [..., 'worker_split', 'adspower_driver']
```
または collect_submodules を使用。

```bash
.venv\Scripts\python.exe -m PyInstaller scrape_data.spec
# → dist/scrape_data.exe が生成される
```

### 3.6 必須⑥ 本番デプロイ（10分）
- 現本番 exe バックアップ: `scrape_data.exe.bak_v8_complete_*`（自動で残る）
- 新 exe コピー: `dist/scrape_data.exe` → `eBay在庫調整ツール（アシックス）\scrape_data.exe`
- worker_split.py / adspower_driver.py も exe 化済なら不要・別ファイルなら本番フォルダにコピー

### 3.7 推奨⑦ Windowsタスク登録（30分）
- 旧 ASICS_v2_*ji タスクは無効化
- 新規 `ASICS_v9_parallel_start` タスクを作成（PC起動時 or 毎日決まった時刻）
- VBS hidden ラッパーで cmd 窓を出さない（CLAUDE.md ルール準拠）

### 3.8 必須⑧ .env 移行（15分）
現在ハードコード:
```
ADSPOWER_API_KEY = 239f4b0eebbc395c1b9e7ccb3bed4ba2008c87845ca7ca0e
ADSPOWER_USER_ID_W2 = k1c60dgp
DECODO Proxy: spp5y3m50d / uj4+jNadmqbP97rRN7（AdsPower側で管理・コード関与なし）
```

→ `eBay在庫調整ツール（アシックス）\.env` に移動・python-dotenv で読み込み。

---

## 4. 重要な技術メモ

### 4.1 単独モード互換性
`NUM_WORKERS=1` の時は **すべての並列分岐がスキップ** されるので、既存 v8 と完全互換。万一並列がうまく動かなくても、`python scrape_data.py`（引数なし）で v8 同等の挙動。

### 4.2 worker2 が触れないもの
| 項目 | 担当 | 理由 |
|---|---|---|
| A1 ステータス書き込み | worker1のみ | 競合回避（write_status で自動 no-op） |
| compact_blank_rows | worker1のみ | 行構造を変えるのでworker2が走ってる時にやると競合 |
| Z1 ポーリング・出品削除キュー | worker1のみ | 重複実行防止 |
| 自分の担当範囲外の行への書き込み | 厳禁 | 比率分割で領域分離されている |

### 4.3 比率の更新方法
`worker_split.py` の `WORKER_CONFIG` を編集:
```python
WORKER_CONFIG = {
    1: {'wait_seconds': 240, 'avg_fetch_seconds': 14},  # 実測で更新
    2: {'wait_seconds': 120, 'avg_fetch_seconds': 31, 'adspower_user_id': 'k1c60dgp'},
}
```
取得時間の平均が変わったら `avg_fetch_seconds` を更新するだけで動的に再計算される。

### 4.4 DECODO 瞬断対策
住宅プロキシは性質上たまに `ERR_TUNNEL_CONNECTION_FAILED` で切断される（PoCで5件中1件）。
- 現状: process_one_item 内では `driver.get` がそのまま → 失敗時はエラー情報書き込み・リトライパス（フェーズ2）で救済
- 追加実装: `adspower_driver.safe_get` で 3回リトライ（8秒間隔）→ 即時救済

### 4.5 AdsPower 起動の前提
- AdsPower クライアントが起動していること
- プロファイル「Onitsuka」（user_id=k1c60dgp）が存在すること
- DECODO プロキシ（jp.decodo.com:30001）が紐付いていること
- Local API が「ON」になっていること

---

## 5. 機密情報（要 .env 移行）

PoC段階で会話・コードに出ている情報:

| 項目 | 値 |
|---|---|
| AdsPower API Key | `239f4b0eebbc395c1b9e7ccb3bed4ba2008c87845ca7ca0e` |
| AdsPower user_id (Onitsuka) | `k1c60dgp` |
| DECODO 日本住宅IP（実測） | 117.109.55.32 / 124.210.45.52 |
| DECODO プロキシ認証 | spp5y3m50d / uj4+jNadmqbP97rRN7 |

→ 次セッションで `.env` 化し、`adspower_driver.py` の hardcode を削除する。

---

## 6. 次セッションの最初のタスクリスト（順番）

```
1. このファイルを読む
2. asics_master_work/scrape_data.py を python scrape_data.py で起動 → 単独モード互換確認
3. AdsPower(Onitsuka) 起動を社長に依頼
4. python scrape_data.py --worker 2 --total-workers 2 で worker2 単体テスト
5. 問題なければ run_parallel.bat 実行 → 10件規模テスト
6. process_one_item の driver.get → safe_get 化（DECODO瞬断対策）
7. PyInstaller spec 更新 → exe 再ビルド
8. 本番デプロイ
9. .env 化（API Key・user_id）
10. memory更新・development-history追記
```

---

## 7. 関連ファイル一覧

| パス | 役割 |
|---|---|
| `asics_master_work/scrape_data.py` | v9 改修済（実機テスト未） |
| `asics_master_work/scrape_data.py.bak_v8_pre_parallel_*` | v8 バックアップ（差し戻し用） |
| `asics_master_work/scrape_data.py.fixed_v8_*` | v8 ソース（旧バージョン） |
| `asics_master_work/worker_split.py` | 比率分割ロジック（新規） |
| `asics_master_work/adspower_driver.py` | AdsPower 起動モジュール（新規） |
| `asics_master_work/run_parallel.bat` | 並列起動ランチャー（新規） |
| `asics_master_work/poc_adspower.py` | PoC 1件 |
| `asics_master_work/poc_5items.py` | PoC 5件連続 |
| `asics_master_work/poc_get_test_url.py` | スプレッドシートURL取得 |
| `asics_master_work/scrape_data.spec` | PyInstaller spec（要更新） |
| `eBay在庫調整ツール（アシックス）\scrape_data.exe` | **本番 exe（v8 のまま・未更新）** |
| `commerce/ebay/tools/handoff_20260505_asics_v8_complete.md` | 前セッションの引継ぎ（v8完成時点） |

---

*作成: 2026-05-05 夜（社長帰宅前）*
*次セッション冒頭でこのファイルを最初に読む*
