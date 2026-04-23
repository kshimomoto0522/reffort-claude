// 新規商品3モデル（SLIP-ON / MOAL 77 NM / SD VIN）の情報をスプレッドシートに挿入
// C列（型番/SKU）、D列（カラー名）、F列（性別）、H列（画像URL）を更新
// 加えてRow 101-103のG列URLを /mexico-66-sd/ → /mexico-66-sd-vin/ に修正
const { google } = require('googleapis');
const path = require('path');

const SPREADSHEET_ID = '1fI-hjq4FvSDsRVWvmb5Z8UWHOf9tBLTFCz7AliIW3ok';
const KEY_FILE = path.resolve('C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/commerce/ebay/analytics/reffort-sheets-fcbca5a4bbc2.json');

// Chrome-in-Chrome MCPでスクレイピング済みのデータ（全UNISEX）
const productData = [
  // Mexico 66 SLIP-ON (rows 86-93)
  { row: 86, code: '1183A360.205', color: 'BIRCH/MIDNIGHT',          gender: 'UNISEX' },
  { row: 87, code: '1183A360.121', color: 'WHITE/TRICOLOR',          gender: 'UNISEX' },
  { row: 88, code: '1183A360.401', color: 'NAVY/OFF-WHITE',          gender: 'UNISEX' },
  { row: 89, code: '1183A360.002', color: 'BLACK/BLACK',             gender: 'UNISEX' },
  { row: 90, code: '1183A360.131', color: 'OFF-WHITE/BEET JUICE',    gender: 'UNISEX' },
  { row: 91, code: '1183A360.132', color: 'WHITE/GINGER PEACH',      gender: 'UNISEX' },
  { row: 92, code: '1183A746.751', color: 'YELLOW/BLACK',            gender: 'UNISEX' },
  { row: 93, code: '1183C141.100', color: 'WHITE/WHITE',             gender: 'UNISEX' },
  // MOAL 77 NM (rows 94-95)
  { row: 94, code: '1183B761.201', color: 'PAPER BAG/WHITE',         gender: 'UNISEX' },
  { row: 95, code: '1183B761.301', color: 'BRONZE GREEN/WHITE',      gender: 'UNISEX' },
  // Mexico 66 SD VIN (rows 96-103)
  { row: 96,  code: '1183C015.200', color: 'BIRCH/METROPOLIS',           gender: 'UNISEX' },
  { row: 97,  code: '1183C015.101', color: 'CREAM/BIRCH',               gender: 'UNISEX' },
  { row: 98,  code: '1183C015.104', color: 'WHITE/DIRECTOIRE BLUE',     gender: 'UNISEX' },
  { row: 99,  code: '1183C015.201', color: 'BIRCH/GREEN',               gender: 'UNISEX' },
  { row: 100, code: '1183C015.202', color: 'BEIGE/BEET JUICE',          gender: 'UNISEX' },
  { row: 101, code: '1183C015.205', color: 'CLAY CANYON/CREAM',         gender: 'UNISEX' },
  { row: 102, code: '1183C015.106', color: 'OFF-WHITE/PURPLE SPECTRUM', gender: 'UNISEX' },
  { row: 103, code: '1183C015.400', color: 'PEACOAT/WHEAT YELLOW',      gender: 'UNISEX' },
];

// 既存行と同じ画像URLパターン（SB_FR_GLB = 1足正面画像）を使用
function getImageUrl(code) {
  const style = code.replace('.', '_');
  return `https://asics.scene7.com/is/image/asics/${style}_SB_FR_GLB?$otmag_zoom$&qlt=99,1`;
}

// Row 101-103のURL修正用（/mexico-66-sd/ → /mexico-66-sd-vin/）
const urlFixes = [
  { row: 101, url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66-sd-vin/1183C015_205.html' },
  { row: 102, url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66-sd-vin/1183C015_106.html' },
  { row: 103, url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66-sd-vin/1183C015_400.html' },
];

async function main() {
  const auth = new google.auth.GoogleAuth({
    keyFile: KEY_FILE,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  const sheets = google.sheets({ version: 'v4', auth });

  const updates = [];

  for (const item of productData) {
    updates.push({ range: `C${item.row}`, values: [[item.code]] });
    updates.push({ range: `D${item.row}`, values: [[item.color]] });
    updates.push({ range: `F${item.row}`, values: [[item.gender]] });
    updates.push({ range: `H${item.row}`, values: [[getImageUrl(item.code)]] });
  }

  // Row 101-103のURL修正
  for (const fix of urlFixes) {
    updates.push({ range: `G${fix.row}`, values: [[fix.url]] });
  }

  const result = await sheets.spreadsheets.values.batchUpdate({
    spreadsheetId: SPREADSHEET_ID,
    requestBody: {
      valueInputOption: 'RAW',
      data: updates,
    },
  });

  console.log(`更新完了: ${result.data.totalUpdatedCells} セルを更新しました`);
  console.log(`対象: 18商品 × 4列 + URL修正3件 = ${18 * 4 + 3}セル想定`);
}

main().catch(err => {
  console.error('エラー:', err.message);
  process.exit(1);
});
