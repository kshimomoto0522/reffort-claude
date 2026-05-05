---
name: ASICS v9 並列ワーカー化プロジェクト
description: AdsPower(Onitsuka)+DECODO日本住宅IPでローカルと並列稼働させ40h→16h短縮するプロジェクト
type: project
originSessionId: 71635640-2b4c-45d4-902d-138036ff99a1
---
# ASICS v9 並列ワーカー化（実装中・2026-05-05夜時点）

## 採用構成

```
worker1 = ローカルFirefox  ・240秒待機 ・自宅IP        ・226件担当（605時）
worker2 = AdsPower Chrome ・120秒待機 ・DECODO日本住宅IP ・379件担当（605時）
全体 15.9時間（40h→16h ＝ 2.5倍速）
```

**Why**: ASICS v8 の240秒待機は単独運用では妥当（Akamai対策）だが、別IP・別指紋なら120秒で済む。
ローカル既存実績を温存しつつ、worker2を追加することで実質倍速化。

**How to apply**: 比率分割で「パイ（総件数）が変わっても両ワーカーが同時刻に終わる」設計。
n1:n2 = (1/t1):(1/t2)。WORKER_CONFIG の avg_fetch_seconds を実測で更新可能。

## PoC実証結果（2026-05-05夜）

- AdsPower Local API（v6+ Bearer認証）疎通OK
- DECODO 日本住宅IP（117.109.55.32 / 124.210.45.52）動作確認
- ASICS 5件連続取得（120秒待機）→ Bot検出ゼロ
- 1件のみDECODO瞬断（住宅プロキシは性質上たまに切断）
- 取得時間平均: 31秒/件

## 環境

| 項目 | 値 |
|---|---|
| AdsPower プロファイル名 | Onitsuka |
| AdsPower user_id | k1c60dgp |
| AdsPower API Key | （adspower_driver.py にハードコード・要 .env 移行） |
| DECODO プロキシ | jp.decodo.com:30001（住宅・日本） |
| DECODO 認証 | spp5y3m50d / uj4+jNadmqbP97rRN7 |

## ファイル

- `asics_master_work/scrape_data.py` v9改修済（要テスト）
- `asics_master_work/worker_split.py` 比率分割（再利用可能）
- `asics_master_work/adspower_driver.py` AdsPower起動 + safe_get
- `asics_master_work/run_parallel.bat` 並列起動ランチャー
- `commerce/ebay/tools/handoff_20260505_evening_parallel_v9.md` 詳細引継ぎ

## 次のステップ

1. 単独モード互換テスト
2. worker2 単体テスト
3. 2並列テスト（10件規模）
4. process_one_item の driver.get → safe_get 化
5. exe 再ビルド
6. 本番デプロイ
7. .env 移行
