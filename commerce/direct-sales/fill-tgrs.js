// MEXICO 66 TGRS 16商品のスプレッドシート入力スクリプト
// C列（SKU）、D列（カラー名）、H列（画像URL）を埋める
const { google } = require('googleapis');
const path = require('path');

const SPREADSHEET_ID = '1fI-hjq4FvSDsRVWvmb5Z8UWHOf9tBLTFCz7AliIW3ok';
const KEY_FILE = path.resolve('C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/commerce/ebay/analytics/reffort-sheets-fcbca5a4bbc2.json');

// TGRS 16商品データ（公式サイトで確認済み）
const tgrsData = [
  { row: 70, code: '1182A660.752', name: 'IVORY/CREAM' },
  { row: 71, code: '1182A660.001', name: 'BLACK/BLACK' },
  { row: 72, code: '1182A660.020', name: 'SILVER/CREAM' },
  { row: 73, code: '1182A678.700', name: 'CRYSTAL PINK/GRAPHITE GREY' },
  { row: 74, code: '1182A678.001', name: 'BLACK/CREAM' },
  { row: 75, code: '1182A678.200', name: 'BIRCH/PEACOAT' },
  { row: 76, code: '1182A678.750', name: 'YELLOW/BLACK' },
  { row: 77, code: '1182A708.700', name: 'CLASSIC RED/CREAM' },
  { row: 78, code: '1182A708.020', name: 'GUNMETAL/METROPOLIS' },
  { row: 79, code: '1182A708.250', name: 'CHAMPAGNE/CREAM' },
  { row: 80, code: '1182A708.701', name: 'CRYSTAL PINK/CREAM' },
  { row: 81, code: '1182A705.250', name: 'BEIGE/BEIGE' },
  { row: 82, code: '1182A705.001', name: 'BLACK/BLACK' },
  { row: 83, code: '1182A705.020', name: 'OYSTER GREY/OYSTER GREY' },
  { row: 84, code: '1182A677.700', name: 'PINK CAMEO/COTTON CANDY' },
  { row: 85, code: '1182A677.001', name: 'BLACK/GUNMETAL' },
];

// 画像URL生成（SB_FR_GLB = 2足並んだフロント画像、全16個 HTTP 200確認済み）
function getImageUrl(code) {
  const style = code.replace('.', '_');
  return `https://asics.scene7.com/is/image/asics/${style}_SB_FR_GLB?$otmag_zoom$&qlt=99,1`;
}

async function main() {
  const auth = new google.auth.GoogleAuth({
    keyFile: KEY_FILE,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  const sheets = google.sheets({ version: 'v4', auth });

  // バッチ更新データを作成（C列=SKU、D列=カラー名、H列=画像URL）
  const updates = [];
  for (const item of tgrsData) {
    updates.push({ range: `C${item.row}`, values: [[item.code]] });
    updates.push({ range: `D${item.row}`, values: [[item.name]] });
    updates.push({ range: `H${item.row}`, values: [[getImageUrl(item.code)]] });
  }

  // 一括更新（API制限回避のためbatchUpdate使用）
  const result = await sheets.spreadsheets.values.batchUpdate({
    spreadsheetId: SPREADSHEET_ID,
    requestBody: {
      valueInputOption: 'RAW',
      data: updates,
    },
  });

  console.log(`✅ スプレッドシート更新完了: ${result.data.totalUpdatedCells} セルを更新`);
}

main().catch(err => {
  console.error('❌ エラー:', err.message);
  process.exit(1);
});
