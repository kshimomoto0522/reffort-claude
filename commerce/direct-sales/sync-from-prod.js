// =============================================
// 本番 → ローカル データ同期スクリプト
// 使い方: node sync-from-prod.js
// 本番(reffort-direct-sales.onrender.com)の全データをローカルdata/へ上書きコピー
// 方向は一方通行：ローカル → 本番 へは絶対に流れない
// =============================================
const https = require('https');
const fs = require('fs');
const path = require('path');

const BASE = 'https://reffort-direct-sales.onrender.com';
const DATA_DIR = path.join(__dirname, 'data');

// APIエンドポイント → 保存先ファイル名
const targets = [
  { api: '/api/products',     file: 'products.json' },
  { api: '/api/orders',       file: 'orders.json' },
  { api: '/api/settings',     file: 'settings.json' },
  { api: '/api/purchases',    file: 'purchases.json' },
  { api: '/api/instructions', file: 'purchaseInstructions.json' },
  { api: '/api/shipments',    file: 'shipments.json' },
  { api: '/api/coupons',      file: 'coupons.json' },
  { api: '/api/deliveries',   file: 'deliveries.json' },
];

function fetchJSON(url) {
  return new Promise((resolve, reject) => {
    https.get(url, res => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', c => body += c);
      res.on('end', () => {
        try { resolve(JSON.parse(body)); }
        catch (e) { reject(new Error(`JSON parse error for ${url}: ${body.slice(0,200)}`)); }
      });
    }).on('error', reject);
  });
}

(async () => {
  console.log('🔄 本番 → ローカル 同期開始');
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

  // 念のため同期前にバックアップ
  const backupDir = path.join(DATA_DIR, `backup_before_sync_${Date.now()}`);
  fs.mkdirSync(backupDir);
  targets.forEach(t => {
    const src = path.join(DATA_DIR, t.file);
    if (fs.existsSync(src)) fs.copyFileSync(src, path.join(backupDir, t.file));
  });
  console.log('💾 既存ローカルデータをバックアップ:', path.basename(backupDir));

  for (const t of targets) {
    try {
      const data = await fetchJSON(BASE + t.api);
      fs.writeFileSync(path.join(DATA_DIR, t.file), JSON.stringify(data, null, 2), 'utf8');
      const count = Array.isArray(data) ? `${data.length}件` : 'object';
      console.log(`  ✅ ${t.file} (${count})`);
    } catch (e) {
      console.log(`  ❌ ${t.file}: ${e.message}`);
    }
  }
  console.log('✨ 同期完了。これで本番と同じデータでローカル起動できます。');
  console.log('次: node server.js でローカルサーバー起動 → http://localhost:3000');
})();
