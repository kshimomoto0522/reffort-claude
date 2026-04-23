// 既存オーダーと新オーダーの紐付け状況を詳しく診断
const fs = require('fs');
const path = require('path');

const D = path.join(__dirname, 'data');
const orders = JSON.parse(fs.readFileSync(path.join(D, 'orders.json'), 'utf-8'));
const purchases = JSON.parse(fs.readFileSync(path.join(D, 'purchases.json'), 'utf-8'));
const shipments = JSON.parse(fs.readFileSync(path.join(D, 'shipments.json'), 'utf-8'));

console.log('===== 各pendingオーダーの発送状況 =====');
const pendingOrders = orders.filter(o => o.status === 'pending');
pendingOrders.forEach((o, idx) => {
  const totalPairs = (o.items || []).reduce((s, i) => s + (i.quantity || 0), 0);
  // このオーダーに紐づく shipments を探す（orderNumbers / orderId で）
  const linkedShipments = shipments.filter(s =>
    (s.orderNumbers || []).includes(o.orderNumber) ||
    (s.orderId && s.orderId === o.id)
  );
  const shippedPairs = linkedShipments.reduce((s, sh) =>
    s + (sh.items || []).reduce((a, i) => a + (i.quantity || 0), 0), 0);
  console.log(`\n[${idx}] orderNumber=${o.orderNumber} id=${o.id}`);
  console.log(`   buyer=${o.buyerName || o.buyer || '?'}  createdAt=${o.createdAt}`);
  console.log(`   status=${o.status}  items=${(o.items||[]).length}  pairs=${totalPairs}`);
  console.log(`   紐付く発送: ${linkedShipments.length}件 (${shippedPairs}足発送済)`);
  if (linkedShipments.length > 0) {
    linkedShipments.forEach(sh => {
      const pairs = (sh.items || []).reduce((a,i)=>a+(i.quantity||0),0);
      console.log(`     - shipment id=${sh.id} pending=${!!sh.pendingShipment} items=${pairs}足 paid=${sh.paid} orderNumbers=${JSON.stringify(sh.orderNumbers)}`);
    });
  }
});

console.log('\n===== shipments 一覧 =====');
shipments.forEach(s => {
  const pairs = (s.items || []).reduce((a,i)=>a+(i.quantity||0),0);
  console.log(`  id=${s.id} pending=${!!s.pendingShipment} paid=${s.paid} orderNumbers=${JSON.stringify(s.orderNumbers || [])} pairs=${pairs}`);
});

console.log('\n===== 最新オーダー(2026-04-17)のSKUを既存オーダーのSKUと照合 =====');
const newest = pendingOrders.find(o => o.createdAt && o.createdAt.startsWith('2026-04-17'));
if (newest) {
  console.log(`newest order: id=${newest.id} items=${newest.items.length}`);
  const newSkus = new Set(newest.items.map(i => i.sku));
  const oldOrders = pendingOrders.filter(o => o !== newest);
  const oldSkuMap = {};
  oldOrders.forEach(o => (o.items||[]).forEach(i => {
    oldSkuMap[i.sku] = (oldSkuMap[i.sku] || 0) + (i.quantity || 0);
  }));
  console.log('  最新と既存の両方に存在するSKU:');
  newSkus.forEach(sku => {
    if (oldSkuMap[sku] !== undefined) {
      const newQty = newest.items.filter(i => i.sku === sku).reduce((s,i)=>s+(i.quantity||0),0);
      console.log(`    - ${sku}: 既存=${oldSkuMap[sku]}足, 新オーダー=${newQty}足`);
    }
  });
}
