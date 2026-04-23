// currentOrderItemsの内部に負数が混ざっていないか確認
const fs = require('fs');
const path = require('path');

const D = path.join(__dirname, 'data');
const orders = JSON.parse(fs.readFileSync(path.join(D, 'orders.json'), 'utf-8'));
const shipments = JSON.parse(fs.readFileSync(path.join(D, 'shipments.json'), 'utf-8'));

function groupItemsBySku(items) {
  const m = {};
  items.forEach(i => {
    if (!m[i.sku]) m[i.sku] = { sku: i.sku, sizes: {} };
    m[i.sku].sizes[i.size] = (m[i.sku].sizes[i.size] || 0) + (i.quantity || 0);
  });
  return Object.values(m);
}

const pendingOrders = orders.filter(o => o.status === 'pending');
const allItems = [];
pendingOrders.forEach(o => o.items.forEach(i => allItems.push(i)));
const grouped = groupItemsBySku(allItems);

const completedShipments = shipments.filter(s => !s.pendingShipment);
const shippedItemsArr = [];
completedShipments.forEach(s => s.items.forEach(i => shippedItemsArr.push(i)));
const shippedGrouped = groupItemsBySku(shippedItemsArr);

console.log('=== order にあるSKU（pendingから集計）===');
const orderSkus = new Set(grouped.map(g => g.sku));
console.log(`${orderSkus.size}SKU`);

console.log('\n=== shipments にあるSKU ===');
const shippedSkus = new Set(shippedGrouped.map(g => g.sku));
console.log(`${shippedSkus.size}SKU`);

console.log('\n🔴 shipmentsにはあるがpendingOrdersにないSKU（過去オーダー由来）:');
const onlyShipped = [...shippedSkus].filter(sku => !orderSkus.has(sku));
onlyShipped.forEach(sku => {
  const sg = shippedGrouped.find(g => g.sku === sku);
  const total = Object.values(sg.sizes).reduce((a,b)=>a+b,0);
  console.log(`  ${sku}: 発送済=${total}足 sizes=${JSON.stringify(sg.sizes)}`);
});

console.log('\n🔵 pendingOrdersとshipments両方にあるSKU:');
const both = [...shippedSkus].filter(sku => orderSkus.has(sku));
both.forEach(sku => {
  const og = grouped.find(g => g.sku === sku);
  const sg = shippedGrouped.find(g => g.sku === sku);
  const oTotal = Object.values(og.sizes).reduce((a,b)=>a+b,0);
  const sTotal = Object.values(sg.sizes).reduce((a,b)=>a+b,0);
  console.log(`  ${sku}: order=${oTotal}, shipped=${sTotal}, diff=${oTotal-sTotal}`);
  console.log(`    orderSizes : ${JSON.stringify(og.sizes)}`);
  console.log(`    shippedSizes: ${JSON.stringify(sg.sizes)}`);
});

// calcRemainingで負数がでるケース確認
console.log('\n=== calcRemaining後の負数チェック ===');
function calcRemaining(og, pg) {
  const skus = new Set();
  og.forEach(g => skus.add(g.sku));
  pg.forEach(g => skus.add(g.sku));
  const result = [];
  skus.forEach(sku => {
    const o = og.find(g => g.sku === sku);
    const p = pg.find(g => g.sku === sku);
    const item = { sku, sizes: {} };
    const sizes = new Set([...Object.keys(o?.sizes || {}), ...Object.keys(p?.sizes || {})]);
    sizes.forEach(s => {
      const ord = (o?.sizes[s]) || 0;
      const pur = (p?.sizes[s]) || 0;
      const rem = ord - pur;
      if (rem !== 0) item.sizes[s] = rem;
    });
    if (Object.keys(item.sizes).length > 0) result.push(item);
  });
  return result;
}

const currentOrderItems = calcRemaining(grouped, shippedGrouped);
let positivePairs = 0, negativePairs = 0, netPairs = 0;
const negativeSKUs = [];
currentOrderItems.forEach(item => {
  Object.entries(item.sizes).forEach(([s, q]) => {
    netPairs += q;
    if (q > 0) positivePairs += q;
    else { negativePairs += q; }
  });
  const hasNeg = Object.values(item.sizes).some(q => q < 0);
  if (hasNeg) negativeSKUs.push(item);
});
console.log(`netPairs (合計)=${netPairs}`);
console.log(`positivePairs=${positivePairs}, negativePairs=${negativePairs}`);
console.log(`\n🔴 負数を含むSKU (${negativeSKUs.length}件):`);
negativeSKUs.forEach(item => {
  console.log(`  ${item.sku}: ${JSON.stringify(item.sizes)}`);
});
