# ダイレクト販売ツール - Claude Code 作業ルール

> Node.js + Express製のWebアプリ。バイヤー向け注文・セラー向け管理を一体化。
> 本番URL: https://reffort-direct-sales.onrender.com
> リポジトリ: https://github.com/kshimomoto0522/reffort-direct-sales (Private)

---

## 📦 新商品（新モデル／新バリアント）追加の標準手順

**いつ使うか**: 社長から「新しい商品を追加して」「メニューに追加して」と依頼された時。
この手順を**必ず順番通り**に実行する。途中を飛ばさない。

### STEP 0: 事前確認
- 社長から**商品情報（モデル名・並び順の希望）**を受け取る
- スプレッドシートを社長が更新済みか確認（B列モデル名、E列仕入値、G列商品URL、I列販売価格は社長入力済が多い）
- スプレッドシートID: `1fI-hjq4FvSDsRVWvmb5Z8UWHOf9tBLTFCz7AliIW3ok`
- サービスアカウント: `C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/commerce/ebay/analytics/reffort-sheets-fcbca5a4bbc2.json`

### STEP 1: スプレッドシートの現状確認
`check-sheet.js` または `check-sheet-wide.js` で対象行の入力状況を確認。
列構造:
| 列 | 内容 | 入力担当 |
|----|------|----------|
| B | モデル名 | 社長 |
| C | 型番（SKU） | **Claude** |
| D | カラー名 | **Claude** |
| E | 仕入値（JPY） | 社長 |
| F | 性別 (UNISEX/MEN/WOMEN) | **Claude** |
| G | 商品URL（onitsukatiger.com） | 社長 |
| H | 商品画像URL（asics.scene7.com） | **Claude** |
| I | 販売価格（USD） | 社長 |

### STEP 2: カラー名・性別をスクレイピング
Onitsuka Tiger公式サイトは**JS-rendered SPA**。curl/WebFetchでは色情報が取れない。
**必ず Chrome-in-Chrome MCP** を使う：
1. `mcp__Claude_in_Chrome__navigate` で商品URLへ
2. `mcp__Claude_in_Chrome__get_page_text` でレンダリング後のテキスト取得
3. 正規表現で抽出: `/￥[\d,]+税込み\s*\n(UNISEX|MEN|WOMEN)\s*\nカラー/`
   - ⚠️ グローバルナビに "MEN" が含まれるので単純 `(MEN|WOMEN|UNISEX)` は誤マッチする
4. カラー名は「カラー」の後の行から抽出

### STEP 3: スプレッドシート C/D/F/H 列を埋める
`fill-sheet-new-models.js` のパターンで Google Sheets API 経由で更新。
画像URLは既存パターンに合わせて **`SB_FR_GLB`**（1足正面画像）を使用：
```
https://asics.scene7.com/is/image/asics/{style}_SB_FR_GLB?$otmag_zoom$&qlt=99,1
```
※ 旧 `fill-sheet.js` は `SB_TP_GLB`（2足並び）だが、既存データは `SB_FR_GLB`。統一する。

### STEP 4: G列URLパスの誤りを確認
社長が手入力したG列URLは、モデル名とパスが一致しないことがある（例: SD VIN なのに `/mexico-66-sd/`）。
実際のリダイレクト先（`/mexico-66-sd-vin/` など）に修正する。

### STEP 5: products.json に登録（=商品登録）
`register-new-models.js` パターンでproducts.jsonへ追記：
- **販売価格(price)**: スプレッドシートI列の**社長入力値**を必ず反映（勝手に推測しない）
- **仕入値(purchasePrice)**: スプレッドシートE列の値
- **displayOrder**: 既存モデルの最大displayOrder + 1 から採番
- **sizeType**: `unisex` / `womens` / `mens`
- **image**: `SB_FR_GLB` パターン
- **supplierUrl**: スプレッドシートG列の値

⚠️ **販売価格は必ずスプレッドシートI列を確認してから登録**。社長が既に入れているケースが多い。

