// Brandonオーダー(id=1776441279778)から size=9/25.75 の3行を削除
// 合計を再計算してPATCHで本番APIへ送信
const https = require('https');

const HOST = 'reffort-direct-sales.onrender.com';
const ORDER_ID = '1776441279778';
const REMOVE_SIZES = ['9/25.75', '5.5/22.75']; // 今後追加サイズが出たらここに追記

function req(method, pathStr, body) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : null;
    const r = https.request({
      hostname: HOST, path: pathStr, method,
      headers: {
        'Content-Type': 'application/json',
        ...(payload ? { 'Content-Length': Buffer.byteLength(payload) } : {})
      },
      timeout: 30000
    }, (res) => {
      let data = ''; res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: data ? JSON.parse(data) : null }); }
        catch (e) { resolve({ status: res.statusCode, body: data }); }
      });
    });
    r.on('error', reject);
    r.on('timeout', () => { r.destroy(); reject(new Error('timeout')); });
    if (payload) r.write(payload);
    r.end();
  });
}

(async () => {
  // 1. 現状取得
  const getRes = await req('GET', '/api/orders');
  const order = getRes.body.find(o => o.id === ORDER_ID);
  if (!order) { console.error('オーダー未発見'); process.exit(1); }

  console.log('=== 修正前 ===');
  console.log(`  buyer=${order.buyerName} totalPairs=${order.totalPairs} totalAmount=$${order.totalAmount}`);
  console.log(`  items総数=${order.items.length}`);

  // 2. 削除対象抽出
  const toRemove = order.items.filter(i => REMOVE_SIZES.includes(i.size));
  console.log(`\n削除対象（${toRemove.length}行）:`);
  toRemove.forEach(i => console.log(`  - ${i.sku} ${i.model} ${i.colorway} size=${i.size} qty=${i.quantity} price=$${i.price}`));

  // 3. フィルタ後のitems + 合計再計算
  const keptItems = order.items.filter(i => !REMOVE_SIZES.includes(i.size));
  const newTotalPairs = keptItems.reduce((s, i) => s + (i.quantity || 0), 0);
  const newTotalAmount = keptItems.reduce((s, i) => s + (i.price || 0) * (i.quantity || 0), 0);

  console.log('\n=== 修正後（予定） ===');
  console.log(`  items総数=${keptItems.length} totalPairs=${newTotalPairs} totalAmount=$${newTotalAmount}`);
  console.log(`  減額: $${order.totalAmount} → $${newTotalAmount} (差$${order.totalAmount - newTotalAmount})`);
  console.log(`  減足: ${order.totalPairs} → ${newTotalPairs} (差${order.totalPairs - newTotalPairs}足)`);

  // 4. PATCH送信
  const patchRes = await req('PATCH', `/api/orders/${ORDER_ID}`, {
    items: keptItems,
    totalPairs: newTotalPairs,
    totalAmount: newTotalAmount
  });
  console.log(`\nPATCH結果: status=${patchRes.status}`);
  if (patchRes.status !== 200) {
    console.error('失敗:', patchRes.body);
    process.exit(1);
  }

  // 5. 確認
  const verifyRes = await req('GET', '/api/orders');
  const after = verifyRes.body.find(o => o.id === ORDER_ID);
  console.log('\n=== 本番確認 ===');
  console.log(`  items総数=${after.items.length} totalPairs=${after.totalPairs} totalAmount=$${after.totalAmount}`);
  const leftover = after.items.filter(i => REMOVE_SIZES.includes(i.size));
  console.log(`  削除対象サイズが残っているか: ${leftover.length === 0 ? '✅ 残無し' : '⚠️ ' + leftover.length + '行残存'}`);
})();
