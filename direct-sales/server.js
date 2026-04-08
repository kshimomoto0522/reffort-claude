// =============================================
// Direct Sales - NYダイレクト販売 注文管理サーバー
// eBay以外の直接取引を管理するWebアプリ
// =============================================
const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// JSONリクエストを処理するミドルウェア
app.use(express.json());
// 静的ファイル（HTML/CSS/JS）を配信
app.use(express.static(path.join(__dirname, 'public')));

// データファイルのパス
const DATA_DIR = path.join(__dirname, 'data');
const PRODUCTS_FILE = path.join(DATA_DIR, 'products.json');
const ORDERS_FILE = path.join(DATA_DIR, 'orders.json');
const SETTINGS_FILE = path.join(DATA_DIR, 'settings.json');
const PURCHASES_FILE = path.join(DATA_DIR, 'purchases.json');
const INSTRUCTIONS_FILE = path.join(DATA_DIR, 'purchaseInstructions.json');
const SHIPMENTS_FILE = path.join(DATA_DIR, 'shipments.json');
const COUPONS_FILE = path.join(DATA_DIR, 'coupons.json');
const DELIVERIES_FILE = path.join(DATA_DIR, 'deliveries.json');

// =============================================
// データ読み書きヘルパー
// =============================================
function readJSON(filePath, defaultValue = []) {
  try {
    if (!fs.existsSync(filePath)) return defaultValue;
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch {
    return defaultValue;
  }
}

function writeJSON(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

// =============================================
// 認証API（セクション別パスワード）
// デフォルトは全て '0000'、詳細設定ページで変更可能。
// settings.json の sectionPasswords が優先される。
// =============================================
const DEFAULT_PASSWORDS = {
  buyer: '0000',
  'seller-top': '0000',
  order: '0000',
  product: '0000',
  settings: '0000',
  finance: '0000',
  shipping: '0000',
  coupon: '0000'
};

// settings.json からパスワード設定を取得（なければデフォルト）
function getSectionPasswords() {
  const settings = readJSON(SETTINGS_FILE, {});
  const saved = settings.sectionPasswords || {};
  return { ...DEFAULT_PASSWORDS, ...saved };
}

app.post('/api/auth', (req, res) => {
  const { role, password } = req.body;
  const PASSWORDS = getSectionPasswords();

  // バイヤー認証
  if (role === 'buyer') {
    if (PASSWORDS.buyer !== password) {
      return res.status(401).json({ error: 'Wrong password' });
    }
    return res.json({ success: true, role: 'buyer' });
  }

  // セラー各セクション認証
  if (PASSWORDS[role] && PASSWORDS[role] === password) {
    return res.json({ success: true, role });
  }

  // 仕入拠点認証（拠点ID＋パスワードで認証）
  if (role === 'purchase') {
    const { locationId } = req.body;
    const settings = readJSON(SETTINGS_FILE, { locations: [] });
    // 拠点IDが指定されていればその拠点で認証
    const location = locationId
      ? settings.locations.find(l => l.id === locationId && l.password === password)
      : settings.locations.find(l => l.password === password);
    if (location) {
      return res.json({ success: true, role: 'purchase', locationId: location.id, locationName: location.name });
    }
    return res.status(401).json({ error: 'Wrong password' });
  }

  return res.status(401).json({ error: 'Wrong password' });
});

// =============================================
// 商品API
// =============================================

// 商品一覧を取得
app.get('/api/products', (req, res) => {
  const products = readJSON(PRODUCTS_FILE);
  res.json(products);
});

// 商品を追加（管理者用）
app.post('/api/products', (req, res) => {
  const products = readJSON(PRODUCTS_FILE);
  const product = {
    id: Date.now().toString(),
    displayOrder: products.length,
    ...req.body
  };
  products.push(product);
  writeJSON(PRODUCTS_FILE, products);
  res.json(product);
});

// 商品を更新（管理者用）
app.put('/api/products/:id', (req, res) => {
  const products = readJSON(PRODUCTS_FILE);
  const idx = products.findIndex(p => p.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Product not found' });
  products[idx] = { ...products[idx], ...req.body };
  writeJSON(PRODUCTS_FILE, products);
  res.json(products[idx]);
});

// 商品を削除（管理者用）
app.delete('/api/products/:id', (req, res) => {
  let products = readJSON(PRODUCTS_FILE);
  products = products.filter(p => p.id !== req.params.id);
  writeJSON(PRODUCTS_FILE, products);
  res.json({ success: true });
});

// 商品の表示順を更新（管理者用）
app.put('/api/products-order', (req, res) => {
  const { orderedIds } = req.body; // ["id1", "id2", ...]
  const products = readJSON(PRODUCTS_FILE);
  const reordered = [];
  orderedIds.forEach((id, i) => {
    const p = products.find(x => x.id === id);
    if (p) {
      p.displayOrder = i;
      reordered.push(p);
    }
  });
  // 含まれていない商品も追加
  products.forEach(p => {
    if (!orderedIds.includes(p.id)) reordered.push(p);
  });
  writeJSON(PRODUCTS_FILE, reordered);
  res.json(reordered);
});

// =============================================
// 注文API
// =============================================

// 最新オーダーIDを追跡（新規オーダー通知用）
let lastKnownOrderCount = null;

// 注文一覧を取得
app.get('/api/orders', (req, res) => {
  const orders = readJSON(ORDERS_FILE);
  res.json(orders);
});

// 新規オーダーチェック（ポーリング用）
app.get('/api/orders/check-new', (req, res) => {
  const orders = readJSON(ORDERS_FILE);
  const pendingCount = orders.filter(o => o.status === 'pending').length;
  const since = req.query.since; // ISO日付文字列
  let newOrders = [];
  if (since) {
    newOrders = orders.filter(o => o.status === 'pending' && new Date(o.createdAt) > new Date(since));
  }
  res.json({ pendingCount, newOrders: newOrders.length, latest: newOrders });
});

// 新規注文を作成（バイヤーがカートから注文）
app.post('/api/orders', (req, res) => {
  const orders = readJSON(ORDERS_FILE);
  const order = {
    id: Date.now().toString(),
    items: req.body.items,
    totalPairs: req.body.totalPairs,
    totalAmount: req.body.totalAmount,
    buyerId: req.body.buyerId || null,
    buyerName: req.body.buyerName || null,
    status: 'pending',
    shippedDate: null,
    shippedExchangeRate: null, // 発送時の為替レートを固定
    paidAt: null,
    createdAt: new Date().toISOString()
  };
  orders.push(order);
  writeJSON(ORDERS_FILE, orders);
  res.json(order);
});

// 注文ステータスを更新（管理者用）
app.patch('/api/orders/:id', (req, res) => {
  const orders = readJSON(ORDERS_FILE);
  const idx = orders.findIndex(o => o.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Order not found' });

  const updates = req.body;
  orders[idx] = { ...orders[idx], ...updates };
  writeJSON(ORDERS_FILE, orders);
  res.json(orders[idx]);
});

// 注文を削除（管理者用）
app.delete('/api/orders/:id', (req, res) => {
  let orders = readJSON(ORDERS_FILE);
  orders = orders.filter(o => o.id !== req.params.id);
  writeJSON(ORDERS_FILE, orders);
  res.json({ success: true });
});

// オーダー数量調整API（管理者が編集モードで増減）
app.post('/api/orders/adjust', (req, res) => {
  const orders = readJSON(ORDERS_FILE);
  const { items } = req.body; // [{sku, model, colorway, size, sizeType, price, delta}]

  const additions = items.filter(i => i.delta > 0);
  const removals = items.filter(i => i.delta < 0);

  // 減少処理：既存pendingオーダーからアイテムを削除
  removals.forEach(removal => {
    let toRemove = Math.abs(removal.delta);
    for (const order of orders) {
      if (order.status !== 'pending' || toRemove <= 0) continue;
      for (let i = order.items.length - 1; i >= 0; i--) {
        const item = order.items[i];
        if (item.sku === removal.sku && item.size === removal.size) {
          const reduce = Math.min(item.quantity, toRemove);
          item.quantity -= reduce;
          toRemove -= reduce;
          if (item.quantity <= 0) order.items.splice(i, 1);
        }
      }
      order.totalPairs = order.items.reduce((s, it) => s + it.quantity, 0);
      order.totalAmount = order.items.reduce((s, it) => s + it.quantity * it.price, 0);
    }
  });

  // 増加処理：管理者調整オーダーを作成
  if (additions.length > 0) {
    const adminItems = additions.map(a => ({
      sku: a.sku, model: a.model, colorway: a.colorway,
      size: a.size, sizeType: a.sizeType, price: a.price,
      quantity: a.delta
    }));
    orders.push({
      id: Date.now().toString(),
      items: adminItems,
      totalPairs: adminItems.reduce((s, it) => s + it.quantity, 0),
      totalAmount: adminItems.reduce((s, it) => s + it.quantity * it.price, 0),
      buyerId: null, buyerName: 'Admin',
      status: 'pending', shippedDate: null, shippedExchangeRate: null, paidAt: null,
      createdAt: new Date().toISOString()
    });
  }

  // 空のオーダーを除去
  const cleaned = orders.filter(o => o.items.length > 0);
  writeJSON(ORDERS_FILE, cleaned);
  res.json({ success: true });
});

// 仕入数量調整API（管理者が編集モードで増減）
app.post('/api/purchases/adjust', (req, res) => {
  const purchases = readJSON(PURCHASES_FILE);
  const { locationId, locationName, items } = req.body; // [{sku, size, sizeType, delta}]

  const additions = items.filter(i => i.delta > 0);
  const removals = items.filter(i => i.delta < 0);

  // 減少処理
  removals.forEach(removal => {
    let toRemove = Math.abs(removal.delta);
    for (const purchase of purchases) {
      if (purchase.locationId !== locationId || toRemove <= 0) continue;
      for (let i = purchase.items.length - 1; i >= 0; i--) {
        const item = purchase.items[i];
        if (item.sku === removal.sku && item.size === removal.size) {
          const reduce = Math.min(item.quantity, toRemove);
          item.quantity -= reduce;
          toRemove -= reduce;
          if (item.quantity <= 0) purchase.items.splice(i, 1);
        }
      }
    }
  });

  // 増加処理
  if (additions.length > 0) {
    purchases.push({
      id: Date.now().toString(),
      locationId, locationName,
      items: additions.map(a => ({
        sku: a.sku, size: a.size, quantity: a.delta, sizeType: a.sizeType
      })),
      createdAt: new Date().toISOString()
    });
  }

  // 空の仕入を除去
  const cleaned = purchases.filter(p => p.items.length > 0);
  writeJSON(PURCHASES_FILE, cleaned);
  res.json({ success: true });
});

// =============================================
// 設定API
// =============================================
const DEFAULT_SETTINGS = {
  customsUnitPrice: 0,
  shippingPerPair: 0,
  couponPerPair: 0,
  locations: [],
  buyers: [],
  sectionPasswords: {}  // { buyer:'0000', 'seller-top':'0000', order:'0000', ... }
};

// ページ別パスワードの取得用API（詳細設定画面で使用）
app.get('/api/section-passwords', (req, res) => {
  const settings = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
  const passwords = { ...DEFAULT_PASSWORDS, ...(settings.sectionPasswords || {}) };
  res.json(passwords);
});

// ページ別パスワードの一括更新用API
app.put('/api/section-passwords', (req, res) => {
  const settings = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
  settings.sectionPasswords = { ...(settings.sectionPasswords || {}), ...req.body };
  writeJSON(SETTINGS_FILE, settings);
  res.json(settings.sectionPasswords);
});

// =============================================
// 納品済API（deliveries） - 手動管理
// BayPack倉庫への納品済数量を記録。
// データ構造: [{ sku, size, quantity, updatedAt }]
// =============================================
app.get('/api/deliveries', (req, res) => {
  const deliveries = readJSON(DELIVERIES_FILE, []);
  res.json(deliveries);
});

// 納品済の数量を設定（上書き保存）
app.put('/api/deliveries', (req, res) => {
  // req.body: { sku, size, quantity }
  const { sku, size, quantity } = req.body;
  if (!sku || !size) return res.status(400).json({ error: 'sku and size required' });
  const deliveries = readJSON(DELIVERIES_FILE, []);
  const idx = deliveries.findIndex(d => d.sku === sku && d.size === size);
  const qty = Math.max(0, parseInt(quantity, 10) || 0);
  if (idx >= 0) {
    if (qty === 0) {
      deliveries.splice(idx, 1);
    } else {
      deliveries[idx].quantity = qty;
      deliveries[idx].updatedAt = new Date().toISOString();
    }
  } else if (qty > 0) {
    deliveries.push({ sku, size, quantity: qty, updatedAt: new Date().toISOString() });
  }
  writeJSON(DELIVERIES_FILE, deliveries);
  res.json(deliveries);
});

// 設定を取得
app.get('/api/settings', (req, res) => {
  const settings = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
  res.json(settings);
});

// 設定を更新
app.put('/api/settings', (req, res) => {
  const current = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
  const updated = { ...current, ...req.body };
  writeJSON(SETTINGS_FILE, updated);
  res.json(updated);
});

// 拠点を追加
app.post('/api/settings/locations', (req, res) => {
  const settings = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
  const location = {
    id: 'loc-' + Date.now(),
    name: req.body.name,
    password: req.body.password
  };
  settings.locations.push(location);
  writeJSON(SETTINGS_FILE, settings);
  res.json(location);
});

// 拠点を更新
app.put('/api/settings/locations/:id', (req, res) => {
  const settings = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
  const idx = settings.locations.findIndex(l => l.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Location not found' });
  settings.locations[idx] = { ...settings.locations[idx], ...req.body };
  writeJSON(SETTINGS_FILE, settings);
  res.json(settings.locations[idx]);
});

// 拠点を削除
app.delete('/api/settings/locations/:id', (req, res) => {
  const settings = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
  settings.locations = settings.locations.filter(l => l.id !== req.params.id);
  writeJSON(SETTINGS_FILE, settings);
  res.json({ success: true });
});

// バイヤーを追加
app.post('/api/settings/buyers', (req, res) => {
  const settings = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
  if (!settings.buyers) settings.buyers = [];
  const buyer = {
    id: 'buyer-' + Date.now(),
    name: req.body.name,
    phone: req.body.phone // 国番号付き（例: +12125551234）
  };
  settings.buyers.push(buyer);
  writeJSON(SETTINGS_FILE, settings);
  res.json(buyer);
});

// バイヤーを更新
app.put('/api/settings/buyers/:id', (req, res) => {
  const settings = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
  if (!settings.buyers) settings.buyers = [];
  const idx = settings.buyers.findIndex(b => b.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Buyer not found' });
  settings.buyers[idx] = { ...settings.buyers[idx], ...req.body };
  writeJSON(SETTINGS_FILE, settings);
  res.json(settings.buyers[idx]);
});

// バイヤーを削除
app.delete('/api/settings/buyers/:id', (req, res) => {
  const settings = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
  if (!settings.buyers) settings.buyers = [];
  settings.buyers = settings.buyers.filter(b => b.id !== req.params.id);
  writeJSON(SETTINGS_FILE, settings);
  res.json({ success: true });
});

// =============================================
// 仕入API（購入記録）
// =============================================

// 仕入記録一覧
app.get('/api/purchases', (req, res) => {
  const purchases = readJSON(PURCHASES_FILE);
  res.json(purchases);
});

// 仕入記録を追加
// 仕入記録を削除（復元誤投稿の取り消し等に使用）
app.delete('/api/purchases/:id', (req, res) => {
  let purchases = readJSON(PURCHASES_FILE);
  const before = purchases.length;
  purchases = purchases.filter(p => p.id !== req.params.id);
  writeJSON(PURCHASES_FILE, purchases);
  res.json({ success: true, deleted: before - purchases.length });
});

app.post('/api/purchases', (req, res) => {
  const purchases = readJSON(PURCHASES_FILE);
  const purchase = {
    id: Date.now().toString() + Math.floor(Math.random()*1000),
    locationId: req.body.locationId,
    locationName: req.body.locationName,
    items: req.body.items, // [{sku, size, quantity, sizeType}]
    // 復元やバッチ完了時にcreatedAtを指定できる。未指定なら現在時刻
    createdAt: req.body.createdAt || new Date().toISOString()
  };
  // batchName/batchId/instructionIdが指定されていれば一緒に保存
  if (req.body.batchName) purchase.batchName = req.body.batchName;
  if (req.body.batchId) purchase.batchId = req.body.batchId;
  if (req.body.instructionId) purchase.instructionId = req.body.instructionId;
  purchases.push(purchase);
  writeJSON(PURCHASES_FILE, purchases);
  res.json(purchase);
});

// =============================================
// 仕入指示API（管理者が拠点に仕入を指示）
// =============================================

// 仕様B: 仕入指示は完了するまで期限切れにしない（日をまたいでも残り続ける）
// 過去に旧仕様で expired になったバッチを active/pending に戻す
function expireOldInstructions() {
  const instructions = readJSON(INSTRUCTIONS_FILE);
  let changed = false;
  instructions.forEach(inst => {
    if (inst.status === 'expired') { inst.status = 'active'; changed = true; }
    (inst.batches || []).forEach(b => {
      if (b.status === 'expired') { b.status = 'pending'; changed = true; }
    });
  });
  if (changed) writeJSON(INSTRUCTIONS_FILE, instructions);
  return instructions;
}

// 仕入指示一覧（期限切れチェック付き）
app.get('/api/instructions', (req, res) => {
  const instructions = expireOldInstructions();
  res.json(instructions);
});

// 特定拠点のアクティブな仕入指示を取得（期限切れチェック付き）
app.get('/api/instructions/location/:locationId', (req, res) => {
  const instructions = expireOldInstructions();
  const active = instructions.filter(i =>
    i.locationId === req.params.locationId && i.status === 'active'
  );
  res.json(active);
});

// 仕入指示を作成（管理者用）
app.post('/api/instructions', (req, res) => {
  const instructions = readJSON(INSTRUCTIONS_FILE);
  const instruction = {
    id: Date.now().toString(),
    locationId: req.body.locationId,
    locationName: req.body.locationName,
    batches: req.body.batches, // [{id, name, items: [{sku, model, colorway, sizeType, image, sizes: {size: qty}}], status: 'pending', completedAt: null}]
    status: 'active',
    createdAt: new Date().toISOString()
  };
  instructions.push(instruction);
  writeJSON(INSTRUCTIONS_FILE, instructions);
  res.json(instruction);
});

// バッチを完了（仕入担当が完了ボタンを押したとき）
app.post('/api/instructions/:instructionId/batches/:batchId/complete', (req, res) => {
  const instructions = readJSON(INSTRUCTIONS_FILE);
  const inst = instructions.find(i => i.id === req.params.instructionId);
  if (!inst) return res.status(404).json({ error: 'Instruction not found' });

  const batch = inst.batches.find(b => b.id === req.params.batchId);
  if (!batch) return res.status(404).json({ error: 'Batch not found' });
  if (batch.status === 'completed') return res.status(400).json({ error: 'Already completed' });

  // バッチを完了にする
  batch.status = 'completed';
  batch.completedAt = new Date().toISOString();

  // 全バッチ完了なら指示全体も完了
  if (inst.batches.every(b => b.status === 'completed')) {
    inst.status = 'completed';
  }

  writeJSON(INSTRUCTIONS_FILE, instructions);

  // 仕入記録（purchases）にも反映
  const purchases = readJSON(PURCHASES_FILE);
  const purchaseItems = [];
  batch.items.forEach(item => {
    Object.entries(item.sizes).forEach(([size, qty]) => {
      if (qty > 0) {
        purchaseItems.push({
          sku: item.sku,
          model: item.model,
          colorway: item.colorway,
          size,
          quantity: qty,
          sizeType: item.sizeType
        });
      }
    });
  });

  if (purchaseItems.length > 0) {
    purchases.push({
      id: Date.now().toString(),
      locationId: inst.locationId,
      locationName: inst.locationName,
      instructionId: inst.id,
      batchId: batch.id,
      batchName: batch.name,
      items: purchaseItems,
      createdAt: new Date().toISOString()
    });
    writeJSON(PURCHASES_FILE, purchases);
  }

  res.json({ instruction: inst, batch });
});

// 仕入指示の順番を変更（管理者用）
app.put('/api/instructions/reorder', (req, res) => {
  const { orderedIds } = req.body; // ["id1", "id2", ...]
  const instructions = readJSON(INSTRUCTIONS_FILE);
  const reordered = [];
  orderedIds.forEach((id, i) => {
    const inst = instructions.find(x => x.id === id);
    if (inst) {
      inst.displayOrder = i;
      reordered.push(inst);
    }
  });
  // 含まれていないものも追加
  instructions.forEach(inst => {
    if (!orderedIds.includes(inst.id)) reordered.push(inst);
  });
  writeJSON(INSTRUCTIONS_FILE, reordered);
  res.json(reordered);
});

// 仕入指示を削除（管理者用）
app.delete('/api/instructions/:id', (req, res) => {
  let instructions = readJSON(INSTRUCTIONS_FILE);
  instructions = instructions.filter(i => i.id !== req.params.id);
  writeJSON(INSTRUCTIONS_FILE, instructions);
  res.json({ success: true });
});

// =============================================
// 為替レートAPI（USD/JPY）
// =============================================
let cachedRate = null;
let rateLastFetched = 0;
const RATE_CACHE_MS = 30 * 60 * 1000; // 30分キャッシュ

app.get('/api/exchange-rate', async (req, res) => {
  const now = Date.now();
  if (cachedRate && (now - rateLastFetched) < RATE_CACHE_MS) {
    return res.json({ rate: cachedRate, cached: true });
  }
  try {
    // 無料の為替APIを使用
    const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
    const data = await response.json();
    cachedRate = data.rates.JPY;
    rateLastFetched = now;
    res.json({ rate: cachedRate, cached: false });
  } catch (e) {
    // フォールバック：キャッシュがあればそれを使う、なければ仮レート
    res.json({ rate: cachedRate || 150, cached: true, error: 'API unavailable' });
  }
});

// =============================================
// 発送API
// =============================================

// 発送一覧
app.get('/api/shipments', (req, res) => {
  const shipments = readJSON(SHIPMENTS_FILE);
  res.json(shipments);
});

// 発送可能な仕入済アイテムを取得（拠点ごとにグループ化）
app.get('/api/shipped-items', (req, res) => {
  // 仕入済（purchases）から発送済（shipments）を差し引いた残りを返す
  const purchases = readJSON(PURCHASES_FILE);
  const shipments = readJSON(SHIPMENTS_FILE);

  // 発送済の数量を集計 {sku: {size: qty}}
  const shippedMap = {};
  shipments.forEach(s => {
    s.items.forEach(item => {
      if (!shippedMap[item.sku]) shippedMap[item.sku] = {};
      shippedMap[item.sku][item.size] = (shippedMap[item.sku][item.size] || 0) + item.quantity;
    });
  });

  // 仕入済を拠点ごとにグループ化し、発送済を差し引く
  const locMap = {}; // {locId: {locName, items: {sku: {size: qty, model, colorway, sizeType, image}}}}
  purchases.forEach(p => {
    if (!locMap[p.locationId]) locMap[p.locationId] = { locationName: p.locationName, items: {} };
    p.items.forEach(item => {
      if (!locMap[p.locationId].items[item.sku]) {
        locMap[p.locationId].items[item.sku] = { model: item.model, colorway: item.colorway, sizeType: item.sizeType, sizes: {} };
      }
      locMap[p.locationId].items[item.sku].sizes[item.size] =
        (locMap[p.locationId].items[item.sku].sizes[item.size] || 0) + item.quantity;
    });
  });

  // 発送済を差し引く（拠点問わず全体から差し引く）
  // 発送済は拠点をまたぐ場合があるので、全体の仕入済から差し引く
  const remainingShipped = JSON.parse(JSON.stringify(shippedMap));
  const result = {};
  for (const [locId, locData] of Object.entries(locMap)) {
    result[locId] = { locationName: locData.locationName, items: [] };
    for (const [sku, itemData] of Object.entries(locData.items)) {
      const remainingSizes = {};
      for (const [size, qty] of Object.entries(itemData.sizes)) {
        // この拠点のこのSKU/サイズから発送済を差し引く
        const shipped = (remainingShipped[sku] && remainingShipped[sku][size]) || 0;
        const deduct = Math.min(shipped, qty);
        const remaining = qty - deduct;
        if (remainingShipped[sku]) remainingShipped[sku][size] = shipped - deduct;
        if (remaining > 0) remainingSizes[size] = remaining;
      }
      if (Object.keys(remainingSizes).length > 0) {
        result[locId].items.push({
          sku, model: itemData.model, colorway: itemData.colorway,
          sizeType: itemData.sizeType, sizes: remainingSizes
        });
      }
    }
    // アイテムが空の拠点は除外
    if (result[locId].items.length === 0) delete result[locId];
  }

  res.json(result);
});

// 発送を作成
app.post('/api/shipments', (req, res) => {
  const shipments = readJSON(SHIPMENTS_FILE);
  const shipment = {
    id: Date.now().toString(),
    items: req.body.items, // [{sku, model, colorway, size, quantity, sizeType, locationId, locationName}]
    locations: req.body.locations, // [{id, name}] 関連拠点
    tracking: req.body.tracking, // [{carrier, trackingNumber}]
    orderNumbers: req.body.orderNumbers || [], // 関連オーダー番号
    createdAt: new Date().toISOString()
  };
  shipments.push(shipment);
  writeJSON(SHIPMENTS_FILE, shipments);

  // 関連オーダーのステータスを更新
  if (shipment.orderNumbers.length > 0) {
    const orders = readJSON(ORDERS_FILE);
    let changed = false;
    shipment.orderNumbers.forEach(orderNum => {
      const order = orders.find(o => o.id === orderNum);
      if (order) {
        order.status = 'shipped';
        order.shippedDate = shipment.createdAt;
        order.tracking = shipment.tracking;
        order.shipmentId = shipment.id;
        changed = true;
      }
    });
    if (changed) writeJSON(ORDERS_FILE, orders);

    // バイヤー情報を収集してレスポンスに含める
    const settings = readJSON(SETTINGS_FILE, DEFAULT_SETTINGS);
    const buyerMap = {};
    shipment.orderNumbers.forEach(orderNum => {
      const order = orders.find(o => o.id === orderNum);
      if (order && order.buyerId) {
        const buyer = (settings.buyers || []).find(b => b.id === order.buyerId);
        if (buyer) {
          if (!buyerMap[buyer.id]) {
            buyerMap[buyer.id] = { name: buyer.name, phone: buyer.phone, orderNumbers: [] };
          }
          buyerMap[buyer.id].orderNumbers.push(orderNum);
        }
      }
    });
    shipment.buyers = Object.values(buyerMap);
  }

  res.json(shipment);
});

// =============================================
// クーポン管理API
// =============================================

// クーポン一覧取得
app.get('/api/coupons', (req, res) => {
  const coupons = readJSON(COUPONS_FILE);
  res.json(coupons);
});

// クーポン登録（管理者）
app.post('/api/coupons', (req, res) => {
  const coupons = readJSON(COUPONS_FILE);
  const coupon = {
    id: Date.now().toString(),
    accountId: req.body.accountId || '',
    password: req.body.password || '',
    couponUrl: req.body.couponUrl || '',
    shareholderNumber: req.body.shareholderNumber || '',
    status: '',           // '' = 未使用, 'in_use' = 使用中, 'used' = 使用済
    locationId: null,
    locationName: null,
    issuedAt: null,
    createdAt: new Date().toISOString()
  };
  coupons.push(coupon);
  writeJSON(COUPONS_FILE, coupons);
  res.json(coupon);
});

// クーポン更新（管理者）
app.put('/api/coupons/:id', (req, res) => {
  const coupons = readJSON(COUPONS_FILE);
  const idx = coupons.findIndex(c => c.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'クーポンが見つかりません' });
  // 編集可能フィールドのみ更新
  const allowed = ['accountId', 'password', 'couponUrl', 'shareholderNumber'];
  allowed.forEach(key => {
    if (req.body[key] !== undefined) coupons[idx][key] = req.body[key];
  });
  writeJSON(COUPONS_FILE, coupons);
  res.json(coupons[idx]);
});

// クーポン削除（管理者）
app.delete('/api/coupons/:id', (req, res) => {
  let coupons = readJSON(COUPONS_FILE);
  coupons = coupons.filter(c => c.id !== req.params.id);
  writeJSON(COUPONS_FILE, coupons);
  res.json({ success: true });
});

// クーポン発行（仕入担当者が拠点に対して新しいクーポンを割り当て）
app.post('/api/coupons/issue', (req, res) => {
  const { locationId, locationName } = req.body;
  if (!locationId) return res.status(400).json({ error: '拠点が指定されていません' });

  const coupons = readJSON(COUPONS_FILE);

  // 現在この拠点で「使用中」のクーポンを「使用済」に変更
  coupons.forEach(c => {
    if (c.locationId === locationId && c.status === 'in_use') {
      c.status = 'used';
    }
  });

  // 未使用のクーポンを1件割り当て（登録順＝先頭から）
  const unused = coupons.find(c => c.status === '');
  if (!unused) {
    writeJSON(COUPONS_FILE, coupons); // 使用済への変更は保存
    return res.status(404).json({ error: '未使用のクーポンがありません。管理者にクーポンの追加を依頼してください。' });
  }

  unused.status = 'in_use';
  unused.locationId = locationId;
  unused.locationName = locationName;
  unused.issuedAt = new Date().toISOString();

  writeJSON(COUPONS_FILE, coupons);
  res.json(unused);
});

// 拠点の現在のクーポン取得（仕入ページ用）
app.get('/api/coupons/location/:locationId', (req, res) => {
  const coupons = readJSON(COUPONS_FILE);
  // この拠点で「使用中」のクーポンを返す
  const current = coupons.find(c => c.locationId === req.params.locationId && c.status === 'in_use');
  res.json(current || null);
});

// =============================================
// サーバー起動
// =============================================
app.listen(PORT, () => {
  console.log(`Direct Sales server running at http://localhost:${PORT}`);
});
