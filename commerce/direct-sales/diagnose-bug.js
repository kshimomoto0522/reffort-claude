// オーダー管理のCurrent Ordersと未指示の不一致原因を診断
// app.jsのrenderOrderAdminロジックを忠実に再現
const fs = require('fs');
const path = require('path');

const D = path.join(__dirname, 'data');
const orders = JSON.parse(fs.readFileSync(path.join(D, 'orders.json'), 'utf-8'));
const purchases = JSON.parse(fs.readFileSync(path.join(D, 'purchases.json'), 'utf-8'));
const shipments = JSON.parse(fs.readFileSync(path.join(D, 'shipments.json'), 'utf-8'));
const instructions = JSON.parse(fs.readFileSync(path.join(D, 'purchaseInstructions.json'), 'utf-8'));
const products = JSON.parse(fs.readFileSync(path.join(D, 'products.json'), 'utf-8'));

console.log(`orders: ${orders.length} (pending=${orders.filter(o=>o.status==='pending').length})`);
console.log(`purchases: ${purchases.length}`);
console.log(`shipments: ${shipments.length} (completed=${shipments.filter(s=>!s.pendingShipment).length})`);
console.log(`instructions: ${instructions.length}`);

// ===== 再現 =====
const pendingOrders = orders.filter(o => o.status === 'pending');
const allItems = [];
pendingOrders.forEach(o => o.items.forEach(i => allItems.push({ ...i, _orderNum: o.orderNumber })));

