/**
 * 【ASICS】在庫管理シート 出品削除予約 GAS
 * 2026-05-05 v1
 *
 * 動作:
 *  1. スプレッドシート上部メニュー「ASICS出品管理 → ✅ チェック商品を削除予約」を押す
 *  2. 確認ダイアログ → OK
 *  3. A1セルに「出品削除予約済み（X件・次の処理タイミングで実行）」を表示
 *  4. Z1セル（隠しキューマーカー）に "PENDING" を書き込む
 *  5. ASICSツール（Pythonスクリプト）が次のアイテム処理直前 or 休憩中に Z1 を検知
 *     → eBay EndItem API を呼んで実際の削除を実行
 *
 * 注意:
 *  - GAS は eBay API を呼ばない（軽量・即時完了）
 *  - 実際の削除は Python ツール側で行う（API認証は config.xlsx 管理）
 */

const SHEET_NAME = '【ASICS】在庫管理';
const QUEUE_CELL = 'Z1';      // 隠しキューマーカー（PENDING / 空）
const STATUS_CELL = 'A1';     // ステータス表示
const Q_COL_INDEX = 17;       // Q列 = 17列目（1-indexed）
const HEADER_ROW = 2;         // ヘッダーは行2
const DATA_START_ROW = 3;     // データは行3以降

/**
 * シートを開いた時にカスタムメニューを追加
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('ASICS出品管理')
    .addItem('✅ チェック商品を削除予約', 'reserveDelete')
    .addSeparator()
    .addItem('ℹ️ 使い方', 'showHelp')
    .addToUi();
}

/**
 * Q列がチェック済みの商品を削除予約する
 */
function reserveDelete() {
  const ui = SpreadsheetApp.getUi();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    ui.alert(`シート「${SHEET_NAME}」が見つかりません。`);
    return;
  }

  // データ範囲のQ列を取得
  const lastRow = sheet.getLastRow();
  if (lastRow < DATA_START_ROW) {
    ui.alert('データがありません。');
    return;
  }
  const range = sheet.getRange(DATA_START_ROW, Q_COL_INDEX, lastRow - HEADER_ROW, 1);
  const values = range.getValues();

  // チェック済み行を数える
  let checkedCount = 0;
  let checkedSkus = [];
  for (let i = 0; i < values.length; i++) {
    if (values[i][0] === true) {
      checkedCount++;
      // SKU列も取得（B列・index 2）
      const skuCell = sheet.getRange(DATA_START_ROW + i, 2).getValue();
      if (skuCell) checkedSkus.push(String(skuCell));
    }
  }

  if (checkedCount === 0) {
    ui.alert('チェック済みの商品がありません。\n削除したい商品の Q列「出品削除」にチェックを入れてください。');
    return;
  }

  // 確認ダイアログ
  const skuPreview = checkedSkus.slice(0, 5).join(', ') +
                     (checkedSkus.length > 5 ? ` ...他${checkedSkus.length - 5}件` : '');
  const confirmMsg =
    `${checkedCount}件の商品を削除予約します。\n\n` +
    `対象SKU: ${skuPreview}\n\n` +
    `※実際の削除はASICSツールが次のアイテム処理直前 or 休憩時に実行します。\n` +
    `（最大4分以内に削除開始される見込み）\n\n` +
    `予約してよろしいですか？`;

  const result = ui.alert('削除予約の確認', confirmMsg, ui.ButtonSet.YES_NO);
  if (result !== ui.Button.YES) {
    return;
  }

  // A1 にメッセージ表示
  const now = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'HH:mm:ss');
  const statusMsg = `出品削除予約済み（${checkedCount}件・次の処理タイミングで実行）| 予約: ${now}`;
  sheet.getRange(STATUS_CELL).setValue(statusMsg);

  // Z1 にキューマーカー
  sheet.getRange(QUEUE_CELL).setValue('PENDING');

  ui.alert(
    '予約完了',
    `${checkedCount}件の削除を予約しました。\n\n` +
    `A1セルに進捗が表示されます。\n` +
    `削除実行は最大4分以内に開始されます。`,
    ui.ButtonSet.OK
  );
}

/**
 * 使い方ダイアログ
 */
function showHelp() {
  SpreadsheetApp.getUi().alert(
    '使い方',
    '1. 削除したい商品のQ列「出品削除」にチェックを入れる\n' +
    '2. 上部メニュー「ASICS出品管理 → ✅ チェック商品を削除予約」をクリック\n' +
    '3. 確認ダイアログ → OK\n' +
    '4. ASICSツール（Pythonスクリプト）が自動で削除を実行（最大4分以内）\n\n' +
    '【削除結果】\n' +
    ' 成功: 該当行の全セル内容がクリアされる\n' +
    ' Policy違反: エラー情報列に「Policy違反の為要手動削除」と表示される\n' +
    ' その他失敗: エラー情報列にエラー詳細が表示される\n\n' +
    '【注意】\n' +
    ' ASICSツールが停止中の場合、次回起動時の最初の処理で実行されます。',
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}
