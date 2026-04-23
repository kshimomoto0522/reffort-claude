// ローカルproducts.jsonの新3モデルを本番APIに登録する
// 本番は永続ディスクのproducts.jsonを使うため、APIで追加する必要あり
const fs = require('fs');
const path = require('path');
const https = require('https');

const PRODUCTS_FILE = path.join(__dirname, 'data', 'products.json');
const PROD_HOST = 'reffort-direct-sales.onrender.com';
const TARGET_MODELS = ['MEXICO 66 SLIP-ON', 'MEXICO 66 SD VIN', 'MOAL 77 NM'];

function httpRequest(method, pathStr, body) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : null;
    const req = https.request({
      hostname: PROD_HOST,
      path: pathStr,
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(payload ? { 'Content-Length': Buffer.byteLength(payload) } : {})
      },
      timeout: 30000
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, body: data ? JSON.parse(data) : null });
        } catch (e) {
          resolve({ status: res.statusCode, body: data });
        }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    if (payload) req.write(payload);
    req.end();
  });
}

async function main() {
  console.log('==== 本番への新規3モデル登録 ====\n');

  // 本番の現状確認
  const current = await httpRequest('GET', '/api/products');
  console.log(`本番現在の商品数: ${current.body.length}`);
  current.body.forEach(p => console.log(`  - ${p.model} (displayOrder=${p.displayOrder}, variants=${p.variants.length})`));

  // 既に登録済みのモデル名を取得
  const existingModels = new Set(current.body.map(p => p.model));

  // ローカルの新3モデルを読み込み
  const localProducts = JSON.parse(fs.readFileSync(PRODUCTS_FILE, 'utf-8'));
  const modelsToRegister = localProducts.filter(p =>
    TARGET_MODELS.includes(p.model) && !existingModels.has(p.model)
  );

  console.log(`\n登録対象: ${modelsToRegister.length}モデル\n`);

  for (const m of modelsToRegister) {
    const payload = {
      model: m.model,
      displayOrder: m.displayOrder,
      variants: m.variants
    };
    const res = await httpRequest('POST', '/api/products', payload);
    if (res.status === 200) {
      console.log(`  ✓ ${m.model} 登録成功 (id=${res.body.id}, ${m.variants.length}バリアント)`);
    } else {
      console.log(`  ✗ ${m.model} 登録失敗: ${res.status} ${JSON.stringify(res.body).slice(0, 200)}`);
    }
  }

  // 登録後の確認
  console.log('\n==== 登録後の本番状態 ====');
  const after = await httpRequest('GET', '/api/products');
  console.log(`本番商品数: ${after.body.length}`);
  after.body.forEach(p => console.log(`  - ${p.model} (displayOrder=${p.displayOrder}, variants=${p.variants.length})`));
}

main().catch(err => {
  console.error('エラー:', err.message);
  process.exit(1);
});
