// 新規登録した18SKUの画像URLを検証し、SB_FR_GLBが403ならSR_FR_GLBにフォールバック
// products.json と スプレッドシートH列 両方を更新
const fs = require('fs');
const path = require('path');
const https = require('https');
const { google } = require('googleapis');

const PRODUCTS_FILE = path.join(__dirname, 'data', 'products.json');
const SPREADSHEET_ID = '1fI-hjq4FvSDsRVWvmb5Z8UWHOf9tBLTFCz7AliIW3ok';
const KEY_FILE = path.resolve('C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/commerce/ebay/analytics/reffort-sheets-fcbca5a4bbc2.json');

const TARGET_MODELS = ['MEXICO 66 SLIP-ON', 'MEXICO 66 SD VIN', 'MOAL 77 NM'];

// SKU → スプレッドシート行番号
const SKU_TO_ROW = {
  '1183A360.205': 86, '1183A360.121': 87, '1183A360.401': 88, '1183A360.002': 89,
  '1183A360.131': 90, '1183A360.132': 91, '1183A746.751': 92, '1183C141.100': 93,
  '1183B761.201': 94, '1183B761.301': 95,
  '1183C015.200': 96, '1183C015.101': 97, '1183C015.104': 98, '1183C015.201': 99,
  '1183C015.202': 100, '1183C015.205': 101, '1183C015.106': 102, '1183C015.400': 103,
};

function buildImageUrl(sku, pattern) {
  const style = sku.replace('.', '_');
  return `https://asics.scene7.com/is/image/asics/${style}_${pattern}?$otmag_zoom$&qlt=99,1`;
}

// HEADリクエストでステータス確認（UAつき）
function checkStatus(url) {
  return new Promise((resolve) => {
    const u = new URL(url);
    const req = https.request({
      hostname: u.hostname,
      path: u.pathname + u.search,
      method: 'HEAD',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      },
      timeout: 10000
    }, (res) => {
      resolve(res.statusCode);
    });
    req.on('error', () => resolve(0));
    req.on('timeout', () => { req.destroy(); resolve(0); });
    req.end();
  });
}

async function pickBestImageUrl(sku) {
  const primary = buildImageUrl(sku, 'SB_FR_GLB');
  const primaryStatus = await checkStatus(primary);
  if (primaryStatus === 200) return { url: primary, pattern: 'SB_FR_GLB', status: 200 };

  const fallback = buildImageUrl(sku, 'SR_FR_GLB');
  const fallbackStatus = await checkStatus(fallback);
  if (fallbackStatus === 200) return { url: fallback, pattern: 'SR_FR_GLB', status: 200 };

  return { url: primary, pattern: 'SB_FR_GLB', status: primaryStatus, note: `fallback also failed (${fallbackStatus})` };
}

async function main() {
  console.log('==== 画像URL検証開始 ====\n');

  // products.json読み込み
  const products = JSON.parse(fs.readFileSync(PRODUCTS_FILE, 'utf-8'));
  const sheetUpdates = [];
  const jsonUpdates = [];  // { sku, newUrl, row }

  for (const modelName of TARGET_MODELS) {
    const product = products.find(p => p.model === modelName);
    if (!product) continue;
    console.log(`--- ${modelName} ---`);
    for (const v of product.variants) {
      const result = await pickBestImageUrl(v.sku);
      const row = SKU_TO_ROW[v.sku];
      const mark = result.pattern === 'SB_FR_GLB' && result.status === 200 ? '✓' : (result.status === 200 ? '→SR_FR_GLB' : '✗');
      console.log(`  ${mark} ${v.sku} (row ${row}): ${result.pattern} [${result.status}]${result.note ? ' ' + result.note : ''}`);

      if (result.status === 200 && v.image !== result.url) {
        v.image = result.url;
        jsonUpdates.push({ sku: v.sku, newUrl: result.url });
        if (row) sheetUpdates.push({ range: `H${row}`, values: [[result.url]] });
      }
    }
  }

  console.log(`\n==== 更新対象: ${jsonUpdates.length}件 ====`);

  if (jsonUpdates.length === 0) {
    console.log('修正不要');
    return;
  }

  // products.json書き込み
  fs.writeFileSync(PRODUCTS_FILE, JSON.stringify(products, null, 2), 'utf-8');
  console.log('products.json 更新完了');

  // スプレッドシート更新
  const auth = new google.auth.GoogleAuth({
    keyFile: KEY_FILE,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  const sheets = google.sheets({ version: 'v4', auth });
  const result = await sheets.spreadsheets.values.batchUpdate({
    spreadsheetId: SPREADSHEET_ID,
    requestBody: { valueInputOption: 'RAW', data: sheetUpdates },
  });
  console.log(`スプレッドシート更新完了: ${result.data.totalUpdatedCells}セル`);
}

main().catch(err => {
  console.error('エラー:', err.message);
  process.exit(1);
});