### STEP 6: app.js の MODEL_PRIORITY_LIST を更新（メニュー順変更時のみ）
社長から並び順の指定があれば、`public/app.js` 冒頭の `MODEL_PRIORITY_LIST` を更新：
```js
const MODEL_PRIORITY_LIST = [
  'MEXICO 66',
  'MEXICO 66 SD',
  'MEXICO 66 SD VIN',
  'MEXICO 66 SLIP-ON',
  'MEXICO 66 TGRS'
];
```
このリストにない商品は「その他」扱い（displayOrder順）。

### STEP 7: ローカル確認
1. `node server.js` もしくは preview_start でローカル起動
2. バイヤーのPlace an order画面で：
   - 新モデルがメニューに出ているか
   - 並び順が社長指定通りか
   - 画像・カラー・価格が正しく表示されるか
   - SKU検索で新商品がヒットするか
3. 社長に **スクリーンショット付きで確認依頼**

### STEP 8: 社長OK後、本番へpush（コード + 商品データ両方必要）
- **営業時間中のpush禁止**（バイヤー利用中の事故防止）

**⚠️ 最重要：本番のdata/products.jsonは永続ディスクにマウントされているため、git pushでは商品データは反映されない！**

#### 8-1. コード変更のpush（app.js / index.html / style.css / CLAUDE.md）
```
git subtree push --prefix=direct-sales render-ds master
```
→ Render自動デプロイ完了を確認（通常1-2分）

#### 8-2. 商品データを本番APIへ登録（products.jsonの変更）
`register-to-prod.js` を実行して本番APIに新商品をPOST：
```
node register-to-prod.js
```
→ 本番の `/api/products` に直接POSTして新モデルを追加する
→ 既存モデルは重複登録しないようフィルタ済み

#### 8-3. 本番反映確認
```
curl -s https://reffort-direct-sales.onrender.com/api/products | jq '.[].model'
```
社長に本番URL動作確認を依頼

---

## 🔒 重要ルール（必ず守ること）

- **販売価格は勝手に推測しない**。必ずスプレッドシートI列の社長入力値を反映する。
  入っていない場合は社長に確認する。
- **営業時間中の本番push禁止**
- **⚠️ 永続ディスク仕様**: 本番の`data/`は永続ディスクマウントのため、git pushでは商品データは反映されない。
  商品追加時は必ず `register-to-prod.js` で本番APIに直接POSTすること。
- **データ形式**: purchases は `{sku, size, quantity, sizeType}` フラット形式。マップ形式 `{sizes:{...}}` 禁止
- **bashのcurlで日本語POST → 文字化け**。必ずNode.jsスクリプト経由でUTF-8安全に送信
- **calcRemaining でprice等のメタ情報が消える**。差引後に必ずprice補完処理を入れる
- **未指示計算はadd方式**: `assigned = purchased + pending_instructed`。max方式は使わない
- **SKU統一表示順**: productsマスタ基準で全セクション固定（sortItemsBySkuOrder）

---

## 🛠️ 使用スクリプト一覧

| ファイル | 用途 |
|----------|------|
| `check-sheet.js` | A-H列の現状確認（行80-110） |
| `check-sheet-wide.js` | A-Z列の全列確認（販売価格I列含む） |
| `fill-sheet.js` | 旧：初期登録用（MEXICO 66基本27バリアント） |
| `fill-sheet-new-models.js` | 新規モデル追加用テンプレート |
| `register-products.js` | 旧：MEXICO 66を一括登録 |
| `register-new-models.js` | 新規モデル追加用テンプレート（販売価格はI列から反映）|
| `register-to-prod.js` | **本番APIに新規モデルを直接POST登録**（git pushでは反映されない商品データの本番反映） |
| `verify-and-fix-images.js` | 画像URL検証・SB_FR_GLB→SR_FR_GLBフォールバック |
| `sync-from-prod.js` | 本番→ローカルのデータ一方通行コピー |

---

## 📂 データファイル

| ファイル | 内容 |
|----------|------|
| products.json | 商品マスタ（モデル＋バリアント配列） |
| orders.json | 注文データ |
| purchases.json | 仕入記録（フラット形式） |
| purchaseInstructions.json | 仕入指示 |
| settings.json | 拠点設定 + sectionPasswords |
| shipments.json | 出荷データ（paid: true/false） |
| coupons.json | クーポン管理 |
| deliveries.json | 納品済データ |

---

*最終更新: 2026-04-16*
