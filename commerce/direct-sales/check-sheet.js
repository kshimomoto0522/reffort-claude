// スプレッドシートの現状確認
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

  // ヘッダー1行目と、対象行周辺を読む
  const readRes = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'A1:H110',
  });
  const rows = readRes.data.values || [];
  console.log('総行数:', rows.length);
  console.log('1行目（ヘッダー）:', JSON.stringify(rows[0]));
  console.log('---');
  // 80行目以降を表示
  for (let i = 79; i < rows.length; i++) {
    console.log(`Row ${i + 1}:`, JSON.stringify(rows[i]));
  }
}

main().catch(err => {
  console.error('エラー:', err.message);
  process.exit(1);
});