function groupItemsBySku(items) {
  const m = {};
  items.forEach(i => {
    if (!m[i.sku]) m[i.sku] = { sku: i.sku, model: i.model, colorway: i.colorway, sizeType: i.sizeType || 'mens', price: i.price, sizes: {} };
    const sz = i.size;
    m[i.sku].sizes[sz] = (m[i.sku].sizes[sz] || 0) + (i.quantity || 0);
  });
  return Object.values(m);
}
function groupPurchaseItems(purchases) {
  const m = {};
  purchases.forEach(p => (p.items || []).forEach(i => {
    if (!m[i.sku]) m[i.sku] = { sku: i.sku, model: i.model, colorway: i.colorway, sizeType: i.sizeType || 'mens', sizes: {} };
    m[i.sku].sizes[i.size] = (m[i.sku].sizes[i.size] || 0) + (i.quantity || 0);
  }));
  return Object.values(m);
}
function groupShippedItems(items) {
  const m = {};
  items.forEach(i => {
    if (!m[i.sku]) m[i.sku] = { sku: i.sku, model: i.model, colorway: i.colorway, sizeType: i.sizeType || 'mens', sizes: {} };
    m[i.sku].sizes[i.size] = (m[i.sku].sizes[i.size] || 0) + (i.quantity || 0);
  });
  return Object.values(m);
}
function getSizesForType() { return []; /* 全サイズ対象、結果的には実際あるsizeのみ */ }
function calcRemaining(orderGrouped, purchasedGrouped) {
  const skus = new Set();
  orderGrouped.forEach(g => skus.add(g.sku));
  purchasedGrouped.forEach(g => skus.add(g.sku));
  const result = [];
  skus.forEach(sku => {
    const o = orderGrouped.find(g => g.sku === sku);
    const p = purchasedGrouped.find(g => g.sku === sku);
    const src = o || p;
    const item = { sku, model: src.model, colorway: src.colorway, sizeType: src.sizeType, sizes: {} };
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
function mergeGroupedAdd(a, b) {
  const m = {};
  [a, b].forEach(g => g.forEach(item => {
    if (!m[item.sku]) m[item.sku] = { sku: item.sku, model: item.model, colorway: item.colorway, sizeType: item.sizeType, sizes: {} };
    Object.entries(item.sizes).forEach(([s, q]) => { m[item.sku].sizes[s] = (m[item.sku].sizes[s] || 0) + q; });
  }));
  return Object.values(m);
}
function calcInstructedItems(insts) {
  // status='pending' のみを集計(完了以外)
  const m = {};
  insts.forEach(ins => {
    if (ins.status === 'completed') return;
    (ins.items || []).forEach(it => {
      if (!m[it.sku]) m[it.sku] = { sku: it.sku, model: it.model, colorway: it.colorway, sizeType: it.sizeType || 'mens', sizes: {} };
      Object.entries(it.sizes || {}).forEach(([s, q]) => {
        m[it.sku].sizes[s] = (m[it.sku].sizes[s] || 0) + q;
      });
    });
  });
  return Object.values(m);
}

const grouped = groupItemsBySku(allItems);
const purchasedGrouped = groupPurchaseItems(purchases);
const completedShipments = shipments.filter(s => !s.pendingShipment);
const shippedItemsArr = [];
completedShipments.forEach(s => s.items.forEach(i => shippedItemsArr.push(i)));
const shippedGrouped = groupShippedItems(shippedItemsArr);

const currentOrderItems = calcRemaining(grouped, shippedGrouped);
const pendingInstructed = calcInstructedItems(instructions);
const purchasedRemainingRaw = calcRemaining(purchasedGrouped, shippedGrouped);
// 0クランプ適用
const purchasedRemaining = purchasedRemainingRaw.map(item => {
  const c = { ...item, sizes: {} };
  Object.entries(item.sizes).forEach(([s, q]) => { if (q > 0) c.sizes[s] = q; });
  return c;
}).filter(i => Object.keys(i.sizes).length > 0);

const assignedRemaining = mergeGroupedAdd(purchasedRemaining, pendingInstructed);
const unassigned = calcRemaining(currentOrderItems, assignedRemaining);

const pairSum = arr => arr.reduce((s, i) => s + Object.values(i.sizes).reduce((a,b)=>a+b,0), 0);

console.log('\n===== 集計 =====');
console.log(`grouped (全オーダー合計): ${pairSum(grouped)}足`);
console.log(`shippedGrouped (発送完了): ${pairSum(shippedGrouped)}足`);
console.log(`currentOrderItems (Current Orders): ${pairSum(currentOrderItems)}足`);
console.log(`purchasedGrouped (仕入済み合計): ${pairSum(purchasedGrouped)}足`);
console.log(`purchasedRemaining (仕入済残): ${pairSum(purchasedRemaining)}足`);
console.log(`pendingInstructed (未完了指示): ${pairSum(pendingInstructed)}足`);
console.log(`assignedRemaining (割り当て済): ${pairSum(assignedRemaining)}足`);
console.log(`unassigned (未指示): ${pairSum(unassigned)}足`);

// SKU別で差分を特定
console.log('\n===== SKU別詳細（currentOrders vs assigned, unassigned） =====');
const allSkus = new Set();
[currentOrderItems, assignedRemaining, unassigned].forEach(a => a.forEach(i => allSkus.add(i.sku)));
allSkus.forEach(sku => {
  const co = currentOrderItems.find(i => i.sku === sku);
  const as = assignedRemaining.find(i => i.sku === sku);
  const un = unassigned.find(i => i.sku === sku);
  const coP = co ? pairSum([co]) : 0;
  const asP = as ? pairSum([as]) : 0;
  const unP = un ? pairSum([un]) : 0;
  const expected = coP - asP;
  const flag = (expected !== unP) ? '  ⚠️ 不一致' : '';
  if (coP > 0 || asP > 0 || unP > 0) {
    console.log(`  ${sku}: current=${coP}, assigned=${asP}, unassigned=${unP} (expected=${Math.max(0,expected)})${flag}`);
    // サイズ別も
    if (co) console.log(`    currentSizes:`, JSON.stringify(co.sizes));
    if (as) console.log(`    assignedSizes:`, JSON.stringify(as.sizes));
    if (un) console.log(`    unassignedSizes:`, JSON.stringify(un.sizes));
  }
});

// 最新オーダーと既存オーダーを分けて表示
console.log('\n===== 全pendingオーダー =====');
pendingOrders.forEach(o => {
  const items = o.items || [];
  const total = items.reduce((s,i)=>s+(i.quantity||0),0);
  console.log(`  ${o.orderNumber} ${o.createdAt || ''} items=${items.length} pairs=${total}`);
});
