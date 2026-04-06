// 画像URLをSB_TP_GLB → SB_FR_GLB（2足斜め並び）に差し替えるスクリプト
const { google } = require('googleapis');
const path = require('path');
const fs = require('fs');

const SPREADSHEET_ID = '1fI-hjq4FvSDsRVWvmb5Z8UWHOf9tBLTFCz7AliIW3ok';
const KEY_FILE = path.resolve('C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/ebay-analytics/reffort-sheets-fcbca5a4bbc2.json');
const PRODUCTS_FILE = path.join(__dirname, 'data', 'products.json');

// 全スタイルコード（Row 4〜30）
const allCodes = [
  { row: 4,  code: '1183C102_002' },
  { row: 5,  code: '1183C102_100' },
  { row: 6,  code: '1183C102_201' },
  { row: 7,  code: '1183C102_200' },
  { row: 8,  code: '1183C102_751' },
  { row: 9,  code: '1183C102_001' },
  { row: 10, code: '1183C102_250' },
  { row: 11, code: '1183C102_104' },
  { row: 12, code: '1183C102_752' },
  { row: 13, code: '1183C102_204' },
  { row: 14, code: '1183C102_203' },
  { row: 15, code: '1183C102_701' },
  { row: 16, code: '1183C102_105' },
  { row: 17, code: '1183C102_600' },
  { row: 18, code: '1183C102_005' },
  { row: 19, code: '1183B566_700' },
  { row: 20, code: '1183B566_020' },
  { row: 21, code: '1183B566_200' },
  { row: 22, code: '1183B566_021' },
  { row: 23, code: '1183B566_201' },
  { row: 24, code: '1183B566_022' },
  { row: 25, code: '1183A201_254' },
  { row: 26, code: '1183A201_304' },
  { row: 27, code: '1183A201_003' },
  { row: 28, code: '1183A201_305' },
  { row: 29, code: '1183A201_126' },
  { row: 30, code: '1183A201_127' },
  { row: 31, code: '1183B511_100' },
];

function getImageUrl(styleCode) {
  return `https://asics.scene7.com/is/image/asics/${styleCode}_SB_FR_GLB?$otmag_zoom$&qlt=99,1`;
}

async function main() {
  // 1. スプレッドシート更新
  console.log('--- スプレッドシート更新 ---');
  const auth = new google.auth.GoogleAuth({
    keyFile: KEY_FILE,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  const sheets = google.sheets({ version: 'v4', auth });

  const updates = allCodes.map(item => ({
    range: `H${item.row}`,
    values: [[getImageUrl(item.code)]],
  }));

  const result = await sheets.spreadsheets.values.batchUpdate({
    spreadsheetId: SPREADSHEET_ID,
    requestBody: {
      valueInputOption: 'RAW',
      data: updates,
    },
  });
  console.log(`スプレッドシート: ${result.data.totalUpdatedCells}セル更新`);

  // 2. products.json更新
  console.log('--- products.json更新 ---');
  const products = JSON.parse(fs.readFileSync(PRODUCTS_FILE, 'utf-8'));
  const mexico = products.find(p => p.model === 'MEXICO 66');
  if (mexico) {
    let updated = 0;
    mexico.variants.forEach(v => {
      if (v.image && v.image.includes('SB_TP_GLB')) {
        v.image = v.image.replace('SB_TP_GLB', 'SB_FR_GLB');
        updated++;
      }
    });
    fs.writeFileSync(PRODUCTS_FILE, JSON.stringify(products, null, 2), 'utf-8');
    console.log(`products.json: ${updated}バリアントの画像URL更新`);
  } else {
    console.log('MEXICO 66が見つかりません');
  }

  console.log('完了！');
}

main().catch(err => {
  console.error('エラー:', err.message);
  process.exit(1);
});
