// スプレッドシートに商品情報を入力するスクリプト
const { google } = require('googleapis');
const path = require('path');

const SPREADSHEET_ID = '1fI-hjq4FvSDsRVWvmb5Z8UWHOf9tBLTFCz7AliIW3ok';
const KEY_FILE = path.resolve('C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/commerce/ebay/analytics/reffort-sheets-fcbca5a4bbc2.json');

// 商品データ（URLからスタイルコードを抽出し、検索結果からカラー名を対応付け）
const productData = [
  // Row 4: 既に入力済み（例）
  // { row: 4, color: '1183C102.002', name: 'BLACK/BLACK', gender: 'UNISEX' },

  // Row 5-30: 未入力分
  { row: 5,  code: '1183C102.100', name: 'WHITE/BLUE',             gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_100.html' },
  { row: 6,  code: '1183C102.201', name: 'BIRCH/GREEN',            gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_201.html' },
  { row: 7,  code: '1183C102.200', name: 'BIRCH/PEACOAT',          gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_200.html' },
  { row: 8,  code: '1183C102.751', name: 'YELLOW/BLACK',           gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_751.html' },
  { row: 9,  code: '1183C102.001', name: 'BLACK/WHITE',            gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_001.html' },
  { row: 10, code: '1183C102.250', name: 'BEIGE/GRASS GREEN',      gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_250.html' },
  { row: 11, code: '1183C102.104', name: 'WHITE/WHITE',            gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_104.html' },
  { row: 12, code: '1183C102.752', name: 'IVORY/BLACK',            gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_752.html' },
  { row: 13, code: '1183C102.204', name: 'BIRCH/RUST ORANGE',      gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_204.html' },
  { row: 14, code: '1183C102.203', name: 'CLAY CANYON/PAPER BAG',   gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_203.html' },
  { row: 15, code: '1183C102.701', name: 'DRAGON FRUIT/BLACK',     gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_701.html' },
  { row: 16, code: '1183C102.105', name: 'WHITE/CLASSIC RED',      gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_105.html' },
  { row: 17, code: '1183C102.600', name: 'CLASSIC RED/BLACK',      gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_600.html' },
  { row: 18, code: '1183C102.005', name: 'BLACK/DRAGON FRUIT',     gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_005.html' },
  { row: 19, code: '1183B566.700', name: 'ROSE GOLD/CREAM',        gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183b566_700.html' },
  { row: 20, code: '1183B566.020', name: 'PURE SILVER/BLACK',      gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B566_020.html' },
  { row: 21, code: '1183B566.200', name: 'GOLD/BLACK',             gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183b566_200.html' },
  { row: 22, code: '1183B566.021', name: 'SILVER/OFF WHITE',       gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B566_021.html' },
  { row: 23, code: '1183B566.201', name: 'GOLD/WHITE',             gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B566_201.html' },
  { row: 24, code: '1183B566.022', name: 'GUNMETAL/BLACK',         gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B566_022.html' },
  { row: 25, code: '1183A201.254', name: 'OATMEAL/GINGER PEACH',   gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183a201_254.html' },
  { row: 26, code: '1183A201.304', name: 'AIRY GREEN/VERDIGRIS GREEN', gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_304.html' },
  { row: 27, code: '1183A201.003', name: 'BLACK/YELLOW',           gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_003.html' },
  { row: 28, code: '1183A201.305', name: 'GARDEN GREEN/PURE SILVER', gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_305.html' },
  { row: 29, code: '1183A201.126', name: 'WHITE/BLACK',            gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_126.html' },
  { row: 30, code: '1183A201.127', name: 'CREAM/LIGHT SAGE',       gender: 'UNISEX', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183b511_100.html' },
];

// 最終行は1183B511.100のURL。Row 30のURLを修正
// Actually row 30 in CSV = 1183b511_100 → 別モデルコード
// Let me re-check: the CSV shows row 29 = 1183A201_127, row 30 = 1183b511_100
// Row 30 should have code 1183B511.100

// 修正: Row 30は1183B511_100
productData[productData.length - 1] = {
  row: 30, code: '1183B511.100', name: 'WHITE/DARK BLUE', gender: 'UNISEX',
  url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183b511_100.html'
};
// Row 29の1183A201.127用URLを修正
productData[productData.length - 2] = {
  row: 29, code: '1183A201.127', name: 'CREAM/LIGHT SAGE', gender: 'UNISEX',
  url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_127.html'
};

// 画像URL生成（2足並んだ画像 = SB_TP_GLB パターン）
function getImageUrl(code) {
  // code: "1183C102.002" → style: "1183C102_002"
  const style = code.replace('.', '_');
  return `https://asics.scene7.com/is/image/asics/${style}_SB_TP_GLB?$otmag_zoom$&qlt=99,1`;
}

async function main() {
  // サービスアカウント認証
  const auth = new google.auth.GoogleAuth({
    keyFile: KEY_FILE,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  const sheets = google.sheets({ version: 'v4', auth });

  // まず既存データを確認
  const readRes = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'A1:H30',
  });
  console.log('現在のデータ行数:', readRes.data.values ? readRes.data.values.length : 0);

  // バッチ更新データを作成
  const updates = [];

  for (const item of productData) {
    const imageUrl = getImageUrl(item.code);

    // カラー（C列）、型番（D列）、性別（F列）、商品画像URL（H列）を更新
    // C列 = カラーコード（例: 1183C102.100）→ 実はCSVを見ると C=カラー, D=型番
    // 例の行: C=1183C102.002, D=BLACK/BLACK
    // つまりカラー列にスタイルコード、型番列にカラー名
    updates.push({
      range: `C${item.row}`,
      values: [[item.code]],
    });
    updates.push({
      range: `D${item.row}`,
      values: [[item.name]],
    });
    updates.push({
      range: `F${item.row}`,
      values: [[item.gender]],
    });
    updates.push({
      range: `H${item.row}`,
      values: [[imageUrl]],
    });
  }

  // 例の行(Row 4)の画像URLも更新（2足並んだ画像に変更）
  updates.push({
    range: `H4`,
    values: [[getImageUrl('1183C102.002')]],
  });

  // バッチ更新を実行
  const result = await sheets.spreadsheets.values.batchUpdate({
    spreadsheetId: SPREADSHEET_ID,
    requestBody: {
      valueInputOption: 'RAW',
      data: updates,
    },
  });

  console.log(`更新完了: ${result.data.totalUpdatedCells} セルを更新しました`);
}

main().catch(err => {
  console.error('エラー:', err.message);
  process.exit(1);
});
