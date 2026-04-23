// スプレッドシートのフル列を確認
const { google } = require('googleapis');
const path = require('path');

const SPREADSHEET_ID = '1fI-hjq4FvSDsRVWvmb5Z8UWHOf9tBLTFCz7AliIW3ok';
const KEY_FILE = path.resolve('C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/commerce/ebay/analytics/reffort-sheets-fcbca5a4bbc2.json');

async function main() {
  const auth = new google.auth.GoogleAuth({
    keyFile: KEY_FILE,
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });
  const sheets = google.sheets({ version: 'v4', auth });

  const readRes = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'A1:Z110',
  });
  const rows = readRes.data.values || [];

  // まず幅広い行のヘッダー行ぽいもの探す
  console.log('Row 1:', JSON.stringify(rows[0]));
  console.log('Row 2:', JSON.stringify(rows[1]));
  console.log('Row 3:', JSON.stringify(rows[2]));
  console.log('Row 4:', JSON.stringify(rows[3]));
  console.log('---');
  // 既存のデータ行(Mexico 66, 80以前)の最大列を確認
  const sample = rows[3];  // Row 4 がデータ例だったはず
  if (sample) {
    console.log('Row 4列数:', sample.length);
  }

  // 対象行（86-103）を列番号つきで表示
  console.log('\n=== 新規登録行 ===');
  for (let i = 85; i < rows.length; i++) {
    const row = rows[i];
    console.log(`Row ${i + 1} (列数=${row.length}):`);
    row.forEach((cell, j) => {
      if (cell) {
        const colLetter = String.fromCharCode(65 + j);
        console.log(`  ${colLetter}: ${JSON.stringify(cell)}`);
      }
    });
  }

  console.log('\n=== 既存例（Row 80 TGRS）===');
  const r80 = rows[79];
  if (r80) {
    r80.forEach((cell, j) => {
      if (cell) {
        const colLetter = String.fromCharCode(65 + j);
        console.log(`  ${colLetter}: ${JSON.stringify(cell)}`);
      }
    });
  }
}

main().catch(err => {
  console.error('エラー:', err.message);
  process.exit(1);
});
