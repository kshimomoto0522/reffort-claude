# 仕入管理表 GASツール仕様（gas_shiire_tool.js）

> 親: `commerce/ebay/tools/CLAUDE.md` から「必要時ロード」として参照される詳細ファイル。
> GASツール改修・トリガー調整・重複バグ調査時に参照する。

---

## 概要

eBay Trading API（GetOrders）から新規オーダーを自動取得し、仕入管理表スプレッドシートに反映するGoogle Apps Scriptツール。

---

## ファイル・環境

| 項目 | 値 |
|------|-----|
| マスターファイル | `commerce/ebay/tools/gas_shiire_tool.js` |
| 本番Apps Script | `1EGuRaF3Hj1Uhayek4jCIgGQcxzKEJxLaqZmqfsgZbRph_RYUNZRgCNNf` |
| テストApps Script | `1s52yu6RVQ3kCPk0MIvR4Gst-bG_DcmXD3jFLjrFBfqNNbbAtb24hlusv` |
| 本番スプレッドシート | `1B1kFIiu8M5Pw8U8YuERK8ApKUa4S--GfIzBkW53kY3g` |
| テストスプレッドシート | `1vkhstYuPhgQJecDfSdMjL67mWsdthtkHJ6HjnXF-KAk` |
| トリガー | 毎朝9:45頃（nearMinute(45)）本番設定済み |
| APIキー | **Script Properties**に保存（EBAY_DEV_ID / APP_ID / CERT_ID / USER_TOKEN）＝コード直書き禁止 |

---

## 主な機能（2026-04-22 大改修後）

- eBay Trading API GetOrders で**過去2日**分のオーダーを取得（FETCH_DAYS_BACK=2）
- `OrderStatus=All` で取得（Cancelled/CancelPendingも含む → キャンセル検知漏れ防止）
- **前回処理時刻（LAST_PROCESSED_CREATED_TIME）以降のみ処理**（Refunded蘇り防止）
- OrderNo + 正規化SKU の組み合わせで重複排除（Z除去正規化で過去データと共存）
- 過去の仕入履歴から型番・仕入先・仕入値を自動参照
- タイトルから型番・**Width（New Balance）**を自動抽出
- キャンセル検知4系統（OrderStatus・CancelStatus・BuyerRequestedCancel・CancelReason）
- **多言語サイズラベル対応**（Schuhgröße / Pointure / Taglia 等 + US/JP/UK/EU値パターン検出）
- O列にタイトル（eBay商品ページハイパーリンク付き）
- E3に赤文字太字の処理中通知（スタッフ向け）
- LockService排他ロック（2重実行防止）
- **Z除去はしない**（シートにZ付きSKUを維持、有在庫判定は `hasStock` フラグで）
- 同一オーダー複数商品 → E列（送料）セル結合

---

## 重複バグ対策（3層防御）

- **対策A（根本）**: `normalizeSkuForCompare_` でシート側・API側の両方をZ除去正規化して比較
- **対策G（検出）**: 同一orderNumberが既存にあるのに新規判定された場合、実行ログに警告
- **対策H（事前検査）**: 🛡️ 重複安全チェックメニューで既存重複・Z混在を事前洗い出し

---

## 新設メニュー

- 🛡️ 重複安全チェック（本番反映前に推奨）
- 🔍 特定オーダーのXMLを確認（デバッグ用・特定オーダーIDで生XML取得）
- ⏮️ 前回処理時刻をリセット

---

## SKU Zフラグルール

- サイズ部分のZ = 有在庫（例: `V0126-8.5Z-30`）
- 親SKU先頭のZ ≠ 有在庫（例: `Z0196-11-23` は無在庫）
- 有在庫判定正規表現: `/-\d+\.?\d*Z(?:-|$)/`
- 重複比較時の正規化正規表現: `/(\d+\.?\d*)Z(?=-|$)/`（書き込み時は除去しない）

---

## 本番既存の重複4組（放置・社長指示で削除しない）

過去のZ除去バグによる重複。新コードでは発生しない。

- 行 7233/7597、7242/7363、7361/7776、7568/7792

---

## コード更新手順（2026-04-22 実証済み）

1. `gas_shiire_tool.js`をローカルで編集
2. PowerShellで `Get-Content gas_shiire_tool.js -Raw -Encoding UTF8 | Set-Clipboard`
3. Apps Scriptエディタを開いて `textarea.inputarea` にフォーカス
4. JS実行で `monaco.editor.getModels()[0].setValue('')` で空にする
5. Ctrl+V で貼り付け → **8秒以上wait**（Monaco大規模ペーストは遅い）
6. `monaco.editor.getModels()[0].getValue().length` で文字数・関数存在を検証
7. Ctrl+S で保存
