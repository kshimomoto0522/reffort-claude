---
name: 仕入管理表GASツール
description: eBay GetOrders APIで仕入管理スプレッドシートに自動反映するGASツールの状況・バグ・ID情報
type: project
originSessionId: 62977e58-41af-44f8-95f2-db269e8e66be
---
## 仕入管理表 GASツール（gas_shiire_tool.js）

eBay Trading API（GetOrders）から新規オーダーを自動取得し、仕入管理表スプレッドシートに反映するGoogle Apps Scriptツール。

### 環境ID
- 本番Apps Script: `1EGuRaF3Hj1Uhayek4jCIgGQcxzKEJxLaqZmqfsgZbRph_RYUNZRgCNNf`
- テストApps Script: `1s52yu6RVQ3kCPk0MIvR4Gst-bG_DcmXD3jFLjrFBfqNNbbAtb24hlusv`
- 本番スプレッドシート: `1B1kFIiu8M5Pw8U8YuERK8ApKUa4S--GfIzBkW53kY3g`
- テストスプレッドシート: `1vkhstYuPhgQJecDfSdMjL67mWsdthtkHJ6HjnXF-KAk`
- トリガー: 毎朝9:45頃（本番設定済み）

### 現在のステータス（2026-04-22 夜 大改修完了）
- 本番稼働中、毎朝自動実行
- **4つの大きな修正を本番反映済み（1331行）**
- 明朝の自動実行で Width機能・有在庫SKU維持 の最終検証予定

### 今回の修正内容（2026-04-21〜22）

**1. eBayMag他国サイトのサイズ反映（Schuhgröße等）**
- `parseVariationSpecifics_` に多言語キーワード追加: schuhgröße / pointure / taille / taglia / numero / talla / maat
- 保険: 値が US\d / JP\d / EU\d / UK\d パターンを含めばサイズ判定
- 対象例: 18-14505-89239（独/US10/JP28）、23-14507-09287（Eigenschaften:Schwarz + US Schuhgröße (Herren):US9.5/UK9.5/JP28）

**2. New Balance Widthサイズ付与**
- `extractWidth_` 新設。タイトルから Width D/2E/4E/6E/B を抽出
- `buildRowData_` で size 末尾に全角スペース区切りで付加（例: `US10/JP28　D`）
- 有在庫時は `US10/JP28　D　※有在庫`

**3. キャンセル検知強化**
- `OrderStatus=Completed` → `OrderStatus=All` に変更（キャンセル処理中のオーダー取得漏れ解消）
- OrderStatus自体（Cancelled/CancelPending）によるキャンセル判定を追加
- トップレベル CancelReason もチェック

**4. Refunded蘇り防止 + 取得期間短縮**
- `FETCH_DAYS_BACK`: 7 → 2日（毎日実行 + 停止1日リカバリ）
- `LAST_PROCESSED_CREATED_TIME` プロパティで前回最大CreatedTimeを記録
- 次回実行時はその時刻以降のオーダーのみ処理（eBay Send refundで蘇り続ける問題を解消）

### 重複バグ対策（3層防御）
**対策A（根本解決）**: `normalizeSkuForCompare_` 新設。シート側・API側の両方でZ除去正規化してから比較
- → 過去のZ無しデータと現在のZ付きデータが混在していても正しく重複判定
**対策G（検出層）**: 同じorderNumberが既存にあるのに新規判定された場合、ログに重複疑惑警告
**対策H（事前検査）**: `checkDuplicatesSafety` メニュー。シート内の既存重複・Z混在を事前洗い出し

### Z除去ポリシー変更（最重要・運用方針）
- **Z除去はしない**（シートにZ付きSKUをそのまま保持）
- 社長が本番コードでZ除去行を手動削除済みだったため、マスターも追従
- 有在庫判定は `hasStock = /-\d+\.?\d*Z(?:-|$)/.test(sku)` でZ付きのまま判定
- 重複チェック時のみ `normalizeSkuForCompare_` でZ除去正規化して比較
- 書き込みはZ付きSKUのまま

### 新設メニュー
- 🛡️ 重複安全チェック（本番反映前に推奨）
- 🔍 特定オーダーのXMLを確認（デバッグ）
- ⏮️ 前回処理時刻をリセット

### 本番既存の重複4組（未削除・社長指示で放置）
過去のZ除去バグによる重複。新コードでは発生しない。削除しない。
- 行 7233/7597 (03-13912-85084|S04116-9.5-4)
- 行 7242/7363 (05-13913-63314|K02338-10.5-2)
- 行 7361/7776 (23-13924-74041|S04798-5.5)
- 行 7568/7792 (16-13990-06850|S05152-6.5-2)

### テスト環境での検証結果（2026-04-21）
- 📥新規オーダー反映: 7件（API 50件取得→43件は既存と一致で除外→7件新規）
- 重複疑惑: 0件
- 最大CreatedTime保存成功
- サイズ・SKU・タイトルリンクすべて正常反映

### 本番反映結果（2026-04-22夜）
- コード転送成功（1331行、全関数検出、シンタックスエラーなし）
- 手動実行で2件反映。ただし今回分は全て無在庫オーダー
- **Width機能・有在庫SKU維持の実機検証は明朝の自動実行待ち**

### 明朝の検証ポイント
1. Width付き商品（New Balance等）で `US10/JP28　D` 形式になっているか
2. 有在庫オーダー時にZ付きSKUが維持され `※有在庫` 付加されるか
3. 前回処理時刻以降のみ対象になっているか（実行ログで確認）
4. 重複疑惑が0件であること

### コード更新手順
1. `gas_shiire_tool.js`（ローカル）を編集
2. PowerShell `Get-Content | Set-Clipboard` でクリップボードにコピー
3. Apps Scriptエディタを開き textarea にフォーカス
4. `monaco.editor.getModels()[0].setValue('')` で空にする
5. Ctrl+V で貼り付け（waitを十分取る／Monacoは大きなペーストに時間がかかる）
6. Ctrl+S で保存
7. 検証: `monaco.editor.getModels()[0].getValue()` で文字数・関数存在確認

### 転送時のトラブルシュート
- Ctrl+Aで選択→Ctrl+Vが途中で切れる場合: setValue('')で空にしてからCtrl+V
- クリップボード汚染防止: 作業直前に必ずSet-Clipboardで再セット
- Monacoにペースト後、改行コードはCRLF変換されて文字数が+行数分増える（正常動作）

**Why:** スタッフが毎朝10時から仕入作業を開始するため、9:45に自動でオーダーデータが準備されている必要がある
**How to apply:** マスターファイルは `ebay-tools/gas_shiire_tool.js`。本番・テストともMonaco Editor経由で転送。gas_copy.html は補助的なバックアップ方式。
