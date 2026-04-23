// スプレッドシートの全データを読み取るスクリプト
const { google } = require('googleapis');
const path = require('path');

const SPREADSHEET_ID = '1fI-hjq4FvSDsRVWvmb5Z8UWHOf9tBLTFCz7AliIW3ok';
const KEY_FILE = path.resolve('C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/commerce/ebay/analytics/reffort-sheets-fcbca5a4bbc2.json');

async function main() {
  // サービスアカウントで認証
  const auth = new google.auth.GoogleAuth({
    keyFile: KEY_FILE,
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });
  const sheets = google.sheets({ version: 'v4', auth });

  // まずシート一覧を取得
  const meta = await sheets.spreadsheets.get({ spreadsheetId: SPREADSHEET_ID });
  const sheetNames = meta.data.sheets.map(s => s.properties.title);
  console.log('=== シート一覧 ===');
  console.log(sheetNames.join(', '));
  console.log('');

  // 全シートのデータを読む
  for (const sheetName of sheetNames) {
    console.log(`=== シート: ${sheetName} ===`);
    const res = await sheets.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: `'${sheetName}'`,
    });
    const rows = res.data.values;
    if (!rows || rows.length === 0) {
      console.log('(データなし)');
      console.log('');
      continue;
    }
    console.log(`行数: ${rows.length}`);
    console.log('');

    // 全行を出力
    rows.forEach((row, i) => {
      console.log(`[Row ${i + 1}] ${JSON.stringify(row)}`);
    });
    console.log('');
  }
}

main().catch(err => {
  console.error('エラー:', err.message);
  process.exit(1);
});
