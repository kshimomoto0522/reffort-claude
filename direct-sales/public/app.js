// =============================================
// Direct Sales - フロントエンドアプリケーション
// =============================================

// サイズ定義
const UNISEX_SIZES = [
  '4/22.5', '4.5/23', '5/23.5', '5.5/24', '6/24.5', '6.5/25',
  '7.5/25.5', '8/26', '8.5/26.5', '9/27', '9.5/27.5',
  '10/28', '11/28.5', '11.5/29', '12.5/30'
];
const WOMENS_SIZES = [
  '4.5/22', '5/22.5', '5.5/22.75', '6/23', '6.5/23.5', '7/24', '7.5/24.5', '8/25',
  '8.5/25.5', '9/25.75', '9.5/26', '10/26.5', '10.5/27', '11/27.5', '11.5/28', '12/28.5'
];

function getSizesForType(sizeType) {
  return sizeType === 'womens' ? WOMENS_SIZES : UNISEX_SIZES;
}
function sizeTypeLabel(sizeType) {
  return sizeType === 'womens' ? "Women's" : 'Unisex';
}

// グローバル状態
let currentRole = null;
let loginTarget = null; // ログイン後の遷移先
let products = [];
let cart = [];
let editingCart = false;
let selectedVariant = null;
let selectedProduct = null;
let currentBuyers = [];
let selectedBuyer = null;
let sizeSelections = {};
let currentSettings = null;
let currentExchangeRate = 150; // デフォルト値
let editingProductId = null; // 商品編集中のID
let pendingPurchaseLocId = null; // 仕入拠点選択時の拠点ID

// 管理者編集モード用
let adminEditMode = false;
let editKeys = [];    // [{type, id, sku, size}] — 各セルの識別情報
let editVals = [];    // [qty] — 現在の値
let origVals = [];    // [qty] — 元の値（差分計算用）
let editKeyMap = {};  // "type\0id\0sku\0size" → index（高速ルックアップ）
let editProductInfo = {}; // sku → {model, colorway, price, sizeType}

// =============================================
// 画面切り替え
// =============================================
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}
function showModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

// =============================================
// トップ画面
// =============================================
function goTop() {
  currentRole = null;
  loginTarget = null;
  stopOrderPolling();
  showScreen('screen-top');
}

// =============================================
// セラートップ（5メニュー表示）
// =============================================
function showSellerTop() {
  showScreen('screen-seller-top');
  startOrderPolling(); // 新規オーダー監視を開始
}

// =============================================
// 新規オーダー通知（30秒ごとにポーリング）
// =============================================
let orderPollTimer = null;
let lastOrderCheckTime = null; // 最後にチェックした時刻

function startOrderPolling() {
  if (orderPollTimer) return; // 既に動いていればスキップ
  lastOrderCheckTime = new Date().toISOString();
  orderPollTimer = setInterval(checkNewOrders, 30000); // 30秒間隔
}

function stopOrderPolling() {
  if (orderPollTimer) { clearInterval(orderPollTimer); orderPollTimer = null; }
}

async function checkNewOrders() {
  try {
    const res = await fetch(`/api/orders/check-new?since=${encodeURIComponent(lastOrderCheckTime)}`);
    const data = await res.json();
    if (data.newOrders > 0) {
      lastOrderCheckTime = new Date().toISOString();
      const pairs = data.latest.reduce((s, o) => s + (o.totalPairs || 0), 0);
      showToast(`🔔 新規オーダー ${data.newOrders}件（${pairs}足）`);
      // オーダー管理画面を表示中なら自動リロード
      const activeScreen = document.querySelector('.screen.active')?.id;
      if (activeScreen === 'screen-order-admin' && !adminEditMode) {
        const [ordersRes, purchasesRes] = await Promise.all([
          fetch('/api/orders'), fetch('/api/purchases')
        ]);
        cachedOrders = await ordersRes.json();
        cachedPurchases = await purchasesRes.json();
        renderOrderAdmin(cachedOrders, cachedPurchases, cachedEffectiveRate, cachedShipments);
      }
      // ブラウザ通知（許可されている場合）
      if (Notification.permission === 'granted') {
        new Notification('Reffort Direct', { body: `新規オーダー ${data.newOrders}件（${pairs}足）` });
      }
    }
  } catch (e) { /* ネットワークエラーは無視 */ }
}

// ブラウザ通知の許可リクエスト（セラーログイン時に1回）
function requestNotificationPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }
}

// パスワード不要のセクション
const NO_PASSWORD_ROLES = ['order', 'shipping', 'product', 'coupon'];

// セラーメニューからログイン画面へ
function showSellerLogin(target) {
  loginTarget = target;

  // 仕入は拠点選択画面を表示（パスワード不要だが拠点選択が必要）
  if (target === 'purchase') {
    showPurchaseLocations();
    return;
  }

  // パスワード不要のセクションはログイン画面をスキップ
  if (NO_PASSWORD_ROLES.includes(target)) {
    currentRole = target;
    autoLogin(target);
    return;
  }

  const titles = {
    settings: '詳細設定',
    finance: '収支管理'
  };
  currentRole = target;
  document.getElementById('login-title').textContent = titles[target] || 'Login';
  document.getElementById('login-password').value = '';
  document.getElementById('login-error').textContent = '';
  showScreen('screen-login');
  setTimeout(() => document.getElementById('login-password').focus(), 100);
}

// パスワード不要セクション用の自動ログイン
async function autoLogin(role) {
  try {
    const res = await fetch('/api/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role, password: '' })
    });
    if (!res.ok) return;
    const data = await res.json();
    loginTarget = role;
    // doLogin()と同じルーティング
    switch (role) {
      case 'order': startOrderPolling(); await showOrderAdmin(); break;
      case 'shipping': await showShipping(); break;
      case 'product': await showProductAdmin(); break;
      case 'coupon': await showCouponAdmin(); break;
      default: goTop();
    }
  } catch (e) { /* fallback: show login screen */ }
}

// 仕入拠点選択画面
async function showPurchaseLocations() {
  const res = await fetch('/api/settings');
  const settings = await res.json();
  const list = document.getElementById('purchase-location-list');
  list.innerHTML = '';
  if (settings.locations.length === 0) {
    list.innerHTML = '<p style="color:#888">拠点が登録されていません。詳細設定から追加してください。</p>';
  } else {
    settings.locations.forEach(loc => {
      const btn = document.createElement('button');
      btn.className = 'menu-btn';
      btn.textContent = loc.name;
      btn.onclick = async () => {
        currentRole = 'purchase';
        loginTarget = 'purchase';
        pendingPurchaseLocId = loc.id;
        // パスワード不要 — 拠点選択で直接ログイン
        try {
          const res = await fetch('/api/auth', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: 'purchase', password: '', locationId: loc.id })
          });
          if (!res.ok) return;
          const data = await res.json();
          showPurchasePage(data.locationId, data.locationName);
        } catch (e) { alert('通信エラー'); }
      };
      list.appendChild(btn);
    });
  }
  showScreen('screen-purchase-locations');
}

// バイヤー/セラーログイン表示
function showLogin(role) {
  currentRole = role;
  loginTarget = role;

  // パスワード不要のセクションはスキップ
  if (NO_PASSWORD_ROLES.includes(role)) {
    autoLogin(role);
    return;
  }

  document.getElementById('login-title').textContent =
    role === 'buyer' ? 'Buyer Login' : 'Seller Login';
  document.getElementById('login-password').value = '';
  document.getElementById('login-error').textContent = '';
  showScreen('screen-login');
  setTimeout(() => document.getElementById('login-password').focus(), 100);
}

// ログイン画面の「戻る」ボタン
function loginGoBack() {
  if (loginTarget === 'buyer' || loginTarget === 'seller-top') {
    goTop();
  } else if (loginTarget === 'purchase') {
    showPurchaseLocations();
  } else {
    showSellerTop();
  }
}

// =============================================
// ログイン処理
// =============================================
async function doLogin() {
  const password = document.getElementById('login-password').value;
  try {
    const res = await fetch('/api/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: currentRole, password, locationId: pendingPurchaseLocId || undefined })
    });
    if (!res.ok) {
      document.getElementById('login-error').textContent = 'パスワードが違います';
      return;
    }
    const data = await res.json();

    // ログイン成功後のルーティング
    switch (loginTarget) {
      case 'buyer':
        await loadProducts();
        // バイヤー一覧を取得してセレクターを準備
        try {
          const settingsRes = await fetch('/api/settings');
          const settings = await settingsRes.json();
          currentBuyers = settings.buyers || [];
          if (currentBuyers.length === 1) {
            selectedBuyer = currentBuyers[0];
          } else {
            selectedBuyer = null;
          }
        } catch(e) { currentBuyers = []; selectedBuyer = null; }
        showBuyerMenu();
        break;
      case 'seller-top':
        requestNotificationPermission();
        showSellerTop();
        break;
      case 'order':
        startOrderPolling();
        await showOrderAdmin();
        break;
      case 'product':
        await showProductAdmin();
        break;
      case 'settings':
        await showSettings();
        break;
      case 'finance':
        await showFinance();
        break;
      case 'shipping':
        await showShipping();
        break;
      case 'coupon':
        await showCouponAdmin();
        break;
      case 'purchase':
        showPurchasePage(data.locationId, data.locationName);
        break;
      default:
        goTop();
    }
  } catch (e) {
    document.getElementById('login-error').textContent = '接続エラー';
  }
}

// =============================================
// バイヤーメニュー
// =============================================
function onBuyerSelect() {
  const sel = document.getElementById('buyer-select');
  if (sel && sel.value) {
    selectedBuyer = currentBuyers.find(b => b.id === sel.value) || null;
  } else {
    selectedBuyer = null;
  }
}

function showBuyerMenu() {
  showScreen('screen-buyer-menu');
  // バイヤー選択セレクター表示
  const container = document.getElementById('buyer-selector');
  if (!container) return;
  if (currentBuyers.length <= 1) {
    container.style.display = 'none';
    return;
  }
  container.style.display = 'block';
  container.innerHTML = `
    <label style="font-size:13px;color:#666;">Who's ordering?</label>
    <select id="buyer-select" class="ship-carrier-select" style="width:100%;margin-top:4px;" onchange="onBuyerSelect()">
      <option value="">-- Select --</option>
      ${currentBuyers.map(b => `<option value="${b.id}" ${selectedBuyer && selectedBuyer.id === b.id ? 'selected' : ''}>${b.name}</option>`).join('')}
    </select>
  `;
}

// =============================================
// 商品一覧（バイヤー）
// =============================================
async function loadProducts() {
  const res = await fetch('/api/products');
  products = await res.json();
}

function showProducts() {
  showScreen('screen-products');
  renderProducts();
  updateCartBadge();
}

function renderProducts() {
  const grid = document.getElementById('product-list');
  grid.innerHTML = '';
  // displayOrderでソート
  const sorted = [...products].sort((a, b) => (a.displayOrder || 0) - (b.displayOrder || 0));
  sorted.forEach(p => {
    const prices = p.variants.map(v => v.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceText = minPrice === maxPrice ? `$${minPrice}` : `$${minPrice} - $${maxPrice}`;
    const card = document.createElement('div');
    card.className = 'product-card';
    card.onclick = () => showVariants(p);
    card.innerHTML = `
      <h3>${p.model}</h3>
      <div class="variant-count">${p.variants.length} colorway${p.variants.length > 1 ? 's' : ''}</div>
      <div class="price-range">${priceText}</div>
    `;
    grid.appendChild(card);
  });
}

// =============================================
// バリアント表示
// =============================================
function showVariants(product) {
  selectedProduct = product;
  document.getElementById('variant-model-name').textContent = product.model;
  const list = document.getElementById('variant-list');
  list.innerHTML = '';
  product.variants.forEach(v => {
    const imgHtml = v.image
      ? `<img src="${v.image}" alt="${v.colorway}" class="variant-thumb">`
      : `<div class="variant-thumb-placeholder">&#128095;</div>`;
    const item = document.createElement('div');
    item.className = 'variant-item';
    item.innerHTML = `
      <div class="variant-left">
        ${imgHtml}
        <div class="variant-info">
          <h4>${v.colorway}</h4>
          <div class="sku-label">${v.sku} &middot; ${sizeTypeLabel(v.sizeType)}</div>
          <div class="variant-price">$${v.price}</div>
        </div>
      </div>
      <button class="variant-add-btn" onclick="openSizeModal('${product.id}', '${v.sku}')">Add</button>
    `;
    list.appendChild(item);
  });
  showModal('modal-variants');
}
function closeVariants() { closeModal('modal-variants'); }

// =============================================
// サイズ選択
// =============================================
function openSizeModal(productId, sku) {
  const product = products.find(p => p.id === productId);
  const variant = product.variants.find(v => v.sku === sku);
  selectedVariant = variant;
  selectedProduct = product;
  sizeSelections = {};
  document.getElementById('size-modal-title').textContent = `${product.model} - ${variant.colorway}`;
  document.getElementById('size-modal-sku').textContent = `${variant.sku} · ${sizeTypeLabel(variant.sizeType)}`;
  document.getElementById('size-modal-price').textContent = `$${variant.price}`;

  // 除外サイズをフィルタ
  const allSizes = getSizesForType(variant.sizeType);
  const excluded = variant.excludedSizes || [];
  const available = allSizes.filter(s => !excluded.includes(s));
  renderSizeGrid(available);
  showModal('modal-sizes');
}

function renderSizeGrid(sizes) {
  const grid = document.getElementById('size-grid');
  grid.innerHTML = '';
  sizes.forEach(size => {
    const qty = sizeSelections[size] || 0;
    const item = document.createElement('div');
    item.className = 'size-item' + (qty > 0 ? ' has-qty' : '');
    item.innerHTML = `
      <div class="size-label">${size}</div>
      <div class="qty-controls">
        <button onclick="adjustSize('${size}', -1)">-</button>
        <span>${qty}</span>
        <button onclick="adjustSize('${size}', 1)">+</button>
      </div>
    `;
    grid.appendChild(item);
  });
}

function adjustSize(size, delta) {
  const current = sizeSelections[size] || 0;
  const newQty = Math.max(0, current + delta);
  if (newQty === 0) delete sizeSelections[size];
  else sizeSelections[size] = newQty;

  const allSizes = getSizesForType(selectedVariant.sizeType);
  const excluded = selectedVariant.excludedSizes || [];
  const available = allSizes.filter(s => !excluded.includes(s));
  renderSizeGrid(available);
}
function closeSizes() { closeModal('modal-sizes'); }

// =============================================
// カートに追加
// =============================================
function addToCart() {
  if (Object.keys(sizeSelections).length === 0) return;
  const existingIdx = cart.findIndex(item => item.sku === selectedVariant.sku);
  if (existingIdx >= 0) {
    const existing = cart[existingIdx];
    for (const [size, qty] of Object.entries(sizeSelections)) {
      existing.sizes[size] = (existing.sizes[size] || 0) + qty;
    }
  } else {
    cart.push({
      productId: selectedProduct.id,
      model: selectedProduct.model,
      colorway: selectedVariant.colorway,
      sku: selectedVariant.sku,
      price: selectedVariant.price,
      sizeType: selectedVariant.sizeType,
      image: selectedVariant.image || '',
      sizes: { ...sizeSelections }
    });
  }
  closeSizes();
  closeVariants();
  updateCartBadge();
  showToast();
}

function showToast(message) {
  const toast = document.getElementById('toast');
  if (message) toast.textContent = message;
  toast.classList.remove('show');
  void toast.offsetWidth;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 1500);
}

function updateCartBadge() {
  const totalPairs = cart.reduce((sum, item) =>
    sum + Object.values(item.sizes).reduce((s, q) => s + q, 0), 0);
  const badge = document.getElementById('cart-count');
  badge.textContent = totalPairs;
  badge.classList.toggle('hidden', totalPairs === 0);
  const badge2 = document.getElementById('cart-count-2');
  if (badge2) {
    badge2.textContent = totalPairs;
    badge2.classList.toggle('hidden', totalPairs === 0);
  }
}

// =============================================
// カート画面（テーブル形式）
// =============================================
function showCart() {
  editingCart = false;
  showScreen('screen-cart');
  renderCartTable();
}

function renderCartTable() {
  const content = document.getElementById('cart-content');
  const actions = document.getElementById('cart-actions');
  const editBtn = document.getElementById('btn-edit');
  content.innerHTML = '';

  if (cart.length === 0) {
    content.innerHTML = '<div class="empty-msg">Your cart is empty.</div>';
    actions.style.display = 'none';
    return;
  }

  actions.style.display = 'flex';
  editBtn.textContent = editingCart ? 'Done' : 'Edit';

  const unisexItems = cart.filter(i => i.sizeType !== 'womens');
  const womensItems = cart.filter(i => i.sizeType === 'womens');

  const wrapper = document.createElement('div');
  wrapper.className = 'order-table-wrapper';

  let totalPairs = 0;
  let totalAmount = 0;

  if (unisexItems.length > 0) {
    const { table, pairs, amount } = buildEditableTable(unisexItems, UNISEX_SIZES, 'SIZE (UNISEX)', editingCart, 'cart');
    wrapper.appendChild(table);
    totalPairs += pairs;
    totalAmount += amount;
  }
  if (womensItems.length > 0) {
    const { table, pairs, amount } = buildEditableTable(womensItems, WOMENS_SIZES, "SIZE (WOMEN'S)", editingCart, 'cart');
    wrapper.appendChild(table);
    totalPairs += pairs;
    totalAmount += amount;
  }

  const totalDiv = document.createElement('div');
  totalDiv.className = 'order-table-total';
  totalDiv.innerHTML = `${totalPairs} pairs &middot; $${totalAmount.toLocaleString()}`;
  wrapper.appendChild(totalDiv);

  content.appendChild(wrapper);
}

function toggleEditCart() {
  editingCart = !editingCart;
  renderCartTable();
}

function cartCellAdjust(sku, size, delta) {
  const item = cart.find(i => i.sku === sku);
  if (!item) return;
  const newQty = (item.sizes[size] || 0) + delta;
  if (newQty <= 0) delete item.sizes[size];
  else item.sizes[size] = newQty;
  if (Object.keys(item.sizes).length === 0) {
    cart.splice(cart.indexOf(item), 1);
  }
  updateCartBadge();
  renderCartTable();
}

// =============================================
// 注文を送信
// =============================================
async function placeOrder() {
  if (cart.length === 0) return;
  const items = [];
  let totalPairs = 0;
  let totalAmount = 0;
  cart.forEach(item => {
    Object.entries(item.sizes).forEach(([size, qty]) => {
      items.push({
        productId: item.productId,
        model: item.model,
        colorway: item.colorway,
        sku: item.sku,
        size, quantity: qty,
        price: item.price,
        sizeType: item.sizeType
      });
      totalPairs += qty;
      totalAmount += qty * item.price;
    });
  });
  try {
    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        items, totalPairs, totalAmount,
        buyerId: selectedBuyer ? selectedBuyer.id : null,
        buyerName: selectedBuyer ? selectedBuyer.name : null
      })
    });
    if (!res.ok) throw new Error('Order failed');
    cart = [];
    updateCartBadge();
    showModal('modal-order-done');
  } catch (e) {
    alert('Failed to place order. Please try again.');
  }
}

function closeOrderDone() {
  closeModal('modal-order-done');
  showBuyerMenu();
}

// =============================================
// 注文履歴（バイヤー）
// =============================================
async function showOrderHistory() {
  showScreen('screen-order-history');
  showHistoryTab('current');
}

async function showHistoryTab(tab) {
  document.getElementById('tab-current').classList.toggle('active', tab === 'current');
  document.getElementById('tab-past').classList.toggle('active', tab === 'past');

  // オーダーと発送データを両方取得
  const [ordersRes, shipmentsRes] = await Promise.all([
    fetch('/api/orders'), fetch('/api/shipments')
  ]);
  const orders = await ordersRes.json();
  const shipments = await shipmentsRes.json();
  const container = document.getElementById('history-content');
  container.innerHTML = '';

  // 発送済アイテムをグルーピング（発送完了分のみ — 発送待ちは除外）
  const completedShipments = shipments.filter(s => !s.pendingShipment);
  const allShippedItems = [];
  completedShipments.forEach(s => s.items.forEach(i => allShippedItems.push(i)));
  const shippedGrouped = groupShippedItems(allShippedItems);

  // 商品マスタからmodel/colorway補完用マップ
  const productInfoMap = {};
  (products || []).forEach(p => {
    (p.variants || []).forEach(v => {
      productInfoMap[v.sku] = { model: p.model, colorway: v.colorway, price: v.price, sizeType: v.sizeType };
    });
  });

  if (tab === 'current') {
    // 全オーダーのアイテムを集計
    const pendingOrders = orders.filter(o => o.status === 'pending');
    if (pendingOrders.length === 0) {
      container.innerHTML = '<div class="no-orders">No current orders.</div>';
      return;
    }
    const allItems = [];
    pendingOrders.forEach(order => {
      order.items.forEach(item => allItems.push(item));
    });
    const grouped = groupItemsBySku(allItems);

    // 発送済を差し引いた残りを表示（バイヤー側はマイナスを除外）
    const currentItemsRaw = calcRemaining(grouped, shippedGrouped);
    // マイナス値を除外（発送超過分はバイヤーに見せない）
    const currentItems = currentItemsRaw.map(item => {
      const cleaned = { ...item, sizes: {} };
      Object.entries(item.sizes).forEach(([size, qty]) => {
        if (qty > 0) cleaned.sizes[size] = qty;
      });
      return cleaned;
    }).filter(item => Object.keys(item.sizes).length > 0);

    if (currentItems.length === 0) {
      container.innerHTML = '<div class="no-orders">All orders have been shipped.</div>';
      return;
    }

    // priceを補完（calcRemainingで消えるので）
    currentItems.forEach(item => {
      if (!item.price && productInfoMap[item.sku]) item.price = productInfoMap[item.sku].price;
      if (!item.price) {
        const orig = grouped.find(g => g.sku === item.sku);
        if (orig) item.price = orig.price;
      }
    });

    const sortedCurrentItems = sortItemsBySkuOrder(currentItems);
    const unisexItems = sortedCurrentItems.filter(g => g.sizeType !== 'womens');
    const womensItems = sortedCurrentItems.filter(g => g.sizeType === 'womens');

    let totalPairs = 0;
    let totalAmount = 0;

    const latestDate = new Date(Math.max(...pendingOrders.map(o => new Date(o.createdAt))));
    const latestDateStr = latestDate.toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric'
    });

    const wrapper = document.createElement('div');
    wrapper.className = 'order-table-wrapper';
    wrapper.innerHTML = `<div class="order-table-header">
      <h4>Latest order: ${latestDateStr}</h4>
    </div>`;

    if (unisexItems.length > 0) {
      const { table, pairs, amount } = buildEditableTable(unisexItems, UNISEX_SIZES, 'SIZE (UNISEX)', false, 'history');
      wrapper.appendChild(table);
      totalPairs += pairs;
      totalAmount += amount;
    }
    if (womensItems.length > 0) {
      const { table, pairs, amount } = buildEditableTable(womensItems, WOMENS_SIZES, "SIZE (WOMEN'S)", false, 'history');
      wrapper.appendChild(table);
      totalPairs += pairs;
      totalAmount += amount;
    }

    const totalDiv = document.createElement('div');
    totalDiv.className = 'order-table-total';
    totalDiv.innerHTML = `${totalPairs} pairs &middot; $${totalAmount.toLocaleString()}`;
    wrapper.appendChild(totalDiv);
    container.appendChild(wrapper);

    // === Order Log: 注文日ごとの一覧表 ===
    // 日付でグルーピング（JST基準）
    const dateGroups = {};
    pendingOrders.forEach(order => {
      const dateJST = new Date(new Date(order.createdAt).getTime() + 9 * 60 * 60 * 1000);
      const dateKey = dateJST.toISOString().split('T')[0]; // YYYY-MM-DD
      if (!dateGroups[dateKey]) dateGroups[dateKey] = [];
      dateGroups[dateKey].push(order);
    });
    // 日付キーを新しい順にソート
    const sortedDateKeys = Object.keys(dateGroups).sort((a, b) => b.localeCompare(a));

    // 年・月の選択肢を収集
    const yearSet = new Set();
    const monthSetByYear = {}; // { "2026": Set(["04","03",...]) }
    sortedDateKeys.forEach(dk => {
      const y = dk.substring(0, 4);
      const m = dk.substring(5, 7);
      yearSet.add(y);
      if (!monthSetByYear[y]) monthSetByYear[y] = new Set();
      monthSetByYear[y].add(m);
    });
    const yearOptions = [...yearSet].sort((a, b) => b.localeCompare(a));

    // 年フィルターHTML
    let yearFilterHtml = '';
    yearOptions.forEach(y => {
      yearFilterHtml += `<option value="${y}">${y}</option>`;
    });
    // 月フィルターHTML（初期表示は最新年の月）
    const initialYear = yearOptions[0];
    let monthFilterHtml = '<option value="all">All</option>';
    if (initialYear && monthSetByYear[initialYear]) {
      [...monthSetByYear[initialYear]].sort((a, b) => b.localeCompare(a)).forEach(m => {
        const label = new Date(initialYear, parseInt(m) - 1).toLocaleDateString('en-US', { month: 'long' });
        monthFilterHtml += `<option value="${m}">${label}</option>`;
      });
    }

    // Order Logヘッダー + 年・月フィルター
    const logSection = document.createElement('div');
    logSection.className = 'order-log-section';
    // 年月データをグローバルに保持（月フィルター更新用）
    window._orderLogMonthsByYear = monthSetByYear;
    logSection.innerHTML = `
      <div class="order-log-header">
        <h3>Order Log</h3>
        <div class="order-log-filters">
          <select id="order-log-year" onchange="updateOrderLogMonthFilter()">${yearFilterHtml}</select>
          <select id="order-log-month" onchange="filterOrderLog()">${monthFilterHtml}</select>
        </div>
      </div>`;
    container.appendChild(logSection);

    // 各日付のテーブルを生成
    const logBody = document.createElement('div');
    logBody.id = 'order-log-body';
    sortedDateKeys.forEach(dateKey => {
      const groupOrders = dateGroups[dateKey];
      // 日付表示
      const [y, m, d] = dateKey.split('-');
      const displayDate = new Date(y, parseInt(m) - 1, parseInt(d)).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric'
      });
      // この日のアイテムをSKUでグルーピング
      const dayItems = [];
      groupOrders.forEach(o => o.items.forEach(i => dayItems.push(i)));
      const dayGrouped = groupItemsBySku(dayItems);
      // price補完
      dayGrouped.forEach(item => {
        if (!item.price && productInfoMap[item.sku]) item.price = productInfoMap[item.sku].price;
      });
      const sorted = sortItemsBySkuOrder(dayGrouped);
      const uItems = sorted.filter(g => g.sizeType !== 'womens');
      const wItems = sorted.filter(g => g.sizeType === 'womens');

      let dayPairs = 0, dayAmount = 0;
      const dayWrapper = document.createElement('div');
      dayWrapper.className = 'order-table-wrapper order-log-day';
      dayWrapper.dataset.month = dateKey.substring(0, 7);
      dayWrapper.innerHTML = `<div class="order-table-header"><h4>${displayDate}</h4></div>`;

      if (uItems.length > 0) {
        const { table, pairs, amount } = buildEditableTable(uItems, UNISEX_SIZES, 'SIZE (UNISEX)', false, 'history');
        dayWrapper.appendChild(table);
        dayPairs += pairs; dayAmount += amount;
      }
      if (wItems.length > 0) {
        const { table, pairs, amount } = buildEditableTable(wItems, WOMENS_SIZES, "SIZE (WOMEN'S)", false, 'history');
        dayWrapper.appendChild(table);
        dayPairs += pairs; dayAmount += amount;
      }
      const dayTotal = document.createElement('div');
      dayTotal.className = 'order-table-total';
      dayTotal.innerHTML = `${dayPairs} pairs &middot; $${dayAmount.toLocaleString()}`;
      dayWrapper.appendChild(dayTotal);
      logBody.appendChild(dayWrapper);
    });
    container.appendChild(logBody);

  } else {
    // Past Orders = 発送完了データから表示（発送待ちは除外）
    const pastShipments = shipments.filter(s => !s.pendingShipment);
    if (pastShipments.length === 0) {
      container.innerHTML = '<div class="no-orders">No past orders.</div>';
      return;
    }

    // 発送ごとに表示（新しい順）
    [...pastShipments].reverse().forEach(s => {
      const dateJST = new Date(new Date(s.createdAt).getTime() + 9 * 60 * 60 * 1000);
      const dateStr = dateJST.toISOString().split('T')[0];
      const totalPairsShip = s.items.reduce((sum, i) => sum + i.quantity, 0);

      // アイテムをSKUでグルーピング（model/colorway補完）
      const itemGrouped = {};
      s.items.forEach(i => {
        if (!itemGrouped[i.sku]) {
          const info = productInfoMap[i.sku] || {};
          itemGrouped[i.sku] = {
            model: i.model || info.model || '',
            colorway: i.colorway || info.colorway || '',
            sku: i.sku,
            price: info.price || 0,
            sizeType: i.sizeType || info.sizeType || 'unisex',
            sizes: {}
          };
        }
        itemGrouped[i.sku].sizes[i.size] = (itemGrouped[i.sku].sizes[i.size] || 0) + i.quantity;
      });
      const grouped = sortItemsBySkuOrder(Object.values(itemGrouped));
      const unisexItems = grouped.filter(g => g.sizeType !== 'womens');
      const womensItems = grouped.filter(g => g.sizeType === 'womens');

      let totalPairs = 0;
      let totalAmount = 0;

      const wrapper = document.createElement('div');
      wrapper.className = 'order-table-wrapper';

      // 追跡番号（横並び表示）
      const trackingHtml = buildTrackingDisplay(s.tracking || []);

      const paidStatus = s.paid
        ? '<span class="paid-badge">Paid</span>'
        : '<span class="unpaid-badge">Unpaid</span>';
      wrapper.innerHTML = `<div class="order-table-header">
        <h4>Shipped: ${dateStr} ${paidStatus}</h4>
      </div>
      ${trackingHtml ? `<div class="tracking-info-inline">${trackingHtml}</div>` : ''}`;

      if (unisexItems.length > 0) {
        const { table, pairs, amount } = buildEditableTable(unisexItems, UNISEX_SIZES, 'SIZE (UNISEX)', false, 'history');
        wrapper.appendChild(table);
        totalPairs += pairs;
        totalAmount += amount;
      }
      if (womensItems.length > 0) {
        const { table, pairs, amount } = buildEditableTable(womensItems, WOMENS_SIZES, "SIZE (WOMEN'S)", false, 'history');
        wrapper.appendChild(table);
        totalPairs += pairs;
        totalAmount += amount;
      }

      const totalDiv = document.createElement('div');
      totalDiv.className = 'order-table-total';
      totalDiv.innerHTML = `${totalPairs} pairs &middot; $${totalAmount.toLocaleString()}`;
      wrapper.appendChild(totalDiv);
      container.appendChild(wrapper);
    });
  }
}

// =============================================
// 追跡番号表示（同一キャリアごとに横並び）
// =============================================
function buildTrackingDisplay(tracking) {
  if (!tracking || tracking.length === 0) return '';
  // キャリアごとにグルーピング
  const byCarrier = {};
  tracking.forEach(t => {
    const c = t.carrier || 'Other';
    if (!byCarrier[c]) byCarrier[c] = [];
    byCarrier[c].push(t.trackingNumber);
  });
  // キャリアごとに1行で表示
  function getTrackUrl(carrier, num) {
    const c = carrier.toUpperCase();
    if (c.includes('DHL')) return `https://www.dhl.com/us-en/home/tracking/tracking-express.html?submit=1&tracking-id=${num}`;
    if (c.includes('FEDEX')) return `https://www.fedex.com/fedextrack/?trknbr=${num}`;
    if (c.includes('UPS')) return `https://www.ups.com/track?tracknum=${num}`;
    return null;
  }
  return Object.entries(byCarrier).map(([carrier, nums]) => {
    const links = nums.map(num => {
      const url = getTrackUrl(carrier, num);
      return url ? `<a href="${url}" target="_blank" class="tracking-link">${num}</a>` : `<span>${num}</span>`;
    }).join('&nbsp;&nbsp;');
    return `<span class="tracking-inline">${carrier}: ${links}</span>`;
  }).join('&nbsp;&nbsp;|&nbsp;&nbsp;');
}

// =============================================
// Order Log 年月フィルター
// =============================================
function filterOrderLog() {
  const year = document.getElementById('order-log-year').value;
  const month = document.getElementById('order-log-month').value;
  document.querySelectorAll('.order-log-day').forEach(el => {
    const elMonth = el.dataset.month; // "YYYY-MM"
    const elYear = elMonth.substring(0, 4);
    const elMo = elMonth.substring(5, 7);
    const yearMatch = elYear === year;
    const monthMatch = month === 'all' || elMo === month;
    el.style.display = (yearMatch && monthMatch) ? '' : 'none';
  });
}

// 年フィルター変更時に月フィルターを更新
function updateOrderLogMonthFilter() {
  const year = document.getElementById('order-log-year').value;
  const monthSelect = document.getElementById('order-log-month');
  const months = window._orderLogMonthsByYear[year] || new Set();
  let html = '<option value="all">All</option>';
  [...months].sort((a, b) => b.localeCompare(a)).forEach(m => {
    const label = new Date(year, parseInt(m) - 1).toLocaleDateString('en-US', { month: 'long' });
    html += `<option value="${m}">${label}</option>`;
  });
  monthSelect.innerHTML = html;
  filterOrderLog();
}

// =============================================
// ヘルパー：アイテムをSKUでグルーピング
// =============================================
function groupItemsBySku(items) {
  const map = {};
  items.forEach(item => {
    const key = item.sku;
    if (!map[key]) {
      map[key] = {
        model: item.model,
        colorway: item.colorway,
        sku: item.sku,
        price: item.price,
        sizeType: item.sizeType || 'unisex',
        sizes: {}
      };
    }
    map[key].sizes[item.size] = (map[key].sizes[item.size] || 0) + item.quantity;
  });
  return Object.values(map);
}

// =============================================
// 共通テーブル生成（Cart / Order History用）
// =============================================
function buildEditableTable(items, allSizes, sizeLabel, editing, mode) {
  let totalPairs = 0;
  let totalAmount = 0;

  const div = document.createElement('div');
  div.className = 'order-spreadsheet';

  let html = '<div class="spreadsheet-scroll"><table>';

  html += `<thead><tr>
    <th class="col-no">No</th>
    <th class="col-product">Products</th>
    <th class="col-color">Color</th>
    <th class="col-sku">Style Code</th>
    <th class="col-qty">QTY</th>
    <th class="col-price">Unit Price</th>
    <th class="col-amount">Amount</th>
    <th class="col-size-group" colspan="${allSizes.length}">${sizeLabel}</th>
  </tr>`;

  html += `<tr>
    <th class="col-no"></th>
    <th class="col-product"></th>
    <th class="col-color"></th>
    <th class="col-sku"></th>
    <th class="col-qty"></th>
    <th class="col-price"></th>
    <th class="col-amount"></th>`;
  allSizes.forEach(s => {
    html += `<th class="col-size">${s}</th>`;
  });
  html += '</tr></thead><tbody>';

  items.forEach((item, idx) => {
    const pairs = Object.values(item.sizes).reduce((s, q) => s + q, 0);
    const amount = pairs * item.price;
    totalPairs += pairs;
    totalAmount += amount;

    html += `<tr>
      <td class="col-no">${idx + 1}</td>
      <td class="col-product">${item.model}</td>
      <td class="col-color">${item.colorway}</td>
      <td class="col-sku">${item.sku}</td>
      <td class="col-qty">${pairs}</td>
      <td class="col-price">$${item.price}</td>
      <td class="col-amount">$${amount.toLocaleString()}</td>`;

    allSizes.forEach(s => {
      const qty = item.sizes[s] || 0;
      if (editing && mode === 'cart') {
        html += `<td class="col-size editing">
          <div class="cell-edit">
            <button onclick="cartCellAdjust('${item.sku}','${s}',-1)">-</button>
            <span>${qty}</span>
            <button onclick="cartCellAdjust('${item.sku}','${s}',1)">+</button>
          </div>
        </td>`;
      } else {
        html += `<td class="col-size ${qty ? 'has-value' : ''}">${qty || ''}</td>`;
      }
    });

    html += '</tr>';
  });

  html += '</tbody></table></div>';
  div.innerHTML = html;

  return { table: div, pairs: totalPairs, amount: totalAmount };
}

// =============================================
// =============================================
// セラー側：詳細設定
// =============================================
// =============================================
async function showSettings() {
  showScreen('screen-settings');
  const res = await fetch('/api/settings');
  currentSettings = await res.json();

  document.getElementById('set-customs-unit').value = currentSettings.customsUnitPrice || '';
  document.getElementById('set-shipping').value = currentSettings.shippingPerPair || '';
  document.getElementById('set-coupon').value = currentSettings.couponPerPair || '';

  updateCustomsCalc();
  renderLocations();
  renderBuyers();
  await loadSectionPasswords();

  // 為替レートを取得して利益計算に使う
  await fetchExchangeRate();

  // 関税リアルタイム計算
  document.getElementById('set-customs-unit').addEventListener('input', updateCustomsCalc);
}

// ページ別パスワードを読み込んでフォームに表示
async function loadSectionPasswords() {
  try {
    const res = await fetch('/api/section-passwords');
    const pws = await res.json();
    const map = {
      'pw-buyer': 'buyer',
      'pw-seller-top': 'seller-top',
      'pw-settings': 'settings',
      'pw-finance': 'finance'
    };
    Object.entries(map).forEach(([elId, key]) => {
      const el = document.getElementById(elId);
      if (el) el.value = pws[key] || '';
    });
  } catch (e) {
    console.error('パスワード読み込み失敗:', e);
  }
}

// ページ別パスワードを保存
async function saveSectionPasswords() {
  const data = {
    buyer: document.getElementById('pw-buyer').value.trim() || '0000',
    'seller-top': document.getElementById('pw-seller-top').value.trim() || '0000',
    settings: document.getElementById('pw-settings').value.trim() || '0000',
    finance: document.getElementById('pw-finance').value.trim() || '0000'
  };
  try {
    await fetch('/api/section-passwords', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    alert('ページ別パスワードを保存しました');
  } catch (e) {
    alert('保存に失敗しました');
  }
}

function updateCustomsCalc() {
  const unit = parseFloat(document.getElementById('set-customs-unit').value) || 0;
  const customs = Math.round(unit * 0.155);
  document.getElementById('customs-calc').textContent = `→ 関税: ¥${customs.toLocaleString()} / 足`;
}

async function saveSettings() {
  const data = {
    customsUnitPrice: parseFloat(document.getElementById('set-customs-unit').value) || 0,
    shippingPerPair: parseFloat(document.getElementById('set-shipping').value) || 0,
    couponPerPair: parseFloat(document.getElementById('set-coupon').value) || 0
  };
  await fetch('/api/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  currentSettings = { ...currentSettings, ...data };
  alert('保存しました');
}

// 利益計算ツール
async function calcProfit() {
  const purchase = parseFloat(document.getElementById('calc-purchase').value) || 0;
  const sellPrice = parseFloat(document.getElementById('calc-sell-price').value) || 0;

  if (purchase === 0 && sellPrice === 0) {
    document.getElementById('calc-result').style.display = 'none';
    return;
  }

  document.getElementById('calc-result').style.display = 'block';

  const rate = currentExchangeRate - 1; // マイナス1円
  const coupon = currentSettings ? (currentSettings.couponPerPair || 0) : 0;
  const customsUnit = currentSettings ? (currentSettings.customsUnitPrice || 0) : 0;
  const shipping = currentSettings ? (currentSettings.shippingPerPair || 0) : 0;

  const A = purchase;            // 仕入値
  const B = coupon;              // クーポン
  const C = A + B;               // 仕入合計
  const D = Math.round(customsUnit * 0.155); // 関税
  const E = shipping;            // 送料
  const F = Math.round(sellPrice * rate);  // 売上（円）
  const G = F - C - D - E;       // 利益
  const margin = F > 0 ? ((G / F) * 100).toFixed(2) : 0;

  document.getElementById('calc-rate').textContent = `¥${rate.toFixed(1)} / USD`;
  document.getElementById('calc-a').textContent = `¥${A.toLocaleString()}`;
  document.getElementById('calc-b').textContent = `¥${B.toLocaleString()}`;
  document.getElementById('calc-c').textContent = `¥${C.toLocaleString()}`;
  document.getElementById('calc-d').textContent = `¥${D.toLocaleString()}`;
  document.getElementById('calc-e').textContent = `¥${E.toLocaleString()}`;
  document.getElementById('calc-f').textContent = `¥${F.toLocaleString()}`;
  document.getElementById('calc-g').textContent = `¥${G.toLocaleString()}`;
  document.getElementById('calc-margin').textContent = `${margin}%`;
}

// 拠点管理
function renderLocations() {
  const list = document.getElementById('location-list');
  list.innerHTML = '';
  if (!currentSettings || !currentSettings.locations) return;
  currentSettings.locations.forEach(loc => {
    const item = document.createElement('div');
    item.className = 'location-item';
    item.innerHTML = `
      <div>
        <div class="loc-info">${loc.name}</div>
      </div>
      <div class="loc-actions">
        <button class="small-btn" onclick="editLocation('${loc.id}')">編集</button>
        <button class="danger-btn" onclick="deleteLocation('${loc.id}')">削除</button>
      </div>
    `;
    list.appendChild(item);
  });
}

async function addLocation() {
  const name = document.getElementById('loc-name').value.trim();
  if (!name) { alert('拠点名を入力してください'); return; }
  const res = await fetch('/api/settings/locations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });
  const loc = await res.json();
  currentSettings.locations.push(loc);
  document.getElementById('loc-name').value = '';
  renderLocations();
}

function editLocation(id) {
  const loc = currentSettings.locations.find(l => l.id === id);
  if (!loc) return;
  const newName = prompt('拠点名', loc.name);
  if (newName === null) return;
  fetch(`/api/settings/locations/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: newName })
  }).then(() => {
    loc.name = newName;
    renderLocations();
  });
}

async function deleteLocation(id) {
  if (!confirm('この拠点を削除しますか？')) return;
  await fetch(`/api/settings/locations/${id}`, { method: 'DELETE' });
  currentSettings.locations = currentSettings.locations.filter(l => l.id !== id);
  renderLocations();
}

// バイヤー管理
function renderBuyers() {
  const list = document.getElementById('buyer-list');
  if (!list) return;
  const buyers = currentSettings.buyers || [];
  if (buyers.length === 0) {
    list.innerHTML = '<div class="no-orders" style="padding:12px">バイヤーが登録されていません</div>';
    return;
  }
  list.innerHTML = buyers.map(b => `
    <div class="location-item">
      <div class="location-info">
        <span class="location-name">${b.name}</span>
        <span class="location-pass">${b.phone}</span>
      </div>
      <div class="location-actions">
        <button class="secondary-btn" onclick="editBuyer('${b.id}')">編集</button>
        <button class="danger-btn-sm" onclick="deleteBuyer('${b.id}')">削除</button>
      </div>
    </div>
  `).join('');
}

async function addBuyer() {
  const name = document.getElementById('buyer-name').value.trim();
  const phone = document.getElementById('buyer-phone').value.trim();
  if (!name || !phone) { alert('名前とWhatsApp番号を入力してください'); return; }
  const res = await fetch('/api/settings/buyers', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, phone })
  });
  const buyer = await res.json();
  if (!currentSettings.buyers) currentSettings.buyers = [];
  currentSettings.buyers.push(buyer);
  document.getElementById('buyer-name').value = '';
  document.getElementById('buyer-phone').value = '';
  renderBuyers();
}

function editBuyer(id) {
  const buyers = currentSettings.buyers || [];
  const buyer = buyers.find(b => b.id === id);
  if (!buyer) return;
  const newName = prompt('名前', buyer.name);
  if (newName === null) return;
  const newPhone = prompt('WhatsApp番号', buyer.phone);
  if (newPhone === null) return;
  fetch(`/api/settings/buyers/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: newName, phone: newPhone })
  }).then(() => {
    buyer.name = newName;
    buyer.phone = newPhone;
    renderBuyers();
  });
}

async function deleteBuyer(id) {
  if (!confirm('このバイヤーを削除しますか？')) return;
  await fetch(`/api/settings/buyers/${id}`, { method: 'DELETE' });
  currentSettings.buyers = (currentSettings.buyers || []).filter(b => b.id !== id);
  renderBuyers();
}

// =============================================
// =============================================
// セラー側：商品登録
// =============================================
// =============================================
async function showProductAdmin() {
  showScreen('screen-product-admin');
  await loadProducts();
  renderAdminProducts();
}

function renderAdminProducts() {
  const list = document.getElementById('admin-product-list');
  list.innerHTML = '';
  const sorted = [...products].sort((a, b) => (a.displayOrder || 0) - (b.displayOrder || 0));
  sorted.forEach((p, idx) => {
    const card = document.createElement('div');
    card.className = 'admin-product-card';

    let variantsHtml = '';
    p.variants.forEach(v => {
      const purchaseStr = v.purchasePrice ? `¥${v.purchasePrice.toLocaleString()}` : '未設定';
      variantsHtml += `
        <div class="admin-variant-row">
          <span class="av-color">${v.colorway}</span>
          <span class="av-sku">${v.sku}</span>
          <span class="av-type">${sizeTypeLabel(v.sizeType)}</span>
          <span class="av-price">$${v.price}</span>
          <span class="av-purchase">仕入: ${purchaseStr}</span>
        </div>
      `;
    });

    card.innerHTML = `
      <div class="admin-product-header">
        <h3>${p.model}</h3>
        <div class="admin-product-actions">
          <button class="move-btn" onclick="moveProduct('${p.id}', -1)" ${idx === 0 ? 'disabled' : ''}>▲</button>
          <button class="move-btn" onclick="moveProduct('${p.id}', 1)" ${idx === sorted.length - 1 ? 'disabled' : ''}>▼</button>
          <button class="small-btn" onclick="editProduct('${p.id}')">編集</button>
          <button class="danger-btn" onclick="deleteProduct('${p.id}')">削除</button>
        </div>
      </div>
      ${variantsHtml}
    `;
    list.appendChild(card);
  });
}

// 商品の並び替え
async function moveProduct(id, direction) {
  const sorted = [...products].sort((a, b) => (a.displayOrder || 0) - (b.displayOrder || 0));
  const idx = sorted.findIndex(p => p.id === id);
  const newIdx = idx + direction;
  if (newIdx < 0 || newIdx >= sorted.length) return;
  [sorted[idx], sorted[newIdx]] = [sorted[newIdx], sorted[idx]];
  const orderedIds = sorted.map(p => p.id);
  const res = await fetch('/api/products-order', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ orderedIds })
  });
  products = await res.json();
  renderAdminProducts();
}

// 商品削除
async function deleteProduct(id) {
  const p = products.find(x => x.id === id);
  if (!confirm(`「${p.model}」を削除しますか？`)) return;
  await fetch(`/api/products/${id}`, { method: 'DELETE' });
  products = products.filter(x => x.id !== id);
  renderAdminProducts();
}

// 商品登録/編集フォーム表示
function showProductForm(productId) {
  editingProductId = productId || null;
  document.getElementById('product-form-title').textContent = productId ? '商品を編集' : '商品を登録';
  document.getElementById('pf-model').value = '';
  document.getElementById('pf-variants').innerHTML = '';

  if (productId) {
    const p = products.find(x => x.id === productId);
    if (!p) return;
    document.getElementById('pf-model').value = p.model;
    p.variants.forEach(v => addVariantRow(v));
  } else {
    addVariantRow();
  }
  showModal('modal-product-form');
}

function editProduct(id) {
  showProductForm(id);
}

function closeProductForm() {
  closeModal('modal-product-form');
}

// バリアント行を追加
let variantCounter = 0;
function addVariantRow(data) {
  variantCounter++;
  const id = variantCounter;
  const container = document.getElementById('pf-variants');
  const row = document.createElement('div');
  row.className = 'variant-form-row';
  row.id = `vf-row-${id}`;

  const sizeType = data ? data.sizeType : 'unisex';
  const allSizes = sizeType === 'womens' ? WOMENS_SIZES : UNISEX_SIZES;
  const excluded = data ? (data.excludedSizes || []) : [];

  let sizeExcludeHtml = allSizes.map(s => {
    const isExcluded = excluded.includes(s);
    return `<span class="size-exclude-item ${isExcluded ? 'excluded' : ''}"
      onclick="toggleSizeExclude(this, '${s}', ${id})" data-size="${s}">${s}</span>`;
  }).join('');

  row.innerHTML = `
    <div class="vf-header">
      <h4>カラー #${id}</h4>
      <button class="danger-btn" onclick="removeVariantRow(${id})">削除</button>
    </div>
    <div class="vf-grid">
      <div class="form-row">
        <label>カラー名</label>
        <input type="text" class="vf-colorway" value="${data ? data.colorway : ''}" placeholder="例: Panda">
      </div>
      <div class="form-row">
        <label>型番 (Style Code)</label>
        <input type="text" class="vf-sku" value="${data ? data.sku : ''}" placeholder="例: DD1391-100">
      </div>
      <div class="form-row">
        <label>性別</label>
        <select class="vf-sizetype" onchange="updateSizeExcludeGrid(${id}, this.value)">
          <option value="unisex" ${sizeType === 'unisex' ? 'selected' : ''}>Unisex</option>
          <option value="womens" ${sizeType === 'womens' ? 'selected' : ''}>Women's</option>
        </select>
      </div>
      <div class="form-row">
        <label>販売価格 (USD)</label>
        <input type="number" class="vf-price" value="${data ? data.price : ''}" placeholder="130">
      </div>
      <div class="form-row">
        <label>画像URL</label>
        <input type="text" class="vf-image" value="${data ? (data.image || '') : ''}" placeholder="https://...">
      </div>
      <div class="form-row">
        <label>仕入先URL</label>
        <input type="text" class="vf-supplier-url" value="${data ? (data.supplierUrl || '') : ''}" placeholder="https://...">
      </div>
      <div class="form-row">
        <label>仕入値（円）</label>
        <input type="number" class="vf-purchase-price" value="${data ? (data.purchasePrice || '') : ''}" placeholder="11550">
      </div>
      <div class="form-row vf-full">
        <label>サイズ（クリックで除外/復活）</label>
        <div class="size-exclude-grid" id="vf-sizes-${id}">${sizeExcludeHtml}</div>
      </div>
    </div>
  `;
  container.appendChild(row);
}

function removeVariantRow(id) {
  const row = document.getElementById(`vf-row-${id}`);
  if (row) row.remove();
}

function toggleSizeExclude(el, size, rowId) {
  el.classList.toggle('excluded');
}

function updateSizeExcludeGrid(rowId, sizeType) {
  const allSizes = sizeType === 'womens' ? WOMENS_SIZES : UNISEX_SIZES;
  const grid = document.getElementById(`vf-sizes-${rowId}`);
  grid.innerHTML = allSizes.map(s =>
    `<span class="size-exclude-item" onclick="toggleSizeExclude(this, '${s}', ${rowId})" data-size="${s}">${s}</span>`
  ).join('');
}

// 商品を保存
async function saveProduct() {
  const model = document.getElementById('pf-model').value.trim();
  if (!model) { alert('モデル名を入力してください'); return; }

  const variantRows = document.querySelectorAll('.variant-form-row');
  const variants = [];
  for (const row of variantRows) {
    const colorway = row.querySelector('.vf-colorway').value.trim();
    const sku = row.querySelector('.vf-sku').value.trim();
    const sizeType = row.querySelector('.vf-sizetype').value;
    const price = parseFloat(row.querySelector('.vf-price').value) || 0;
    const image = row.querySelector('.vf-image').value.trim();
    const supplierUrl = row.querySelector('.vf-supplier-url').value.trim();
    const purchasePrice = parseFloat(row.querySelector('.vf-purchase-price').value) || 0;

    if (!colorway || !sku || !price) {
      alert('カラー名、型番、販売価格は必須です');
      return;
    }

    // 除外サイズを収集
    const excludedSizes = [];
    row.querySelectorAll('.size-exclude-item.excluded').forEach(el => {
      excludedSizes.push(el.dataset.size);
    });

    variants.push({ colorway, sku, sizeType, price, image, supplierUrl, purchasePrice, excludedSizes });
  }

  if (variants.length === 0) { alert('少なくとも1つのカラーを追加してください'); return; }

  if (editingProductId) {
    // 更新
    const res = await fetch(`/api/products/${editingProductId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, variants })
    });
    const updated = await res.json();
    const idx = products.findIndex(p => p.id === editingProductId);
    if (idx >= 0) products[idx] = updated;
  } else {
    // 新規
    const res = await fetch('/api/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, variants })
    });
    const created = await res.json();
    products.push(created);
  }

  closeProductForm();
  renderAdminProducts();
}

// =============================================
// =============================================
// セラー側：オーダー管理（収支計算付き）
// =============================================
// =============================================
let cachedOrders = [];
let cachedPurchases = [];
let cachedInstructions = [];
let cachedShipments = [];
let cachedDeliveries = [];
let cachedEffectiveRate = 149;

async function fetchExchangeRate() {
  try {
    const res = await fetch('/api/exchange-rate');
    const data = await res.json();
    currentExchangeRate = data.rate;
  } catch (e) {
    currentExchangeRate = 150;
  }
}

async function showOrderAdmin() {
  showScreen('screen-order-admin');
  await Promise.all([
    fetchExchangeRate(),
    loadProducts()
  ]);

  cachedEffectiveRate = currentExchangeRate - 1;
  document.getElementById('exchange-rate-display').textContent =
    `USD/JPY: ¥${cachedEffectiveRate.toFixed(1)}（実勢 ¥${currentExchangeRate.toFixed(1)} - ¥1）`;

  const [settingsRes, ordersRes, purchasesRes, instRes, shipmentsRes, deliveriesRes] = await Promise.all([
    fetch('/api/settings'),
    fetch('/api/orders'),
    fetch('/api/purchases'),
    fetch('/api/instructions'),
    fetch('/api/shipments'),
    fetch('/api/deliveries')
  ]);
  currentSettings = await settingsRes.json();
  cachedOrders = await ordersRes.json();
  cachedPurchases = await purchasesRes.json();
  cachedInstructions = await instRes.json();
  cachedShipments = await shipmentsRes.json();
  cachedDeliveries = await deliveriesRes.json();

  renderOrderAdmin(cachedOrders, cachedPurchases, cachedEffectiveRate, cachedShipments);
  updateInstButton();
}

// 折りたたみセクションヘルパー
function addCollapsible(container, title, bgClass, id, contentFn) {
  const header = document.createElement('div');
  header.className = `collapsible-header ${bgClass}`;
  header.id = `ch-${id}`;
  header.innerHTML = `<span class="collapse-icon">▼</span> ${title}`;
  header.onclick = () => toggleCollapse(id);
  container.appendChild(header);

  const body = document.createElement('div');
  body.className = 'collapsible-body';
  body.id = `cb-${id}`;
  body.style.maxHeight = '5000px';
  contentFn(body);
  container.appendChild(body);
}

function toggleCollapse(id) {
  const header = document.getElementById(`ch-${id}`);
  const body = document.getElementById(`cb-${id}`);
  header.classList.toggle('collapsed');
  body.classList.toggle('collapsed');
}

// =============================================
// 管理者編集モード
// =============================================
function editKeyStr(type, id, sku, size) {
  return `${type}\0${id}\0${sku}\0${size}`;
}

// 編集モードを開始
function enterAdminEdit() {
  adminEditMode = true;
  editKeys = [];
  editVals = [];
  origVals = [];
  editKeyMap = {};
  editProductInfo = {};

  // Current Ordersのデータを取得（発送済みを差し引いた残り。発送待ちは除外）
  const pendingOrders = cachedOrders.filter(o => o.status === 'pending');
  const allItems = [];
  pendingOrders.forEach(o => o.items.forEach(i => allItems.push(i)));
  const orderGroupedRaw = groupItemsBySku(allItems);
  const shipments = (cachedShipments || []).filter(s => !s.pendingShipment);
  const allShippedItems = [];
  shipments.forEach(s => s.items.forEach(i => allShippedItems.push(i)));
  const allShippedGrouped = groupShippedItems(allShippedItems);
  const orderGrouped = calcRemaining(orderGroupedRaw, allShippedGrouped);

  // 商品情報を保存
  orderGrouped.forEach(item => {
    editProductInfo[item.sku] = {
      model: item.model, colorway: item.colorway,
      price: item.price, sizeType: item.sizeType
    };
  });

  // オーダーの編集キーを登録
  orderGrouped.forEach(item => {
    const sizes = getSizesForType(item.sizeType);
    sizes.forEach(s => {
      const qty = item.sizes[s] || 0;
      const k = editKeyStr('order', '', item.sku, s);
      editKeyMap[k] = editKeys.length;
      editKeys.push({ type: 'order', id: '', sku: item.sku, size: s });
      editVals.push(qty);
      origVals.push(qty);
    });
  });

  // 各拠点の編集キーを登録
  if (currentSettings.locations) {
    currentSettings.locations.forEach(loc => {
      const locPurchases = cachedPurchases.filter(p => p.locationId === loc.id);
      const locGrouped = groupPurchaseItems(locPurchases);
      const locShipped = allShippedItems.filter(i => i.locationId === loc.id);
      const locShippedGrouped = groupShippedItems(locShipped);
      const locRemaining = calcRemaining(locGrouped, locShippedGrouped);

      // オーダー全商品 + 拠点既存商品をマージ
      const allProducts = [...orderGrouped];
      locGrouped.forEach(locItem => {
        if (!allProducts.find(p => p.sku === locItem.sku)) {
          allProducts.push(locItem);
          if (!editProductInfo[locItem.sku]) {
            editProductInfo[locItem.sku] = {
              model: locItem.model, colorway: locItem.colorway,
              price: 0, sizeType: locItem.sizeType
            };
          }
        }
      });

      allProducts.forEach(item => {
        const locItem = locRemaining.find(r => r.sku === item.sku);
        const sizes = getSizesForType(item.sizeType);
        sizes.forEach(s => {
          const qty = locItem ? (locItem.sizes[s] || 0) : 0;
          const k = editKeyStr('loc', loc.id, item.sku, s);
          editKeyMap[k] = editKeys.length;
          editKeys.push({ type: 'loc', id: loc.id, sku: item.sku, size: s });
          editVals.push(qty);
          origVals.push(qty);
        });
      });
    });
  }

  // ボタン切り替え＆再描画
  updateEditButtons(true);
  renderOrderAdmin(cachedOrders, cachedPurchases, cachedEffectiveRate, cachedShipments);
}

// 編集モードをキャンセル
function cancelAdminEdit() {
  adminEditMode = false;
  updateEditButtons(true);
  renderOrderAdmin(cachedOrders, cachedPurchases, cachedEffectiveRate, cachedShipments);
}

// +/- ボタンで値を変更
function editAdjust(idx, delta) {
  editVals[idx] = Math.max(0, editVals[idx] + delta);
  // 表示用とpopup内の両方を更新
  const el = document.getElementById(`ev-${idx}`);
  if (el) el.textContent = editVals[idx] || '';
  const elp = document.getElementById(`evp-${idx}`);
  if (elp) elp.textContent = editVals[idx];
  // セルの色を更新
  const cell = document.getElementById(`ec-${idx}`);
  if (cell) {
    if (editVals[idx] > 0) cell.classList.add('has-value');
    else cell.classList.remove('has-value');
  }

  // 行のQTYを再計算
  const key = editKeys[idx];
  let total = 0;
  editKeys.forEach((k, i) => {
    if (k.type === key.type && k.id === key.id && k.sku === key.sku) {
      total += editVals[i];
    }
  });
  const qtyEl = document.getElementById(`eq-${key.type}-${key.id}-${key.sku}`);
  if (qtyEl) qtyEl.textContent = total;
}

// 編集セルのクリックで±ボタンを展開/折りたたみ
let activeEditCell = null;
function toggleEditCell(idx, event) {
  const popup = document.getElementById(`ep-${idx}`);
  if (!popup) return;

  // 既に開いているpopupを閉じる
  if (activeEditCell !== null && activeEditCell !== idx) {
    const prev = document.getElementById(`ep-${activeEditCell}`);
    if (prev) prev.style.display = 'none';
  }

  if (popup.style.display === 'none') {
    popup.style.display = 'flex';
    activeEditCell = idx;
  } else {
    popup.style.display = 'none';
    activeEditCell = null;
  }
}

// 編集内容を保存
async function saveAdminEdits() {
  // デルタを計算
  const orderDeltas = [];
  const locDeltaMap = {}; // locId → items[]

  editKeys.forEach((key, i) => {
    const delta = editVals[i] - origVals[i];
    if (delta === 0) return;

    if (key.type === 'order') {
      const info = editProductInfo[key.sku];
      orderDeltas.push({
        sku: key.sku, size: key.size, delta,
        model: info.model, colorway: info.colorway,
        price: info.price, sizeType: info.sizeType
      });
    } else if (key.type === 'loc') {
      if (!locDeltaMap[key.id]) locDeltaMap[key.id] = [];
      const info = editProductInfo[key.sku];
      locDeltaMap[key.id].push({
        sku: key.sku, size: key.size, delta,
        sizeType: info.sizeType
      });
    }
  });

  // APIに送信
  const promises = [];
  if (orderDeltas.length > 0) {
    promises.push(fetch('/api/orders/adjust', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: orderDeltas })
    }));
  }
  Object.entries(locDeltaMap).forEach(([locId, items]) => {
    const loc = currentSettings.locations.find(l => l.id === locId);
    promises.push(fetch('/api/purchases/adjust', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ locationId: locId, locationName: loc?.name || '', items })
    }));
  });

  if (promises.length > 0) await Promise.all(promises);

  // データ再取得＆再描画
  adminEditMode = false;
  const [ordersRes, purchasesRes] = await Promise.all([
    fetch('/api/orders'),
    fetch('/api/purchases')
  ]);
  cachedOrders = await ordersRes.json();
  cachedPurchases = await purchasesRes.json();
  updateEditButtons(true);
  renderOrderAdmin(cachedOrders, cachedPurchases, cachedEffectiveRate, cachedShipments);
  showToast('保存しました');
}

// ヘッダーボタンの表示切り替え
function updateEditButtons(hasOrders) {
  const editBtn = document.getElementById('btn-admin-edit');
  const instBtn = document.getElementById('btn-inst');
  const saveBtn = document.getElementById('btn-admin-save');
  const cancelBtn = document.getElementById('btn-admin-cancel');
  if (adminEditMode) {
    if (editBtn) editBtn.style.display = 'none';
    if (instBtn) instBtn.style.display = 'none';
    if (saveBtn) saveBtn.style.display = '';
    if (cancelBtn) cancelBtn.style.display = '';
  } else {
    if (editBtn) editBtn.style.display = hasOrders ? '' : 'none';
    if (instBtn) instBtn.style.display = '';
    if (saveBtn) saveBtn.style.display = 'none';
    if (cancelBtn) cancelBtn.style.display = 'none';
  }
}

// 2つのグループデータのmax値をマージ（未指示計算用）
// 例: 指示済み3足、仕入済み5足 → 割り当て済みは5足
function mergeGroupedMax(groupA, groupB) {
  const map = {};
  groupA.forEach(item => {
    if (!map[item.sku]) map[item.sku] = { model: item.model, colorway: item.colorway, sku: item.sku, sizeType: item.sizeType, sizes: {} };
    Object.entries(item.sizes).forEach(([s, q]) => {
      map[item.sku].sizes[s] = Math.max(map[item.sku].sizes[s] || 0, q);
    });
  });
  groupB.forEach(item => {
    if (!map[item.sku]) map[item.sku] = { model: item.model, colorway: item.colorway, sku: item.sku, sizeType: item.sizeType, sizes: {} };
    Object.entries(item.sizes).forEach(([s, q]) => {
      map[item.sku].sizes[s] = Math.max(map[item.sku].sizes[s] || 0, q);
    });
  });
  return Object.values(map);
}

// 仕入済み + 未完了指示を加算（二重計上なし前提）
function mergeGroupedAdd(groupA, groupB) {
  const map = {};
  groupA.forEach(item => {
    if (!map[item.sku]) map[item.sku] = { model: item.model, colorway: item.colorway, sku: item.sku, sizeType: item.sizeType, sizes: {} };
    Object.entries(item.sizes).forEach(([s, q]) => {
      map[item.sku].sizes[s] = (map[item.sku].sizes[s] || 0) + q;
    });
  });
  groupB.forEach(item => {
    if (!map[item.sku]) map[item.sku] = { model: item.model, colorway: item.colorway, sku: item.sku, sizeType: item.sizeType, sizes: {} };
    Object.entries(item.sizes).forEach(([s, q]) => {
      map[item.sku].sizes[s] = (map[item.sku].sizes[s] || 0) + q;
    });
  });
  return Object.values(map);
}

// 商品リストのマージ（オーダー商品 + 拠点商品）
function mergeProductLists(list1, list2) {
  const merged = list1.map(item => ({
    model: item.model, colorway: item.colorway,
    sku: item.sku, sizeType: item.sizeType, sizes: {}
  }));
  list2.forEach(item => {
    if (!merged.find(m => m.sku === item.sku)) {
      merged.push({
        model: item.model, colorway: item.colorway,
        sku: item.sku, sizeType: item.sizeType, sizes: {}
      });
    }
  });
  return merged;
}

// 編集可能なテーブルを構築（+/-ボタン付き）
function buildEditableAdminTable(items, type, id) {
  const unisexItems = items.filter(g => g.sizeType !== 'womens');
  const womensItems = items.filter(g => g.sizeType === 'womens');

  const div = document.createElement('div');
  const tables = [];
  if (unisexItems.length > 0) tables.push({ items: unisexItems, sizes: UNISEX_SIZES, label: 'SIZE (UNISEX)' });
  if (womensItems.length > 0) tables.push({ items: womensItems, sizes: WOMENS_SIZES, label: "SIZE (WOMEN'S)" });

  if (tables.length === 0) {
    div.innerHTML = '<div class="no-orders" style="padding:20px">商品なし</div>';
    return div;
  }

  let rowNum = 1;
  tables.forEach(({ items: tItems, sizes, label }) => {
    const tDiv = document.createElement('div');
    tDiv.className = 'finance-spreadsheet';
    let html = '<div class="spreadsheet-scroll"><table>';
    html += `<thead><tr>
      <th class="col-no">No</th><th class="col-product">Products</th>
      <th class="col-color">Color</th><th class="col-sku">Style Code</th>
      <th class="col-qty">QTY</th>
      <th class="col-size-group" colspan="${sizes.length}">${label}</th>
    </tr><tr>
      <th class="col-no"></th><th class="col-product"></th><th class="col-color"></th>
      <th class="col-sku"></th><th class="col-qty"></th>`;
    sizes.forEach(s => html += `<th class="col-size">${s}</th>`);
    html += '</tr></thead><tbody>';

    tItems.forEach(item => {
      // 行QTYの計算
      let rowTotal = 0;
      sizes.forEach(s => {
        const k = editKeyStr(type, id, item.sku, s);
        const idx = editKeyMap[k];
        if (idx !== undefined) rowTotal += editVals[idx];
      });
      const qtyId = `eq-${type}-${id}-${item.sku}`;

      html += `<tr>
        <td class="col-no">${rowNum++}</td>
        <td class="col-product">${item.model}</td>
        <td class="col-color">${item.colorway}</td>
        <td class="col-sku">${item.sku}</td>
        <td class="col-qty" id="${qtyId}">${rowTotal}</td>`;

      sizes.forEach(s => {
        const k = editKeyStr(type, id, item.sku, s);
        const idx = editKeyMap[k];
        if (idx !== undefined) {
          const qty = editVals[idx];
          const hasValue = qty > 0 ? ' has-value' : '';
          // クリックで±ボタンを展開、通常は数値のみ表示
          html += `<td class="col-size inst-cell${hasValue}" id="ec-${idx}" onclick="toggleEditCell(${idx}, event)">`;
          html += `<span class="inst-val-display" id="ev-${idx}">${qty || ''}</span>`;
          html += `<div class="inst-picker-popup" id="ep-${idx}" style="display:none;">`;
          html += `<button class="inst-minus" onclick="editAdjust(${idx},-1);event.stopPropagation();">-</button>`;
          html += `<span class="inst-val" id="evp-${idx}">${qty}</span>`;
          html += `<button class="inst-plus" onclick="editAdjust(${idx},1);event.stopPropagation();">+</button>`;
          html += `</div></td>`;
        } else {
          html += '<td class="col-size"></td>';
        }
      });
      html += '</tr>';
    });

    html += '</tbody></table></div>';
    tDiv.innerHTML = html;
    div.appendChild(tDiv);
  });

  return div;
}

// 編集モードのレンダリング
function renderOrderAdminEditMode(container, orderGrouped, purchases, shippedItems) {
  // Current Orders（編集可能）
  addCollapsible(container, 'Current Orders', 'bg-dark', 'current', (body) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'order-table-wrapper';
    wrapper.appendChild(buildEditableAdminTable(orderGrouped, 'order', ''));
    body.appendChild(wrapper);
  });

  // 全登録拠点（編集可能）
  if (currentSettings.locations) {
    currentSettings.locations.forEach(loc => {
      const locPurchases = cachedPurchases.filter(p => p.locationId === loc.id);
      const locGrouped = groupPurchaseItems(locPurchases);
      const locShipped = shippedItems.filter(i => i.locationId === loc.id);
      const locShippedGrouped = groupShippedItems(locShipped);
      const locRemaining = calcRemaining(locGrouped, locShippedGrouped);
      const mergedProducts = mergeProductLists(orderGrouped, locRemaining);
      const locPairs = locRemaining.reduce((s, i) => s + Object.values(i.sizes).reduce((a, b) => a + b, 0), 0);

      addCollapsible(container, `${loc.name}（${locPairs}足）`, 'bg-blue', `loc-${loc.id}`, (body) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'order-table-wrapper';
        wrapper.appendChild(buildEditableAdminTable(mergedProducts, 'loc', loc.id));
        body.appendChild(wrapper);
      });
    });
  }
}

function renderOrderAdmin(orders, purchases, rate, shipments) {
  shipments = shipments || [];
  const container = document.getElementById('order-admin-content');
  container.innerHTML = '';

  const purchasePriceMap = {};
  const supplierUrlMap = {};
  const imageMap = {};
  products.forEach(p => {
    p.variants.forEach(v => {
      purchasePriceMap[v.sku] = v.purchasePrice || 0;
      supplierUrlMap[v.sku] = v.supplierUrl || '';
      imageMap[v.sku] = v.image || '';
    });
  });

  const coupon = currentSettings.couponPerPair || 0;
  const customsUnit = currentSettings.customsUnitPrice || 0;
  const customsPerPair = Math.round(customsUnit * 0.155);
  const shippingPerPair = currentSettings.shippingPerPair || 0;

  const pendingOrders = orders.filter(o => o.status === 'pending');

  // 編集ボタンの表示制御
  updateEditButtons(pendingOrders.length > 0);

  if (pendingOrders.length === 0) {
    container.innerHTML = '<div class="no-orders">現在のオーダーはありません</div>';
    return;
  }

  const allItems = [];
  pendingOrders.forEach(o => o.items.forEach(i => allItems.push(i)));
  const grouped = groupItemsBySku(allItems);
  const purchasedGrouped = groupPurchaseItems(purchases);

  // 発送済アイテムをグループ化（発送完了分のみ — 発送待ちは除外）
  const completedShipments = shipments.filter(s => !s.pendingShipment);
  const shippedItems = [];
  completedShipments.forEach(s => s.items.forEach(i => shippedItems.push(i)));
  const shippedGrouped = groupShippedItems(shippedItems);

  // ======= SKU表示順の統一 =======
  // 全セクションでproductsマスタ順（sortItemsBySkuOrder）を使用
  const sortBySkuOrder = sortItemsBySkuOrder;

  // 編集モードの場合は専用レンダリング
  if (adminEditMode) {
    renderOrderAdminEditMode(container, grouped, purchases, shippedItems);
    return;
  }

  // 未完了指示アイテムを計算（ビルディング中のブロックも含む）
  const pendingInstructed = getInstructedIncludingBuilding();
  // 割り当て済み = 仕入済み + 未完了指示（加算。completedバッチはpurchasesに含まれるため二重計上なし）
  const assignedGrouped = mergeGroupedAdd(purchasedGrouped, pendingInstructed);
  // 未指示 = オーダー - 割り当て済み
  const unassigned = calcRemaining(grouped, assignedGrouped);

  // ======= Current Orders（発送済を差し引いた残り） =======
  const currentOrderItems = calcRemaining(grouped, shippedGrouped);
  // priceを補完（calcRemainingで欠ける場合）
  currentOrderItems.forEach(item => {
    if (!item.price) {
      const orig = grouped.find(g => g.sku === item.sku);
      if (orig) item.price = orig.price;
    }
  });
  const currentOrderPairs = currentOrderItems.reduce((s,i) => s + Object.values(i.sizes).reduce((a,b)=>a+b,0), 0);

  if (currentOrderPairs === 0 && grouped.length > 0) {
    // 全発送済
    addCollapsible(container, 'Current Orders（0足 - 全て発送済）', 'bg-dark', 'current', (body) => {
      body.innerHTML = '<div class="no-orders" style="padding:20px">全て発送済みです</div>';
    });
  } else {
    addCollapsible(container, `Current Orders（${currentOrderPairs}足）`, 'bg-dark', 'current', (body) => {
      const wrapper = document.createElement('div');
      wrapper.className = 'order-table-wrapper';
      const result = buildFinanceTable(sortBySkuOrder(currentOrderItems.length > 0 ? currentOrderItems : grouped), rate, purchasePriceMap, supplierUrlMap, coupon, customsPerPair, shippingPerPair);
      wrapper.appendChild(result.table);
      wrapper.appendChild(buildFinanceTotals(result.totals));
      body.appendChild(wrapper);
    });
  }

  // ======= 未指示 =======
  const unassignedPairs = unassigned.length > 0 ? unassigned.reduce((s,i) => s + Object.values(i.sizes).reduce((a,b)=>a+b,0), 0) : 0;
  addCollapsible(container, `未指示（${unassignedPairs}足）`, 'bg-red', 'unassigned', (body) => {
    if (unassigned.length === 0) {
      body.innerHTML = '<div class="no-orders" style="padding:20px">全て指示済みです</div>';
    } else {
      const wrapper = document.createElement('div');
      wrapper.className = 'order-table-wrapper';
      const result = buildUnassignedTable(unassigned);
      wrapper.appendChild(result.table);
      body.appendChild(wrapper);
    }
  });

  // ======= 仕入残り =======
  const remaining = calcRemaining(grouped, purchasedGrouped);
  const remainingPairs = remaining.reduce((s,i) => s + Object.values(i.sizes).reduce((a,b)=>a+b,0), 0);
  addCollapsible(container, `仕入残り（${remainingPairs}足）`, 'bg-orange', 'remaining', (body) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'order-table-wrapper';
    const result = buildRemainingTable(remaining);
    wrapper.appendChild(result.table);
    body.appendChild(wrapper);
  });

  // ======= 仕入済（拠点別・発送済み差引） =======
  // 各拠点の仕入済から、その拠点で発送済みの分を差し引く
  let totalPurchasedRemaining = 0;
  const locPurchaseData = []; // [{loc, remaining, pairs}]
  if (currentSettings.locations) {
    currentSettings.locations.forEach(loc => {
      const locPurchases = purchases.filter(p => p.locationId === loc.id);
      const locGrouped = groupPurchaseItems(locPurchases);
      // この拠点の発送済みを差し引く（発送完了分のみ）
      const locShipped = [];
      completedShipments.forEach(s => s.items.forEach(i => {
        if (i.locationId === loc.id) locShipped.push(i);
      }));
      const locShippedGrouped = groupShippedItems(locShipped);
      const locRemaining = calcRemaining(locGrouped, locShippedGrouped);
      const locPairs = locRemaining.reduce((s,i) => s + Object.values(i.sizes).reduce((a,b)=>a+b,0), 0);
      totalPurchasedRemaining += locPairs;
      if (locPairs > 0) locPurchaseData.push({ loc, remaining: locRemaining, pairs: locPairs });
    });
  }
  // 全拠点の合計
  const allRemainingGrouped = [];
  locPurchaseData.forEach(d => {
    d.remaining.forEach(item => {
      const existing = allRemainingGrouped.find(g => g.sku === item.sku);
      if (existing) {
        Object.entries(item.sizes).forEach(([s, q]) => {
          existing.sizes[s] = (existing.sizes[s] || 0) + q;
        });
      } else {
        allRemainingGrouped.push({ ...item, sizes: { ...item.sizes } });
      }
    });
  });

  if (allRemainingGrouped.length > 0 || locPurchaseData.length > 0) {
    addCollapsible(container, `仕入済（${totalPurchasedRemaining}足）`, 'bg-green', 'purchased', (body) => {
      // 合計一覧テーブル
      if (allRemainingGrouped.length > 0) {
        const totalHeader = document.createElement('div');
        totalHeader.className = 'loc-sub-header';
        totalHeader.textContent = `合計（${totalPurchasedRemaining}足）`;
        body.appendChild(totalHeader);
        const totalWrapper = document.createElement('div');
        totalWrapper.className = 'order-table-wrapper';
        const totalResult = buildSimpleTable(sortBySkuOrder(allRemainingGrouped));
        totalWrapper.appendChild(totalResult.table);
        body.appendChild(totalWrapper);
      }
      // 拠点別
      locPurchaseData.forEach(d => {
        const locHeader = document.createElement('div');
        locHeader.className = 'loc-sub-header';
        locHeader.textContent = `${d.loc.name}（${d.pairs}足）`;
        body.appendChild(locHeader);
        const wrapper = document.createElement('div');
        wrapper.className = 'order-table-wrapper';
        const result = buildSimpleTable(sortBySkuOrder(d.remaining));
        wrapper.appendChild(result.table);
        body.appendChild(wrapper);
      });
    });
  }

  // ======= 登録済み仕入指示（拠点ごとにグループ化・タブ表示） =======
  const activeInstructions = cachedInstructions.filter(i => i.status === 'active');
  if (activeInstructions.length > 0) {
    // 拠点ごとにグループ化
    const locGroups = {};
    activeInstructions.forEach(inst => {
      if (!locGroups[inst.locationId]) locGroups[inst.locationId] = { name: inst.locationName, instructions: [] };
      locGroups[inst.locationId].instructions.push(inst);
    });

    addCollapsible(container, `仕入指示一覧（${activeInstructions.length}件）`, 'bg-dark', 'instructions', (body) => {
      Object.entries(locGroups).forEach(([locId, group]) => {
        // 拠点ヘッダー
        const locSection = document.createElement('div');
        locSection.className = 'inst-loc-section';

        // タブバー
        const tabBar = document.createElement('div');
        tabBar.className = 'inst-tab-bar';
        group.instructions.forEach((inst, idx) => {
          const totalPairs = inst.batches.reduce((s, b) =>
            s + b.items.reduce((ss, i) => ss + Object.values(i.sizes).reduce((a,v)=>a+v,0), 0), 0);
          const blockCount = inst.batches.length;
          const tab = document.createElement('button');
          tab.className = `inst-tab ${idx === 0 ? 'active' : ''}`;
          tab.id = `inst-tab-${locId}-${idx}`;
          tab.textContent = `${group.name}仕入 ${idx + 1}（${totalPairs}足/${blockCount}ブロック）`;
          tab.onclick = () => switchLocInstTab(locId, idx, group.instructions.length);
          tabBar.appendChild(tab);
        });
        locSection.appendChild(tabBar);

        // タブコンテンツ
        group.instructions.forEach((inst, idx) => {
          const panel = document.createElement('div');
          panel.className = `inst-tab-panel ${idx === 0 ? 'active' : ''}`;
          panel.id = `inst-panel-${locId}-${idx}`;

          // 順番変更 + 削除
          const actions = document.createElement('div');
          actions.className = 'inst-tab-actions';
          actions.innerHTML = `
            <button class="inst-move-btn" onclick="moveLocInstruction('${locId}',${idx},-1)" ${idx === 0 ? 'disabled' : ''}>▲ 上へ</button>
            <button class="inst-move-btn" onclick="moveLocInstruction('${locId}',${idx},1)" ${idx === group.instructions.length - 1 ? 'disabled' : ''}>▼ 下へ</button>
            <button class="danger-btn-sm" onclick="deleteInstruction('${inst.id}')">削除</button>
          `;
          panel.appendChild(actions);

          // ブロック（バッチ）ごとに商品テーブルを表示
          inst.batches.forEach(batch => {
            const batchDiv = document.createElement('div');
            batchDiv.className = 'inst-batch-section';
            const isCompleted = batch.status === 'completed';
            const totalBatchPairs = batch.items.reduce((s, i) => s + Object.values(i.sizes).reduce((a,v)=>a+v,0), 0);
            const statusBadge = isCompleted ? ' <span class="batch-done-badge">✅ 仕入済</span>' : '';
            batchDiv.innerHTML = `<div class="inst-batch-label" style="display:flex;align-items:center;justify-content:space-between;">
              <span>${batch.name}（${totalBatchPairs}足）${statusBadge}</span>
              <button class="batch-delete-btn-sm" onclick="deleteBatch('${inst.id}','${batch.id}','${batch.name}',${isCompleted})">🗑 削除</button>
            </div>`;
            const items = batch.items.map(bi => ({
              model: bi.model, colorway: bi.colorway, sku: bi.sku, sizeType: bi.sizeType, sizes: bi.sizes
            }));
            if (items.length > 0) {
              const wrapper = document.createElement('div');
              wrapper.className = 'order-table-wrapper';
              const result = buildSimpleTable(items);
              wrapper.appendChild(result.table);
              batchDiv.appendChild(wrapper);
            }
            panel.appendChild(batchDiv);
          });

          locSection.appendChild(panel);
        });

        body.appendChild(locSection);
      });
    });
  }
}

// 未完了指示アイテムを計算（pendingバッチのみ。completedバッチはpurchasesに含まれるため除外）
function calcInstructedItems(instructions) {
  const map = {};
  instructions.filter(i => i.status === 'active').forEach(inst => {
    inst.batches.filter(b => b.status === 'pending').forEach(batch => {
      batch.items.forEach(item => {
        if (!map[item.sku]) {
          map[item.sku] = { model: item.model, colorway: item.colorway, sku: item.sku, sizeType: item.sizeType, sizes: {} };
        }
        Object.entries(item.sizes).forEach(([size, qty]) => {
          map[item.sku].sizes[size] = (map[item.sku].sizes[size] || 0) + qty;
        });
      });
    });
  });
  return Object.values(map);
}

// タブ切り替え（拠点別）
function switchLocInstTab(locId, idx, total) {
  for (let i = 0; i < total; i++) {
    const tab = document.getElementById(`inst-tab-${locId}-${i}`);
    const panel = document.getElementById(`inst-panel-${locId}-${i}`);
    if (tab) tab.classList.toggle('active', i === idx);
    if (panel) panel.classList.toggle('active', i === idx);
  }
}

// 仕入指示の順番変更（拠点内）
async function moveLocInstruction(locId, idx, direction) {
  const locInstructions = cachedInstructions.filter(i => i.status === 'active' && i.locationId === locId);
  const newIdx = idx + direction;
  if (newIdx < 0 || newIdx >= locInstructions.length) return;

  // 拠点内の入れ替え
  [locInstructions[idx], locInstructions[newIdx]] = [locInstructions[newIdx], locInstructions[idx]];

  // 全指示の新しい順序を構築
  const allIds = [];
  // アクティブ: 変更した拠点 + 他の拠点
  const otherActive = cachedInstructions.filter(i => i.status === 'active' && i.locationId !== locId);
  locInstructions.forEach(i => allIds.push(i.id));
  otherActive.forEach(i => allIds.push(i.id));
  // 非アクティブ
  cachedInstructions.filter(i => i.status !== 'active').forEach(i => allIds.push(i.id));

  await fetch('/api/instructions/reorder', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ orderedIds: allIds })
  });
  await showOrderAdmin();
}

// 仕入指示を削除
async function deleteInstruction(id) {
  if (!confirm('この仕入指示を削除しますか？')) return;
  await fetch(`/api/instructions/${id}`, { method: 'DELETE' });
  await showOrderAdmin();
}

// 収支付きテーブル生成
function buildFinanceTable(grouped, rate, purchasePriceMap, supplierUrlMap, coupon, customsPerPair, shippingPerPair) {
  const unisexItems = grouped.filter(g => g.sizeType !== 'womens');
  const womensItems = grouped.filter(g => g.sizeType === 'womens');

  const allGrouped = [...unisexItems, ...womensItems];
  const div = document.createElement('div');

  // 合計変数
  let totals = { pairs: 0, amountUsd: 0, purchase: 0, couponTotal: 0, purchaseTotal: 0, customs: 0, shipping: 0, revenue: 0, profit: 0 };

  // Unisex と Women's を分けて描画
  const tables = [];
  if (unisexItems.length > 0) {
    tables.push({ items: unisexItems, sizes: UNISEX_SIZES, label: 'SIZE (UNISEX)' });
  }
  if (womensItems.length > 0) {
    tables.push({ items: womensItems, sizes: WOMENS_SIZES, label: "SIZE (WOMEN'S)" });
  }

  let rowNum = 1;
  tables.forEach(({ items, sizes, label }) => {
    const tDiv = document.createElement('div');
    tDiv.className = 'finance-spreadsheet';

    let html = '<div class="spreadsheet-scroll"><table>';

    // ヘッダー行1
    html += `<thead><tr>
      <th class="col-no">No</th>
      <th class="col-product">Products</th>
      <th class="col-color">Color</th>
      <th class="col-sku">Style Code</th>
      <th class="col-qty">QTY</th>
      <th class="col-price">単価</th>
      <th class="col-amount">Amount</th>
      <th class="col-size-group" colspan="${sizes.length}">${label}</th>
      <th class="col-url">URL</th>
      <th class="col-fin">仕入値</th>
      <th class="col-fin">クーポン</th>
      <th class="col-fin-total">仕入合計</th>
      <th class="col-fin">関税</th>
      <th class="col-fin">送料</th>
      <th class="col-fin">売上</th>
      <th class="col-fin">利益</th>
      <th class="col-margin">利益率</th>
    </tr>`;

    // ヘッダー行2
    html += `<tr>
      <th class="col-no"></th><th class="col-product"></th><th class="col-color"></th>
      <th class="col-sku"></th><th class="col-qty"></th><th class="col-price"></th><th class="col-amount"></th>`;
    sizes.forEach(s => html += `<th class="col-size">${s}</th>`);
    html += `<th class="col-url"></th><th class="col-fin">A</th><th class="col-fin">B</th>
      <th class="col-fin-total">C</th><th class="col-fin">D</th><th class="col-fin">E</th>
      <th class="col-fin">F</th><th class="col-fin">G</th><th class="col-margin"></th>
    </tr></thead><tbody>`;

    items.forEach(item => {
      const pairs = Object.values(item.sizes).reduce((s, q) => s + q, 0);
      const amountUsd = pairs * item.price;
      const pp = purchasePriceMap[item.sku] || 0;
      const url = supplierUrlMap[item.sku] || '';

      const A = pp * pairs;             // 仕入値合計
      const B = coupon * pairs;          // クーポン合計
      const C = A + B;                   // 仕入合計
      const D = customsPerPair * pairs;  // 関税合計
      const E = shippingPerPair * pairs; // 送料合計
      const F = Math.round(amountUsd * rate); // 売上（円）
      const G = F - C - D - E;          // 利益
      const margin = F > 0 ? ((G / F) * 100).toFixed(1) : '0.0';

      totals.pairs += pairs;
      totals.amountUsd += amountUsd;
      totals.purchase += A;
      totals.couponTotal += B;
      totals.purchaseTotal += C;
      totals.customs += D;
      totals.shipping += E;
      totals.revenue += F;
      totals.profit += G;

      const profitClass = G >= 0 ? 'profit-positive' : 'profit-negative';
      const urlHtml = url ? `<a href="${url}" target="_blank">Link</a>` : '';

      html += `<tr>
        <td class="col-no">${rowNum++}</td>
        <td class="col-product">${item.model}</td>
        <td class="col-color">${item.colorway}</td>
        <td class="col-sku">${item.sku}</td>
        <td class="col-qty">${pairs}</td>
        <td class="col-price">$${item.price}</td>
        <td class="col-amount">$${amountUsd.toLocaleString()}</td>`;

      sizes.forEach(s => {
        const qty = item.sizes[s] || 0;
        html += `<td class="col-size ${qty ? 'has-value' : ''}">${qty || ''}</td>`;
      });

      html += `
        <td class="col-url">${urlHtml}</td>
        <td class="col-fin">¥${A.toLocaleString()}</td>
        <td class="col-fin">¥${B.toLocaleString()}</td>
        <td class="col-fin-total">¥${C.toLocaleString()}</td>
        <td class="col-fin">¥${D.toLocaleString()}</td>
        <td class="col-fin">¥${E.toLocaleString()}</td>
        <td class="col-fin">¥${F.toLocaleString()}</td>
        <td class="col-fin ${profitClass}">¥${G.toLocaleString()}</td>
        <td class="col-margin">${margin}%</td>
      </tr>`;
    });

    html += '</tbody></table></div>';
    tDiv.innerHTML = html;
    div.appendChild(tDiv);
  });

  return { table: div, totals };
}

// 合計表示
function buildFinanceTotals(totals) {
  const margin = totals.revenue > 0 ? ((totals.profit / totals.revenue) * 100).toFixed(1) : '0.0';
  const div = document.createElement('div');
  div.className = 'finance-totals';
  div.innerHTML = `
    <div class="ft-item"><span class="ft-label">合計足数:</span><span class="ft-value">${totals.pairs}</span></div>
    <div class="ft-item"><span class="ft-label">売上(USD):</span><span class="ft-value">$${totals.amountUsd.toLocaleString()}</span></div>
    <div class="ft-item"><span class="ft-label">仕入合計:</span><span class="ft-value">¥${totals.purchaseTotal.toLocaleString()}</span></div>
    <div class="ft-item"><span class="ft-label">関税:</span><span class="ft-value">¥${totals.customs.toLocaleString()}</span></div>
    <div class="ft-item"><span class="ft-label">送料:</span><span class="ft-value">¥${totals.shipping.toLocaleString()}</span></div>
    <div class="ft-item"><span class="ft-label">売上(JPY):</span><span class="ft-value">¥${totals.revenue.toLocaleString()}</span></div>
    <div class="ft-item"><span class="ft-label">利益:</span><span class="ft-value" style="color:${totals.profit >= 0 ? '#2e7d32' : '#c62828'}">¥${totals.profit.toLocaleString()}</span></div>
    <div class="ft-item"><span class="ft-label">利益率:</span><span class="ft-value">${margin}%</span></div>
  `;
  return div;
}

// 仕入記録をSKU+サイズでグルーピング
function groupPurchaseItems(purchases) {
  // 商品マスタからmodel/colorwayを引くためのマップ
  const productInfoMap = {};
  products.forEach(p => {
    p.variants.forEach(v => {
      productInfoMap[v.sku] = { model: p.model, colorway: v.colorway };
    });
  });

  const map = {};
  purchases.forEach(p => {
    p.items.forEach(item => {
      const key = item.sku;
      if (!map[key]) {
        const info = productInfoMap[item.sku] || {};
        map[key] = {
          model: item.model || info.model || '',
          colorway: item.colorway || info.colorway || '',
          sku: item.sku,
          sizeType: item.sizeType || 'unisex',
          sizes: {}
        };
      }
      map[key].sizes[item.size] = (map[key].sizes[item.size] || 0) + item.quantity;
    });
  });
  return Object.values(map);
}

// 発送済アイテムをSKUでグループ化
function groupShippedItems(shippedItems) {
  const map = {};
  shippedItems.forEach(item => {
    const key = item.sku;
    if (!map[key]) {
      map[key] = {
        model: item.model || '',
        colorway: item.colorway || '',
        sku: item.sku,
        sizeType: item.sizeType || 'unisex',
        sizes: {}
      };
    }
    map[key].sizes[item.size] = (map[key].sizes[item.size] || 0) + item.quantity;
  });
  return Object.values(map);
}

// 仕入残り計算（オーダー - 仕入済）
function calcRemaining(orderGrouped, purchasedGrouped) {
  // 全SKUを取得
  const allSkus = new Set();
  orderGrouped.forEach(g => allSkus.add(g.sku));
  purchasedGrouped.forEach(g => allSkus.add(g.sku));

  const result = [];
  allSkus.forEach(sku => {
    const orderItem = orderGrouped.find(g => g.sku === sku);
    const purchaseItem = purchasedGrouped.find(g => g.sku === sku);

    const source = orderItem || purchaseItem;
    const item = {
      model: source.model,
      colorway: source.colorway,
      sku,
      sizeType: source.sizeType,
      price: source.price, // price情報を保持
      sizes: {}
    };

    // 全サイズを対象
    const allSizes = getSizesForType(item.sizeType);
    allSizes.forEach(s => {
      const ordered = orderItem ? (orderItem.sizes[s] || 0) : 0;
      const purchased = purchaseItem ? (purchaseItem.sizes[s] || 0) : 0;
      const remaining = ordered - purchased;
      if (remaining !== 0) {
        item.sizes[s] = remaining;
      }
    });

    if (Object.keys(item.sizes).length > 0) {
      result.push(item);
    }
  });
  return result;
}

// 仕入残りテーブル（マイナスは赤字）
function buildRemainingTable(items) {
  const unisexItems = items.filter(g => g.sizeType !== 'womens');
  const womensItems = items.filter(g => g.sizeType === 'womens');

  const div = document.createElement('div');
  const tables = [];
  if (unisexItems.length > 0) tables.push({ items: unisexItems, sizes: UNISEX_SIZES, label: 'SIZE (UNISEX)' });
  if (womensItems.length > 0) tables.push({ items: womensItems, sizes: WOMENS_SIZES, label: "SIZE (WOMEN'S)" });

  if (tables.length === 0) {
    div.innerHTML = '<div class="no-orders">仕入残りはありません</div>';
    return { table: div };
  }

  let rowNum = 1;
  tables.forEach(({ items: tItems, sizes, label }) => {
    const tDiv = document.createElement('div');
    tDiv.className = 'finance-spreadsheet';
    let html = '<div class="spreadsheet-scroll"><table>';
    html += `<thead><tr>
      <th class="col-no">No</th><th class="col-product">Products</th>
      <th class="col-color">Color</th><th class="col-sku">Style Code</th>
      <th class="col-qty">残り</th>
      <th class="col-size-group" colspan="${sizes.length}">${label}</th>
    </tr><tr>
      <th class="col-no"></th><th class="col-product"></th><th class="col-color"></th>
      <th class="col-sku"></th><th class="col-qty"></th>`;
    sizes.forEach(s => html += `<th class="col-size">${s}</th>`);
    html += '</tr></thead><tbody>';

    tItems.forEach(item => {
      const totalRemaining = Object.values(item.sizes).reduce((s, q) => s + q, 0);
      html += `<tr>
        <td class="col-no">${rowNum++}</td>
        <td class="col-product">${item.model}</td>
        <td class="col-color">${item.colorway}</td>
        <td class="col-sku">${item.sku}</td>
        <td class="col-qty">${totalRemaining}</td>`;

      sizes.forEach(s => {
        const qty = item.sizes[s] || 0;
        if (qty < 0) {
          html += `<td class="col-size negative-qty">${qty}</td>`;
        } else if (qty > 0) {
          html += `<td class="col-size has-value">${qty}</td>`;
        } else {
          html += `<td class="col-size"></td>`;
        }
      });
      html += '</tr>';
    });

    html += '</tbody></table></div>';
    tDiv.innerHTML = html;
    div.appendChild(tDiv);
  });

  return { table: div };
}

// シンプルテーブル（仕入済/拠点別）
function buildSimpleTable(items) {
  const unisexItems = items.filter(g => g.sizeType !== 'womens');
  const womensItems = items.filter(g => g.sizeType === 'womens');

  const div = document.createElement('div');
  const tables = [];
  if (unisexItems.length > 0) tables.push({ items: unisexItems, sizes: UNISEX_SIZES, label: 'SIZE (UNISEX)' });
  if (womensItems.length > 0) tables.push({ items: womensItems, sizes: WOMENS_SIZES, label: "SIZE (WOMEN'S)" });

  if (tables.length === 0) {
    div.innerHTML = '<div class="no-orders">データなし</div>';
    return { table: div };
  }

  let rowNum = 1;
  tables.forEach(({ items: tItems, sizes, label }) => {
    const tDiv = document.createElement('div');
    tDiv.className = 'finance-spreadsheet';
    let html = '<div class="spreadsheet-scroll"><table>';
    html += `<thead><tr>
      <th class="col-no">No</th><th class="col-product">Products</th>
      <th class="col-color">Color</th><th class="col-sku">Style Code</th>
      <th class="col-qty">QTY</th>
      <th class="col-size-group" colspan="${sizes.length}">${label}</th>
    </tr><tr>
      <th class="col-no"></th><th class="col-product"></th><th class="col-color"></th>
      <th class="col-sku"></th><th class="col-qty"></th>`;
    sizes.forEach(s => html += `<th class="col-size">${s}</th>`);
    html += '</tr></thead><tbody>';

    tItems.forEach(item => {
      const pairs = Object.values(item.sizes).reduce((s, q) => s + q, 0);
      html += `<tr>
        <td class="col-no">${rowNum++}</td>
        <td class="col-product">${item.model}</td>
        <td class="col-color">${item.colorway}</td>
        <td class="col-sku">${item.sku}</td>
        <td class="col-qty">${pairs}</td>`;

      sizes.forEach(s => {
        const qty = item.sizes[s] || 0;
        html += `<td class="col-size ${qty ? 'has-value' : ''}">${qty || ''}</td>`;
      });
      html += '</tr>';
    });

    html += '</tbody></table></div>';
    tDiv.innerHTML = html;
    div.appendChild(tDiv);
  });

  return { table: div };
}

// =============================================
// 納品済テーブル（編集可能）
// 仕入済SKU×size をベースに、納品済を手動で入力できる
// =============================================
function buildDeliveryEditTable(baseItems, deliveries) {
  // deliveries を sku -> size -> qty の map に変換
  const delMap = {};
  deliveries.forEach(d => {
    if (!delMap[d.sku]) delMap[d.sku] = {};
    delMap[d.sku][d.size] = d.quantity;
  });

  // 仕入済 + deliveries の SKU をユニオン
  const skuSet = new Set(baseItems.map(i => i.sku));
  deliveries.forEach(d => skuSet.add(d.sku));

  // baseItems に存在しない SKU は products から補完
  const items = [];
  skuSet.forEach(sku => {
    const found = baseItems.find(i => i.sku === sku);
    if (found) {
      items.push({ ...found, _delMap: delMap[sku] || {} });
    } else {
      // products マスタから補完
      let model = '', colorway = '', sizeType = 'unisex';
      for (const p of (products || [])) {
        const v = (p.variants || []).find(v => v.sku === sku);
        if (v) {
          model = p.model || '';
          colorway = v.colorway || '';
          sizeType = v.sizeType || p.sizeType || 'unisex';
          break;
        }
      }
      items.push({ sku, model, colorway, sizeType, sizes: {}, _delMap: delMap[sku] || {} });
    }
  });

  const unisexItems = items.filter(g => g.sizeType !== 'womens');
  const womensItems = items.filter(g => g.sizeType === 'womens');

  const div = document.createElement('div');
  const tables = [];
  if (unisexItems.length > 0) tables.push({ items: unisexItems, sizes: UNISEX_SIZES, label: 'SIZE (UNISEX)' });
  if (womensItems.length > 0) tables.push({ items: womensItems, sizes: WOMENS_SIZES, label: "SIZE (WOMEN'S)" });

  if (tables.length === 0) {
    div.innerHTML = '<div class="no-orders" style="padding:20px">仕入済アイテムがありません。仕入が完了すると納品済として手動入力できるようになります。</div>';
    return { table: div };
  }

  let rowNum = 1;
  tables.forEach(({ items: tItems, sizes, label }) => {
    const tDiv = document.createElement('div');
    tDiv.className = 'finance-spreadsheet';
    let html = '<div class="spreadsheet-scroll"><table>';
    html += `<thead><tr>
      <th class="col-no">No</th><th class="col-product">Products</th>
      <th class="col-color">Color</th><th class="col-sku">Style Code</th>
      <th class="col-qty">納品</th>
      <th class="col-size-group" colspan="${sizes.length}">${label}</th>
    </tr><tr>
      <th class="col-no"></th><th class="col-product"></th><th class="col-color"></th>
      <th class="col-sku"></th><th class="col-qty"></th>`;
    sizes.forEach(s => html += `<th class="col-size">${s}</th>`);
    html += '</tr></thead><tbody>';

    tItems.forEach(item => {
      const delQtySum = Object.values(item._delMap).reduce((s, q) => s + (q || 0), 0);
      const totalId = `del-total-${item.sku.replace(/[^a-zA-Z0-9]/g,'_')}`;
      html += `<tr>
        <td class="col-no">${rowNum++}</td>
        <td class="col-product">${item.model}</td>
        <td class="col-color">${item.colorway}</td>
        <td class="col-sku">${item.sku}</td>
        <td class="col-qty" id="${totalId}">${delQtySum}</td>`;

      sizes.forEach(s => {
        const delQty = item._delMap[s] || 0;
        // 仕入済がある、または納品済がある → 入力可能セル
        const cellClass = delQty > 0 ? 'has-value' : '';
        html += `<td class="col-size ${cellClass}">`;
        html += `<input type="number" class="delivery-input" min="1" value="${delQty > 0 ? delQty : ''}"`;
        html += ` data-sku="${item.sku}" data-size="${s}" data-total="${totalId}"`;
        html += ` onchange="saveDelivery(this)" /></td>`;
      });
      html += '</tr>';
    });

    html += '</tbody></table></div>';
    tDiv.innerHTML = html;
    div.appendChild(tDiv);
  });

  return { table: div };
}

// 納品済の数量変更を保存
async function saveDelivery(inputEl) {
  const sku = inputEl.dataset.sku;
  const size = inputEl.dataset.size;
  const quantity = parseInt(inputEl.value, 10) || 0;
  try {
    const res = await fetch('/api/deliveries', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sku, size, quantity })
    });
    cachedDeliveries = await res.json();
    // 空欄/0は実際に削除（空欄表示に統一）
    if (quantity === 0) inputEl.value = '';
    // 合計を更新
    const totalId = inputEl.dataset.total;
    const totalEl = document.getElementById(totalId);
    if (totalEl) {
      const rowSum = Array.from(document.querySelectorAll(`.delivery-input[data-sku="${sku}"]`))
        .reduce((s, el) => s + (parseInt(el.value, 10) || 0), 0);
      totalEl.textContent = rowSum;
    }
    // セルのスタイル更新
    if (quantity > 0) inputEl.parentElement.classList.add('has-value');
    else inputEl.parentElement.classList.remove('has-value');
    // 納品済タブのヘッダーラベルを更新
    const total = (cachedDeliveries || []).reduce((s, d) => s + (d.quantity || 0), 0);
    const header = document.getElementById('ch-delivered');
    if (header) header.innerHTML = `<span class="collapse-icon">▼</span> 納品済（${total}足）`;
  } catch (e) {
    alert('納品済の保存に失敗しました');
  }
}

// =============================================
// 仕入指示フロー（管理者側）
// 未指示テーブルに直接+/-を表示、ヘッダーボタンが赤くなったら拠点選択→確定
// =============================================
let instSelections = {}; // {sku: {size: qty}}
let cachedSettings = null;

// 未指示テーブル（+/-付き）を構築
function buildUnassignedTable(items) {
  instSelections = {}; // 選択リセット

  const unisexItems = items.filter(g => g.sizeType !== 'womens');
  const womensItems = items.filter(g => g.sizeType === 'womens');

  const div = document.createElement('div');
  const tables = [];
  if (unisexItems.length > 0) tables.push({ items: unisexItems, sizes: UNISEX_SIZES, label: 'SIZE (UNISEX)' });
  if (womensItems.length > 0) tables.push({ items: womensItems, sizes: WOMENS_SIZES, label: "SIZE (WOMEN'S)" });

  if (tables.length === 0) {
    div.innerHTML = '<div class="no-orders">データなし</div>';
    return { table: div };
  }

  let rowNum = 1;
  tables.forEach(({ items: tItems, sizes, label }) => {
    const tDiv = document.createElement('div');
    tDiv.className = 'finance-spreadsheet';
    let html = '<div class="spreadsheet-scroll"><table>';
    html += `<thead><tr>
      <th class="col-no">No</th><th class="col-product">Products</th>
      <th class="col-color">Color</th><th class="col-sku">Style Code</th>
      <th class="col-qty">QTY</th>
      <th class="col-size-group" colspan="${sizes.length}">${label}</th>
    </tr><tr>
      <th class="col-no"></th><th class="col-product"></th><th class="col-color"></th>
      <th class="col-sku"></th><th class="col-qty"></th>`;
    sizes.forEach(s => html += `<th class="col-size">${s}</th>`);
    html += '</tr></thead><tbody>';

    tItems.forEach(item => {
      const pairs = Object.values(item.sizes).reduce((s, q) => s + q, 0);
      html += `<tr>
        <td class="col-no">${rowNum++}</td>
        <td class="col-product">${item.model}</td>
        <td class="col-color">${item.colorway}</td>
        <td class="col-sku">${item.sku}</td>
        <td class="col-qty">${pairs}</td>`;

      sizes.forEach(s => {
        const qty = item.sizes[s] || 0;
        if (qty > 0) {
          const safeId = item.sku.replace(/[^a-zA-Z0-9]/g, '_') + '-' + s.replace(/[^a-zA-Z0-9.]/g, '_');
          html += `<td class="col-size has-value inst-cell">
            <div class="inst-picker">
              <button class="inst-minus" onclick="instAdjust('${item.sku}','${s}',-1,${qty})">-</button>
              <span class="inst-val" id="inst-v-${safeId}">0</span>
              <button class="inst-plus" onclick="instAdjust('${item.sku}','${s}',1,${qty})">+</button>
            </div>
            <div class="inst-max">${qty}</div>
          </td>`;
        } else {
          html += `<td class="col-size"></td>`;
        }
      });
      html += '</tr>';
    });

    html += '</tbody></table></div>';
    tDiv.innerHTML = html;
    div.appendChild(tDiv);
  });

  return { table: div };
}

// 数量調整（未指示テーブル上で直接）
function instAdjust(sku, size, delta, max) {
  if (!instSelections[sku]) instSelections[sku] = {};
  const current = instSelections[sku][size] || 0;
  const newVal = Math.max(0, Math.min(max, current + delta));
  instSelections[sku][size] = newVal;

  const safeId = sku.replace(/[^a-zA-Z0-9]/g, '_') + '-' + size.replace(/[^a-zA-Z0-9.]/g, '_');
  const el = document.getElementById(`inst-v-${safeId}`);
  if (el) {
    el.textContent = newVal;
    el.classList.toggle('selected', newVal > 0);
  }

  // 選択数に応じて仕入指示ボタンの色を変更
  updateInstButton();
}

// ビルディングモード（1つの仕入指示に複数ブロック追加）
let instBuilding = false;
let instBuildingLoc = null; // {id, name}
let instBuildingBlocks = []; // [{name:'仕入A', items:[{sku,model,colorway,image,sizeType,sizes}]}]

// 選択合計を取得
function getInstSelectionTotal() {
  return Object.values(instSelections).reduce((sum, sizes) =>
    sum + Object.values(sizes).reduce((s, q) => s + q, 0), 0);
}

// 仕入指示ボタンの色を更新
function updateInstButton() {
  const btn = document.getElementById('btn-inst');
  if (!btn) return;
  const totalSelected = getInstSelectionTotal();
  const buildingTotal = instBuildingBlocks.reduce((sum, block) =>
    sum + block.items.reduce((s, item) => s + Object.values(item.sizes).reduce((a,v)=>a+v,0), 0), 0);

  if (instBuilding) {
    btn.className = 'danger-btn';
    btn.textContent = totalSelected > 0
      ? `仕入指示 作成中（+${totalSelected}足）`
      : `仕入指示 作成中（${buildingTotal}足）`;
  } else if (totalSelected > 0) {
    btn.className = 'danger-btn';
    btn.textContent = `仕入指示（${totalSelected}足）`;
  } else {
    btn.className = 'primary-btn';
    btn.textContent = '仕入指示';
  }
}

// ビルディングモード中の選択済みアイテムを集計（未指示計算用）
function getInstructedIncludingBuilding() {
  const items = calcInstructedItems(cachedInstructions);
  instBuildingBlocks.forEach(block => {
    block.items.forEach(bItem => {
      let existing = items.find(i => i.sku === bItem.sku);
      if (!existing) {
        existing = { model: bItem.model, colorway: bItem.colorway, sku: bItem.sku, sizeType: bItem.sizeType, sizes: {} };
        items.push(existing);
      }
      Object.entries(bItem.sizes).forEach(([size, qty]) => {
        existing.sizes[size] = (existing.sizes[size] || 0) + qty;
      });
    });
  });
  return items;
}

// 現在の選択をブロックとしてビルディングに追加
function addCurrentSelectionAsBlock() {
  const cleaned = {};
  Object.entries(instSelections).forEach(([sku, sizes]) => {
    const filtered = {};
    Object.entries(sizes).forEach(([size, qty]) => {
      if (qty > 0) filtered[size] = qty;
    });
    if (Object.keys(filtered).length > 0) cleaned[sku] = filtered;
  });
  if (Object.keys(cleaned).length === 0) return false;

  const blockLetter = String.fromCharCode(65 + instBuildingBlocks.length);
  const skuInfo = {};
  products.forEach(p => {
    (p.variants || []).forEach(v => {
      skuInfo[v.sku] = { model: p.model, colorway: v.colorway, image: v.image, sizeType: v.sizeType || p.sizeType || 'mens' };
    });
  });

  instBuildingBlocks.push({
    name: `仕入${blockLetter}`,
    items: Object.entries(cleaned).map(([sku, sizes]) => ({
      sku,
      model: (skuInfo[sku] || {}).model || '',
      colorway: (skuInfo[sku] || {}).colorway || '',
      image: (skuInfo[sku] || {}).image || '',
      sizeType: (skuInfo[sku] || {}).sizeType || 'mens',
      sizes
    }))
  });
  instSelections = {};
  return true;
}

// 仕入指示ボタンクリック
function openInstructionFlow() {
  const totalSelected = getInstSelectionTotal();

  if (!instBuilding && totalSelected === 0) {
    alert('未指示テーブルで仕入するアイテムを+/-で選択してください');
    return;
  }

  document.getElementById('modal-instruction').classList.add('active');

  if (!instBuilding) {
    // 新規: まず拠点を選択
    showLocationPickerModal();
  } else {
    // ビルディング中: 選択があれば追加してサマリー表示
    if (totalSelected > 0) {
      addCurrentSelectionAsBlock();
    }
    showBuildingSummary();
  }
}

function closeInstructionModal() {
  document.getElementById('modal-instruction').classList.remove('active');
}

// 拠点選択画面（初回のみ）
async function showLocationPickerModal() {
  try {
    const res = await fetch('/api/settings');
    cachedSettings = await res.json();
  } catch (e) {}

  const settings = cachedSettings || { locations: [] };
  const body = document.getElementById('instruction-modal-body');
  document.getElementById('instruction-modal-title').textContent = '仕入指示 - 拠点を選択';

  let html = '<div class="inst-step"><div class="inst-loc-grid">';
  settings.locations.forEach(loc => {
    html += `<button class="inst-loc-btn" onclick="instPickLocation('${loc.id}','${loc.name}')">${loc.name}</button>`;
  });
  if (settings.locations.length === 0) {
    html += '<p>拠点が登録されていません。詳細設定から追加してください。</p>';
  }
  html += '</div>';
  html += '<div style="margin-top:16px"><button class="secondary-btn" onclick="closeInstructionModal()">キャンセル</button></div>';
  html += '</div>';
  body.innerHTML = html;
}

// 拠点選択 → ビルディングモード開始
function instPickLocation(locId, locName) {
  instBuildingLoc = { id: locId, name: locName };
  instBuilding = true;
  addCurrentSelectionAsBlock();
  showBuildingSummary();
}

// ビルディングサマリー表示（確定/追加/キャンセル）
function showBuildingSummary() {
  const body = document.getElementById('instruction-modal-body');

  // 仕入番号を計算（この拠点の既存active指示数 + 1）
  const activeForLoc = cachedInstructions.filter(i => i.status === 'active' && i.locationId === instBuildingLoc.id);
  const instNum = activeForLoc.length + 1;
  document.getElementById('instruction-modal-title').textContent =
    `${instBuildingLoc.name}仕入 ${instNum}`;

  let html = '<div class="inst-step">';

  // ブロック一覧
  instBuildingBlocks.forEach(block => {
    const totalPairs = block.items.reduce((s, item) => s + Object.values(item.sizes).reduce((a,v)=>a+v,0), 0);
    html += `<div class="inst-block-summary">`;
    html += `<div class="block-header"><strong>${block.name}</strong>（${totalPairs}足）</div>`;
    html += '<ul>';
    block.items.forEach(item => {
      const sizePairs = Object.entries(item.sizes).map(([s,q]) => `${s} x${q}`).join(', ');
      html += `<li>${item.model} / ${item.sku} - ${sizePairs}</li>`;
    });
    html += '</ul></div>';
  });

  const totalAll = instBuildingBlocks.reduce((sum, block) =>
    sum + block.items.reduce((s, item) => s + Object.values(item.sizes).reduce((a,v)=>a+v,0), 0), 0);
  html += `<p style="margin:12px 0;font-weight:700;">合計: ${totalAll}足 / ${instBuildingBlocks.length}ブロック</p>`;

  html += '<div class="inst-actions" style="display:flex;gap:8px;flex-wrap:wrap;">';
  html += '<button class="primary-btn" onclick="instFinalize()">確定</button>';
  html += '<button class="secondary-btn" onclick="instAddMore()">追加</button>';
  html += '<button class="secondary-btn" onclick="instCancelBuilding()">キャンセル</button>';
  html += '</div></div>';

  body.innerHTML = html;
}

// 追加: モーダルを閉じて未指示テーブルに戻る
function instAddMore() {
  closeInstructionModal();
  // 未指示テーブルを再描画（ビルディング中のブロック分が引かれる）
  renderOrderAdmin(cachedOrders, cachedPurchases, cachedEffectiveRate, cachedShipments);
  updateInstButton();
}

// 確定: サーバーに保存
async function instFinalize() {
  if (instBuildingBlocks.length === 0) {
    alert('ブロックがありません');
    return;
  }

  const batches = instBuildingBlocks.map(block => ({
    id: 'batch-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5),
    name: block.name,
    items: block.items,
    status: 'pending',
    completedAt: null
  }));

  try {
    await fetch('/api/instructions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        locationId: instBuildingLoc.id,
        locationName: instBuildingLoc.name,
        batches
      })
    });
    instBuilding = false;
    instBuildingLoc = null;
    instBuildingBlocks = [];
    instSelections = {};
    closeInstructionModal();
    await showOrderAdmin();
  } catch (e) {
    alert('エラーが発生しました');
  }
}

// キャンセル: ビルディングを破棄
function instCancelBuilding() {
  if (instBuildingBlocks.length > 0 && !confirm('作成中の仕入指示を破棄しますか？')) return;
  instBuilding = false;
  instBuildingLoc = null;
  instBuildingBlocks = [];
  instSelections = {};
  closeInstructionModal();
  renderOrderAdmin(cachedOrders, cachedPurchases, cachedEffectiveRate, cachedShipments);
  updateInstButton();
}

// =============================================
// 仕入ページ（SP対応・仕入担当者用）
// =============================================
let purchaseLocationId = null;
let purchaseLocationName = null;

async function showPurchasePage(locId, locName) {
  purchaseLocationId = locId;
  purchaseLocationName = locName;
  document.getElementById('purchase-title').textContent = `仕入 - ${locName}`;
  showScreen('screen-purchase');
  await renderPurchasePage();
}

async function renderPurchasePage() {
  const container = document.getElementById('purchase-content');
  container.innerHTML = '<p>読み込み中...</p>';

  try {
    const [instrRes, prodRes] = await Promise.all([
      fetch(`/api/instructions/location/${purchaseLocationId}`),
      fetch('/api/products')
    ]);
    const instructions = await instrRes.json();
    const prods = await prodRes.json();

    // SKU情報マップ
    const skuInfo = {};
    prods.forEach(p => {
      (p.variants || []).forEach(v => {
        skuInfo[v.sku] = { model: p.model, colorway: v.colorway, image: v.image, sizeType: v.sizeType || 'mens' };
      });
    });

    // クーポンセクションを先に取得
    const couponHtml = await renderPurchaseCoupon();

    if (instructions.length === 0) {
      container.innerHTML = couponHtml + '<p style="text-align:center;padding:32px;color:#888;">現在の仕入指示はありません</p>';
      return;
    }

    // 最初の未完了指示のみ表示（仕入1）。全ブロック完了したら次の指示へ。
    const currentInst = instructions[0]; // サーバーで順番管理済み
    const instNum = 1; // 常に「仕入 1」として表示

    let html = `<div class="purchase-inst-header">仕入 ${instNum}</div>`;

    currentInst.batches.forEach(batch => {
      const isCompleted = batch.status === 'completed';
      html += `<div class="purchase-batch ${isCompleted ? 'batch-completed' : ''}">`;
      html += `<div class="batch-header">
        <span class="batch-name">${batch.name}</span>
        ${isCompleted ? '<span class="batch-done-badge">✅ 仕入済</span>' : '<span class="batch-pending-badge">未完了</span>'}
      </div>`;

      batch.items.forEach(item => {
        const info = skuInfo[item.sku] || {};
        const imgSrc = item.image || info.image || '';

        html += '<div class="purchase-item">';
        if (imgSrc) {
          html += `<div class="pi-image"><img src="${imgSrc}" alt="${item.sku}"></div>`;
        }
        html += '<div class="pi-info">';
        html += `<div class="pi-model">${item.model || info.model || ''}</div>`;
        html += `<div class="pi-sku" onclick="copySku('${item.sku}')">${item.sku} <span class="copy-hint">📋</span></div>`;
        html += `<div class="pi-color">${item.colorway || info.colorway || ''}</div>`;
        html += '<div class="pi-sizes">';
        Object.entries(item.sizes).forEach(([size, qty]) => {
          if (qty > 0) {
            // JPサイズ(cm)のみ表示（例: "8/26" → "26"）
            const jpSize = size.includes('/') ? size.split('/')[1] : size;
            for (let i = 0; i < qty; i++) {
              html += `<span class="pi-size-tag">${jpSize}</span>`;
            }
          }
        });
        html += '</div></div></div>';
      });

      if (!isCompleted) {
        html += `<button class="batch-complete-btn" onclick="completeBatch('${currentInst.id}','${batch.id}')">仕入完了にする</button>`;
      }
      // 削除ボタン（完了・未完了問わず表示）
      html += `<button class="batch-delete-btn" onclick="deleteBatch('${currentInst.id}','${batch.id}','${batch.name}', ${isCompleted})">🗑 ${batch.name} を削除</button>`;
      html += '</div>';
    });

    // 残りの指示数を表示
    if (instructions.length > 1) {
      html += `<div class="purchase-remaining">次の仕入指示が ${instructions.length - 1} 件待機中</div>`;
    }

    container.innerHTML = couponHtml + html;
  } catch (e) {
    container.innerHTML = '<p style="color:red;">読み込みエラー</p>';
  }
}

// SKUコピー
function copySku(sku) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(sku).then(() => {
      showToast('SKUをコピーしました');
    });
  } else {
    const ta = document.createElement('textarea');
    ta.value = sku;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('SKUをコピーしました');
  }
}

// バッチ完了
async function completeBatch(instructionId, batchId) {
  if (!confirm('このバッチの仕入を完了しますか？')) return;

  try {
    const res = await fetch(`/api/instructions/${instructionId}/batches/${batchId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) {
      const err = await res.json();
      alert(err.error || 'エラーが発生しました');
      return;
    }
    showToast('仕入完了しました');
    await renderPurchasePage();
  } catch (e) {
    alert('通信エラーが発生しました');
  }
}

// バッチ削除
async function deleteBatch(instructionId, batchId, batchName, isCompleted) {
  const msg = isCompleted
    ? `「${batchName}」を削除しますか？\n仕入済みデータも取り消されます。`
    : `「${batchName}」を削除しますか？`;
  if (!confirm(msg)) return;

  try {
    const res = await fetch(`/api/instructions/${instructionId}/batches/${batchId}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const err = await res.json();
      alert(err.error || 'エラーが発生しました');
      return;
    }
    showToast(`${batchName} を削除しました`);
    // 現在の画面に応じてリロード
    const currentScreen = document.querySelector('.screen.active')?.id;
    if (currentScreen === 'screen-order-admin') {
      await showOrderAdmin();
    } else {
      await renderPurchasePage();
    }
  } catch (e) {
    alert('通信エラーが発生しました');
  }
}

// =============================================
// 収支管理ページ（仕入履歴タブ）
// =============================================
let currentFinanceTab = 'overview';

async function showFinance() {
  showScreen('screen-finance');
  await showFinanceTab('history');
}

async function showFinanceTab(tab) {
  currentFinanceTab = tab;
  document.querySelectorAll('#screen-finance .tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.id === `fin-tab-${tab}`);
  });

  const content = document.getElementById('finance-content');

  if (tab === 'overview') {
    await renderFinanceOverview(content);
  } else if (tab === 'history') {
    await renderPurchaseHistory(content);
  }
}

// =============================================
// 収支管理：概要タブ（月別実績＋発送ごとの収支テーブル）
// =============================================
async function renderFinanceOverview(container) {
  container.innerHTML = '<p>読み込み中...</p>';

  try {
    // 必要データを並列取得
    await loadProducts();
    await fetchExchangeRate();
    const [shipmentsRes, settingsRes] = await Promise.all([
      fetch('/api/shipments'), fetch('/api/settings')
    ]);
    const allShipments = await shipmentsRes.json();
    const settings = await settingsRes.json();

    // 収支管理は発送完了分のみ表示（発送待ちは除外）
    const shipments = allShipments.filter(s => !s.pendingShipment);
    if (shipments.length === 0) {
      container.innerHTML = '<div class="no-orders" style="padding:20px">発送データがありません</div>';
      return;
    }

    // 収支計算用パラメータ
    const purchasePriceMap = {};
    const supplierUrlMap = {};
    products.forEach(p => {
      p.variants.forEach(v => {
        purchasePriceMap[v.sku] = v.purchasePrice || 0;
        supplierUrlMap[v.sku] = v.supplierUrl || '';
      });
    });
    const coupon = settings.couponPerPair || 0;
    const customsUnit = settings.customsUnitPrice || 0;
    const customsPerPair = Math.round(customsUnit * 0.155);
    const shippingPerPair = settings.shippingPerPair || 0;
    const fallbackRate = currentExchangeRate - 1; // exchangeRate未保存の発送用フォールバック

    // 商品マスタ情報マップ
    const productInfoMap = {};
    products.forEach(p => {
      p.variants.forEach(v => {
        productInfoMap[v.sku] = { model: p.model, colorway: v.colorway, price: v.price, sizeType: v.sizeType };
      });
    });

    // 発送を月でグルーピング（JST）
    const monthGroups = {};
    shipments.forEach(s => {
      const dateJST = new Date(new Date(s.createdAt).getTime() + 9 * 60 * 60 * 1000);
      const monthKey = dateJST.toISOString().substring(0, 7); // YYYY-MM
      if (!monthGroups[monthKey]) monthGroups[monthKey] = [];
      monthGroups[monthKey].push(s);
    });

    // 年・月フィルター選択肢
    const sortedMonthKeys = Object.keys(monthGroups).sort((a, b) => b.localeCompare(a));
    const yearSet = new Set();
    const monthSetByYear = {};
    sortedMonthKeys.forEach(mk => {
      const y = mk.substring(0, 4);
      const m = mk.substring(5, 7);
      yearSet.add(y);
      if (!monthSetByYear[y]) monthSetByYear[y] = new Set();
      monthSetByYear[y].add(m);
    });
    const yearOptions = [...yearSet].sort((a, b) => b.localeCompare(a));
    const initialYear = yearOptions[0];

    // フィルターHTML
    let yearHtml = '';
    yearOptions.forEach(y => { yearHtml += `<option value="${y}">${y}</option>`; });
    let monthHtml = '<option value="all">All</option>';
    if (initialYear && monthSetByYear[initialYear]) {
      [...monthSetByYear[initialYear]].sort((a, b) => b.localeCompare(a)).forEach(m => {
        const label = new Date(initialYear, parseInt(m) - 1).toLocaleDateString('en-US', { month: 'long' });
        monthHtml += `<option value="${m}">${label}</option>`;
      });
    }
    window._financeMonthsByYear = monthSetByYear;

    container.innerHTML = '';

    // フィルターバー
    const filterBar = document.createElement('div');
    filterBar.className = 'order-log-header';
    filterBar.innerHTML = `
      <h3>月別実績</h3>
      <div class="order-log-filters">
        <select id="finance-year" onchange="updateFinanceMonthFilter()">${yearHtml}</select>
        <select id="finance-month" onchange="filterFinanceOverview()">${monthHtml}</select>
      </div>`;
    container.appendChild(filterBar);

    // 月ごとにセクション生成
    const overviewBody = document.createElement('div');
    overviewBody.id = 'finance-overview-body';

    sortedMonthKeys.forEach(monthKey => {
      const monthShipments = monthGroups[monthKey];
      const [y, m] = monthKey.split('-');
      const monthLabel = new Date(y, parseInt(m) - 1).toLocaleDateString('en-US', { year: 'numeric', month: 'long' });

      const monthSection = document.createElement('div');
      monthSection.className = 'finance-month-section';
      monthSection.dataset.year = y;
      monthSection.dataset.month = m;

      // --- 月合計：各発送の固定レートを使って合算 ---
      // 発送ごとの収支を先に計算し、その合計を月合計とする
      const shipmentResults = [];
      const sortedShipments = [...monthShipments].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      sortedShipments.forEach(s => {
        const shipRate = s.exchangeRate ? (s.exchangeRate - 1) : fallbackRate;
        const sItems = [];
        s.items.forEach(i => {
          const info = productInfoMap[i.sku] || {};
          sItems.push({
            sku: i.sku, size: i.size, quantity: i.quantity,
            sizeType: i.sizeType || info.sizeType || 'unisex',
            model: i.model || info.model || '',
            colorway: i.colorway || info.colorway || '',
            price: info.price || 0
          });
        });
        const grouped = groupItemsBySku(sItems);
        grouped.forEach(item => { if (!item.price && productInfoMap[item.sku]) item.price = productInfoMap[item.sku].price; });
        const result = buildFinanceTable(sortItemsBySkuOrder(grouped), shipRate, purchasePriceMap, supplierUrlMap, coupon, customsPerPair, shippingPerPair);
        shipmentResults.push({ shipment: s, result, rate: shipRate });
      });

      // 月合計 = 各発送のtotalsを合算
      const monthTotals = { pairs: 0, amountUsd: 0, purchase: 0, couponTotal: 0, purchaseTotal: 0, customs: 0, shipping: 0, revenue: 0, profit: 0 };
      shipmentResults.forEach(({ result }) => {
        Object.keys(monthTotals).forEach(k => { monthTotals[k] += result.totals[k]; });
      });

      const monthHeader = document.createElement('div');
      monthHeader.className = 'order-table-header';
      monthHeader.innerHTML = `<h4>${monthLabel} — Monthly Total</h4>`;
      monthSection.appendChild(monthHeader);

      const monthTotalsDiv = buildFinanceTotals(monthTotals);
      const monthWrapper = document.createElement('div');
      monthWrapper.className = 'order-table-wrapper';
      monthWrapper.appendChild(monthTotalsDiv);
      monthSection.appendChild(monthWrapper);

      // --- 各発送ごとのテーブル（事前計算済みshipmentResultsを使用）---
      shipmentResults.forEach(({ shipment: s, result, rate: shipRate }) => {
        const dateJST = new Date(new Date(s.createdAt).getTime() + 9 * 60 * 60 * 1000);
        const dateStr = dateJST.toISOString().split('T')[0];
        const shipPairs = s.items.reduce((sum, i) => sum + i.quantity, 0);

        // 支払ステータス
        const paidBadge = s.paid
          ? '<span class="paid-badge">Paid</span>'
          : '<span class="unpaid-badge">Unpaid</span>';

        // 追跡番号（同一キャリアごとに横並び）
        const trackingHtml = buildTrackingDisplay(s.tracking || []);

        // 為替レート表示
        const rateDisplay = s.exchangeRate
          ? `USD/JPY: ¥${shipRate.toFixed(1)}（実勢 ¥${s.exchangeRate.toFixed(1)} - ¥1）`
          : `USD/JPY: ¥${shipRate.toFixed(1)}（※発送時レート未記録）`;

        const shipHeader = document.createElement('div');
        shipHeader.className = 'order-table-header';
        shipHeader.innerHTML = `<h4>Shipped: ${dateStr}（${shipPairs}足）${paidBadge}</h4>
          ${trackingHtml ? `<div class="tracking-info-inline">${trackingHtml}</div>` : ''}
          <div class="exchange-rate-info">${rateDisplay}</div>`;

        const shipWrapper = document.createElement('div');
        shipWrapper.className = 'order-table-wrapper';
        shipWrapper.style.marginTop = '16px';
        shipWrapper.appendChild(shipHeader);
        shipWrapper.appendChild(result.table);
        shipWrapper.appendChild(buildFinanceTotals(result.totals));
        monthSection.appendChild(shipWrapper);
      });

      overviewBody.appendChild(monthSection);
    });

    container.appendChild(overviewBody);
  } catch (e) {
    container.innerHTML = '<p style="color:red;">読み込みエラー</p>';
    console.error(e);
  }
}

// 概要タブのフィルター
function filterFinanceOverview() {
  const year = document.getElementById('finance-year').value;
  const month = document.getElementById('finance-month').value;
  document.querySelectorAll('.finance-month-section').forEach(el => {
    const elYear = el.dataset.year;
    const elMonth = el.dataset.month;
    const yearMatch = elYear === year;
    const monthMatch = month === 'all' || elMonth === month;
    el.style.display = (yearMatch && monthMatch) ? '' : 'none';
  });
}

function updateFinanceMonthFilter() {
  const year = document.getElementById('finance-year').value;
  const monthSelect = document.getElementById('finance-month');
  const months = window._financeMonthsByYear[year] || new Set();
  let html = '<option value="all">All</option>';
  [...months].sort((a, b) => b.localeCompare(a)).forEach(m => {
    const label = new Date(year, parseInt(m) - 1).toLocaleDateString('en-US', { month: 'long' });
    html += `<option value="${m}">${label}</option>`;
  });
  monthSelect.innerHTML = html;
  filterFinanceOverview();
}

async function renderPurchaseHistory(container) {
  container.innerHTML = '<p>読み込み中...</p>';

  try {
    const [purchasesRes, settingsRes] = await Promise.all([
      fetch('/api/purchases'),
      fetch('/api/settings')
    ]);
    const purchases = await purchasesRes.json();
    const settings = await settingsRes.json();

    if (purchases.length === 0) {
      container.innerHTML = '<div class="no-orders" style="padding:20px">仕入履歴はありません</div>';
      return;
    }

    // 日付ごとにグループ化（JST）
    const byDate = {};
    purchases.forEach(p => {
      const dateJST = new Date(new Date(p.createdAt).getTime() + 9 * 60 * 60 * 1000).toISOString().split('T')[0];
      if (!byDate[dateJST]) byDate[dateJST] = [];
      byDate[dateJST].push(p);
    });

    // 月ごとの合計を計算
    const byMonth = {};
    Object.entries(byDate).forEach(([date, items]) => {
      const month = date.substring(0, 7); // YYYY-MM
      if (!byMonth[month]) byMonth[month] = {};
      items.forEach(p => {
        const locName = p.locationName || '不明';
        if (!byMonth[month][locName]) byMonth[month][locName] = 0;
        p.items.forEach(item => {
          byMonth[month][locName] += item.quantity;
        });
      });
    });

    let html = '';

    // 月別サマリー
    html += '<div class="history-section"><h3>月別サマリー</h3>';
    html += '<table class="history-summary-table"><thead><tr><th>月</th><th>拠点</th><th>仕入数</th></tr></thead><tbody>';
    Object.entries(byMonth).sort((a,b) => b[0].localeCompare(a[0])).forEach(([month, locs]) => {
      let first = true;
      const locEntries = Object.entries(locs);
      const totalPairs = locEntries.reduce((s, [_, q]) => s + q, 0);
      locEntries.forEach(([locName, pairs]) => {
        html += `<tr>`;
        if (first) {
          html += `<td rowspan="${locEntries.length + 1}" class="month-cell">${month}</td>`;
          first = false;
        }
        html += `<td>${locName}</td><td>${pairs}足</td></tr>`;
      });
      html += `<tr class="month-total"><td><strong>合計</strong></td><td><strong>${totalPairs}足</strong></td></tr>`;
    });
    html += '</tbody></table></div>';

    // 日別詳細（新しい順）
    html += '<div class="history-section"><h3>日別詳細</h3>';
    Object.entries(byDate).sort((a,b) => b[0].localeCompare(a[0])).forEach(([date, items]) => {
      const totalPairs = items.reduce((s, p) => s + p.items.reduce((ss, i) => ss + i.quantity, 0), 0);
      html += `<div class="history-date-group">`;
      html += `<div class="history-date-header">${date}（${totalPairs}足）</div>`;

      items.forEach(p => {
        const time = new Date(new Date(p.createdAt).getTime() + 9 * 60 * 60 * 1000).toISOString().substring(11, 16);
        const pairCount = p.items.reduce((s, i) => s + i.quantity, 0);
        html += `<div class="history-entry">`;
        html += `<div class="he-header"><span class="he-time">${time}</span> <span class="he-loc">${p.locationName}</span>`;
        if (p.batchName) html += ` <span class="he-batch">${p.batchName}</span>`;
        html += ` <span class="he-pairs">${pairCount}足</span></div>`;
        html += '<div class="he-items">';
        p.items.forEach(item => {
          html += `<span class="he-item">${item.sku} ${item.size} x${item.quantity}</span>`;
        });
        html += '</div></div>';
      });

      html += '</div>';
    });
    html += '</div>';

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = '<p style="color:red;">読み込みエラー</p>';
  }
}

// =============================================
// 発送管理
// =============================================
let shipLocData = {};
let shipSelectedLocs = {};
let shipMode = false;
let shipAdjustments = {};
let shipItems = [];

async function showShipping() {
  showScreen('screen-shipping');
  await showShippingTab('ship');
}

async function showShippingTab(tab) {
  document.getElementById('ship-tab-ship').classList.toggle('active', tab === 'ship');
  document.getElementById('ship-tab-history').classList.toggle('active', tab === 'history');
  const content = document.getElementById('shipping-content');
  if (tab === 'ship') await renderShippingPage(content);
  else await renderShipmentHistory(content);
}

async function renderShippingPage(container) {
  container.innerHTML = '<p>読み込み中...</p>';
  shipMode = false;
  shipSelectedLocs = {};
  shipAdjustments = {};
  shipSummaryItems = []; // 発送商品一覧

  // 商品マスタ・発送可能アイテムを並列取得
  try {
    await loadProducts();
    const shipRes = await fetch('/api/shipped-items');
    shipLocData = await shipRes.json();
  } catch (e) {
    container.innerHTML = '<p style="color:red;">読み込みエラー</p>';
    return;
  }

  const locIds = Object.keys(shipLocData);

  let html = '';

  // ======= 発送商品タブ（固定ヘッダー、発送ボタン押下後に表示） =======
  html += `<div id="ship-summary-panel" style="display:none;" class="ship-summary-panel">
    <div class="ship-summary-header">
      <h3>発送商品</h3>
      <span id="ship-summary-count"></span>
    </div>
    <div id="ship-summary-table"></div>
    <div class="ship-summary-actions">
      <button class="primary-btn" onclick="confirmShipSelection()">確定</button>
      <button class="secondary-btn" onclick="cancelShipMode()">キャンセル</button>
    </div>
  </div>`;

  html += '<div class="ship-actions-bar">';
  html += '<button id="btn-ship-start" class="primary-btn" onclick="startShipMode()">発送</button>';
  html += '</div>';

  if (locIds.length === 0) {
    html += '<div class="no-orders" style="padding:20px">発送可能な仕入済アイテムはありません</div>';
  }

  // 拠点ごとの発送可能アイテム（SKU順統一、model/colorway補完）
  locIds.forEach(locId => {
    const loc = shipLocData[locId];
    // model/colorway を商品マスタから補完
    loc.items.forEach(item => {
      if (!item.model || !item.colorway) {
        for (const p of (products || [])) {
          const v = (p.variants || []).find(v => v.sku === item.sku);
          if (v) {
            if (!item.model) item.model = p.model;
            if (!item.colorway) item.colorway = v.colorway;
            if (!item.sizeType) item.sizeType = v.sizeType;
            break;
          }
        }
      }
    });
    // SKU順ソート
    loc.items = sortItemsBySkuOrder(loc.items);

    const totalPairs = loc.items.reduce((s, i) => s + Object.values(i.sizes).reduce((a,b)=>a+b,0), 0);
    html += `<div class="ship-loc-section" id="ship-loc-${locId}">`;
    html += `<div class="ship-loc-header">`;
    html += `<span class="ship-loc-check" id="ship-check-${locId}" style="display:none;">`;
    html += `<input type="checkbox" id="ship-cb-${locId}" onchange="toggleShipLoc('${locId}')">`;
    html += `</span>`;
    html += `<h3>${loc.locationName}（${totalPairs}足）</h3>`;
    html += `</div>`;
    html += `<div class="ship-loc-items" id="ship-items-${locId}">`;
    html += buildShipItemsTable(loc.items, locId, false);
    html += `</div></div>`;
  });

  container.innerHTML = html;
}

// SKU順ソート用ヘルパー（グローバルで使用）
function sortItemsBySkuOrder(items) {
  // モデル優先順位: MEXICO 66 → MEXICO 66 SD → その他
  const MODEL_PRIORITY = ['MEXICO 66', 'MEXICO 66 SD'];
  function getModelRank(model) {
    const idx = MODEL_PRIORITY.indexOf(model);
    return idx !== -1 ? idx : MODEL_PRIORITY.length;
  }
  // productsマスタの順番を基準にソート（同一モデル内の順序用）
  const skuOrder = [];
  (products || []).forEach(p => {
    (p.variants || []).forEach(v => {
      if (!skuOrder.includes(v.sku)) skuOrder.push(v.sku);
    });
  });
  return [...items].sort((a, b) => {
    // まずモデル優先順位で比較
    const ma = getModelRank(a.model);
    const mb = getModelRank(b.model);
    if (ma !== mb) return ma - mb;
    // 同一モデル内はproductsマスタ順
    const ia = skuOrder.indexOf(a.sku);
    const ib = skuOrder.indexOf(b.sku);
    if (ia === -1 && ib === -1) return 0;
    if (ia === -1) return 1;
    if (ib === -1) return -1;
    return ia - ib;
  });
}

// 発送商品の合計一覧を更新
let shipSummaryItems = [];
function updateShipSummary() {
  const summaryPanel = document.getElementById('ship-summary-panel');
  const summaryTable = document.getElementById('ship-summary-table');
  const summaryCount = document.getElementById('ship-summary-count');

  // 選択中の全拠点のアイテムを集計
  const totalItems = {};
  Object.entries(shipSelectedLocs).forEach(([locId, selected]) => {
    if (!selected) return;
    const loc = shipLocData[locId];
    loc.items.forEach(item => {
      const adjs = (shipAdjustments[locId] && shipAdjustments[locId][item.sku]) || {};
      Object.entries(item.sizes).forEach(([size, maxQty]) => {
        const qty = adjs[size] !== undefined ? adjs[size] : maxQty;
        if (qty > 0) {
          if (!totalItems[item.sku]) {
            totalItems[item.sku] = { model: item.model, colorway: item.colorway, sku: item.sku, sizeType: item.sizeType, sizes: {} };
          }
          totalItems[item.sku].sizes[size] = (totalItems[item.sku].sizes[size] || 0) + qty;
        }
      });
    });
  });

  const items = sortItemsBySkuOrder(Object.values(totalItems));
  const totalPairs = items.reduce((s, i) => s + Object.values(i.sizes).reduce((a,b)=>a+b,0), 0);

  if (totalPairs === 0) {
    summaryPanel.style.display = 'none';
    return;
  }

  summaryPanel.style.display = 'block';
  summaryCount.textContent = `${totalPairs}足`;
  summaryTable.innerHTML = buildShipItemsTable(items, 'summary', false);
}

// 発送モードキャンセル
function cancelShipMode() {
  shipMode = false;
  shipSelectedLocs = {};
  shipAdjustments = {};
  const summaryPanel = document.getElementById('ship-summary-panel');
  if (summaryPanel) summaryPanel.style.display = 'none';
  // チェックボックスを非表示に戻す
  Object.keys(shipLocData).forEach(locId => {
    const checkEl = document.getElementById(`ship-check-${locId}`);
    if (checkEl) checkEl.style.display = 'none';
    const cb = document.getElementById(`ship-cb-${locId}`);
    if (cb) cb.checked = false;
    const itemsEl = document.getElementById(`ship-items-${locId}`);
    if (itemsEl) itemsEl.innerHTML = buildShipItemsTable(shipLocData[locId].items, locId, false);
  });
  const btn = document.getElementById('btn-ship-start');
  if (btn) {
    btn.textContent = '発送';
    btn.disabled = false;
    btn.classList.remove('btn-disabled');
    btn.onclick = () => startShipMode();
  }
}

function buildShipItemsTable(items, locId, adjustable) {
  // オーダー管理と同じフォーマット（buildSimpleTableと統一）
  const unisexItems = items.filter(i => i.sizeType !== 'womens');
  const womensItems = items.filter(i => i.sizeType === 'womens');
  let html = '';
  const tables = [];
  if (unisexItems.length > 0) tables.push({ items: unisexItems, sizes: UNISEX_SIZES, label: 'SIZE (UNISEX)' });
  if (womensItems.length > 0) tables.push({ items: womensItems, sizes: WOMENS_SIZES, label: "SIZE (WOMEN'S)" });

  let rowNum = 1;
  tables.forEach(({ items: tItems, sizes, label }) => {
    html += buildShipSizeTable(tItems, sizes, locId, adjustable, label, rowNum);
    rowNum += tItems.length;
  });
  return html;
}

function buildShipSizeTable(items, sizes, locId, adjustable, label, startRowNum) {
  // オーダー管理のbuildSimpleTableと同じHTML構造・CSSクラスを使用
  let html = '<div class="finance-spreadsheet"><div class="spreadsheet-scroll"><table>';
  html += `<thead><tr>
    <th class="col-no">No</th><th class="col-product">Products</th>
    <th class="col-color">Color</th><th class="col-sku">Style Code</th>
    <th class="col-qty">QTY</th>
    <th class="col-size-group" colspan="${sizes.length}">${label}</th>
  </tr><tr>
    <th class="col-no"></th><th class="col-product"></th><th class="col-color"></th>
    <th class="col-sku"></th><th class="col-qty"></th>`;
  sizes.forEach(s => html += `<th class="col-size">${s}</th>`);
  html += '</tr></thead><tbody>';

  let rowNum = startRowNum || 1;
  items.forEach(item => {
    const pairs = Object.values(item.sizes).reduce((s, q) => s + q, 0);
    html += `<tr>
      <td class="col-no">${rowNum++}</td>
      <td class="col-product">${item.model || ''}</td>
      <td class="col-color">${item.colorway || ''}</td>
      <td class="col-sku">${item.sku}</td>
      <td class="col-qty">${pairs}</td>`;

    sizes.forEach(size => {
      const qty = item.sizes[size] || 0;
      if (qty > 0 && adjustable) {
        const adjKey = `${locId}|${item.sku}|${size}`;
        const currentAdj = getShipAdj(locId, item.sku, size, qty);
        html += `<td class="col-size inst-cell"><div class="inst-picker">`;
        html += `<button class="inst-minus" onclick="shipAdjust('${locId}','${item.sku}','${size}',-1,${qty})">-</button>`;
        html += `<span class="inst-val" id="ship-val-${adjKey}">${currentAdj}</span>`;
        html += `<button class="inst-plus" onclick="shipAdjust('${locId}','${item.sku}','${size}',1,${qty})">+</button>`;
        html += `</div><div class="inst-max">/${qty}</div></td>`;
      } else if (qty > 0) {
        html += `<td class="col-size has-value">${qty}</td>`;
      } else {
        html += '<td class="col-size"></td>';
      }
    });
    html += '</tr>';
  });
  html += '</tbody></table></div></div>';
  return html;
}

function getShipAdj(locId, sku, size, max) {
  if (!shipAdjustments[locId] || !shipAdjustments[locId][sku]) return max;
  return shipAdjustments[locId][sku][size] !== undefined ? shipAdjustments[locId][sku][size] : max;
}

function shipAdjust(locId, sku, size, delta, max) {
  if (!shipAdjustments[locId]) shipAdjustments[locId] = {};
  if (!shipAdjustments[locId][sku]) shipAdjustments[locId][sku] = {};
  if (shipAdjustments[locId][sku][size] === undefined) shipAdjustments[locId][sku][size] = max;
  let val = shipAdjustments[locId][sku][size] + delta;
  val = Math.max(0, Math.min(val, max));
  shipAdjustments[locId][sku][size] = val;
  const el = document.getElementById(`ship-val-${locId}|${sku}|${size}`);
  if (el) el.textContent = val;
  // 発送商品サマリーを更新
  updateShipSummary();
}

function startShipMode() {
  shipMode = true;
  Object.keys(shipLocData).forEach(locId => {
    const checkEl = document.getElementById(`ship-check-${locId}`);
    if (checkEl) checkEl.style.display = 'inline';
  });
  const btn = document.getElementById('btn-ship-start');
  btn.textContent = 'キャンセル';
  btn.disabled = false;
  btn.classList.remove('btn-disabled');
  btn.onclick = () => cancelShipMode();
}

function toggleShipLoc(locId) {
  const cb = document.getElementById(`ship-cb-${locId}`);
  shipSelectedLocs[locId] = cb.checked;
  const loc = shipLocData[locId];
  const itemsEl = document.getElementById(`ship-items-${locId}`);
  if (cb.checked) {
    if (!shipAdjustments[locId]) {
      shipAdjustments[locId] = {};
      loc.items.forEach(item => {
        shipAdjustments[locId][item.sku] = {};
        Object.entries(item.sizes).forEach(([size, qty]) => { shipAdjustments[locId][item.sku][size] = qty; });
      });
    }
    itemsEl.innerHTML = buildShipItemsTable(loc.items, locId, true);
  } else {
    delete shipAdjustments[locId];
    itemsEl.innerHTML = buildShipItemsTable(loc.items, locId, false);
  }
  // 発送商品サマリーを更新
  updateShipSummary();
}

function confirmShipSelection() {
  shipItems = [];
  const selectedLocations = [];
  Object.entries(shipSelectedLocs).forEach(([locId, selected]) => {
    if (!selected) return;
    const loc = shipLocData[locId];
    selectedLocations.push({ id: locId, name: loc.locationName });
    loc.items.forEach(item => {
      const adjs = (shipAdjustments[locId] && shipAdjustments[locId][item.sku]) || {};
      Object.entries(item.sizes).forEach(([size, maxQty]) => {
        const qty = adjs[size] !== undefined ? adjs[size] : maxQty;
        if (qty > 0) {
          shipItems.push({
            sku: item.sku, model: item.model, colorway: item.colorway,
            size, quantity: qty, sizeType: item.sizeType,
            locationId: locId, locationName: loc.locationName
          });
        }
      });
    });
  });
  if (shipItems.length === 0) { alert('発送するアイテムがありません'); return; }
  showShippingModal(selectedLocations);
}

function showShippingModal(locations) {
  document.getElementById('modal-shipping').classList.add('active');
  const body = document.getElementById('shipping-modal-body');
  const totalPairs = shipItems.reduce((s, i) => s + i.quantity, 0);
  const locNames = locations.map(l => l.name).join(' + ');
  let html = `<div class="ship-summary"><p><strong>${locNames}</strong> から <strong>${totalPairs}足</strong> を発送</p></div>`;
  html += `<div class="form-row"><label>オーダー番号（カンマ区切りで複数可）</label>`;
  html += `<input type="text" id="ship-order-nums" placeholder="例: 260329, 260330"></div>`;
  // 発送待ちチェックボックス
  html += `<div style="margin:12px 0;">
    <label style="display:inline-flex;align-items:center;gap:6px;cursor:pointer;font-size:14px;">
      <input type="checkbox" id="ship-pending-check" onchange="togglePendingShipment()" style="margin:0;">
      発送待ち状態にする（追跡番号なしで登録）
    </label>
  </div>`;
  html += `<div class="ship-tracking-section" id="ship-tracking-section"><label>追跡番号</label>`;
  html += `<div id="ship-tracking-list">${buildTrackingRow(0)}</div>`;
  html += `<button class="secondary-btn" onclick="addTrackingRow()" style="margin-top:8px">+ 追跡番号を追加</button></div>`;
  html += `<div class="form-actions" style="margin-top:16px;">`;
  html += `<button class="primary-btn" onclick="finalizeShipment()">完了</button>`;
  html += `<button class="secondary-btn" onclick="closeShippingModal()">キャンセル</button></div>`;
  body.innerHTML = html;
  body.dataset.locations = JSON.stringify(locations);
  trackingRowCount = 1;
}

let trackingRowCount = 1;
function buildTrackingRow(idx) {
  return `<div class="tracking-row" id="tracking-row-${idx}">
    <select id="ship-carrier-${idx}" class="ship-carrier-select">
      <option value="DHL">DHL</option><option value="FedEx">FedEx</option>
      <option value="UPS">UPS</option><option value="EMS">EMS</option>
      <option value="Other">その他</option>
    </select>
    <input type="text" id="ship-tracking-${idx}" placeholder="追跡番号" class="ship-tracking-input">
    ${idx > 0 ? `<button class="danger-btn-sm" onclick="removeTrackingRow(${idx})">✕</button>` : ''}
  </div>`;
}
function addTrackingRow() {
  const list = document.getElementById('ship-tracking-list');
  const div = document.createElement('div');
  div.innerHTML = buildTrackingRow(trackingRowCount);
  list.appendChild(div.firstElementChild);
  trackingRowCount++;
}
function removeTrackingRow(idx) {
  const row = document.getElementById(`tracking-row-${idx}`);
  if (row) row.remove();
}
function closeShippingModal() {
  document.getElementById('modal-shipping').classList.remove('active');
}

// 発送待ちチェック切り替え（追跡番号セクションの表示/非表示）
function togglePendingShipment() {
  const checked = document.getElementById('ship-pending-check').checked;
  const trackingSection = document.getElementById('ship-tracking-section');
  trackingSection.style.display = checked ? 'none' : '';
}

async function finalizeShipment() {
  const isPending = document.getElementById('ship-pending-check').checked;
  const tracking = [];
  if (!isPending) {
    for (let i = 0; i < trackingRowCount; i++) {
      const carrierEl = document.getElementById(`ship-carrier-${i}`);
      const trackEl = document.getElementById(`ship-tracking-${i}`);
      if (carrierEl && trackEl && trackEl.value.trim()) {
        tracking.push({ carrier: carrierEl.value, trackingNumber: trackEl.value.trim() });
      }
    }
    if (tracking.length === 0) { alert('追跡番号を入力してください'); return; }
  }
  const orderNumsStr = document.getElementById('ship-order-nums').value.trim();
  const orderNumbers = orderNumsStr ? orderNumsStr.split(',').map(s => s.trim()).filter(Boolean) : [];
  const locations = JSON.parse(document.getElementById('shipping-modal-body').dataset.locations);
  try {
    const shipRes = await fetch('/api/shipments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: shipItems, locations, tracking, orderNumbers, exchangeRate: currentExchangeRate, pendingShipment: isPending })
    });
    const shipResult = await shipRes.json();

    // バイヤー情報があればWhatsAppボタンを表示
    if (shipResult.buyers && shipResult.buyers.length > 0) {
      showShipmentCompleteWithWhatsApp(shipResult, tracking);
    } else {
      closeShippingModal();
      showToast('発送が完了しました');
      await showShippingTab('ship');
    }
  } catch (e) { alert('通信エラー'); }
}

// WhatsApp通知画面（発送完了後）
function buildWhatsAppUrl(buyer, tracking) {
  const trackingText = tracking.map(t => `${t.carrier}: ${t.trackingNumber}`).join('\n');
  const message = `Hi ${buyer.name},

Your order has been shipped!

Tracking:
${trackingText}

You can view your order history here:
http://localhost:3000

Thank you!`;
  const phone = buyer.phone.replace(/[^0-9]/g, '');
  return `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
}

function showShipmentCompleteWithWhatsApp(shipResult, tracking) {
  const body = document.getElementById('shipping-modal-body');
  let html = `<div style="text-align:center;padding:20px 0;">
    <div style="font-size:40px;margin-bottom:12px;">✅</div>
    <h3 style="margin:0 0 20px;">発送が完了しました</h3>
    <p style="color:#666;font-size:13px;margin-bottom:20px;">WhatsAppでバイヤーに通知を送信できます</p>`;

  shipResult.buyers.forEach(buyer => {
    const waUrl = buildWhatsAppUrl(buyer, tracking);
    html += `<a href="${waUrl}" target="_blank" class="whatsapp-btn">
      <span class="whatsapp-icon">💬</span> ${buyer.name} に通知を送る
    </a>`;
  });

  html += `<button class="secondary-btn" style="margin-top:20px;width:100%;" onclick="closeShipmentComplete()">閉じる</button>`;
  html += `</div>`;
  body.innerHTML = html;
}

async function closeShipmentComplete() {
  closeShippingModal();
  await showShippingTab('ship');
}

// =============================================
// 発送履歴
// =============================================
// 発送履歴のまとめ選択用
let mergeSelectMode = false;
let mergeSelected = {};

async function renderShipmentHistory(container) {
  container.innerHTML = '<p>読み込み中...</p>';
  await loadProducts();
  mergeSelectMode = false;
  mergeSelected = {};

  // 商品マスタからmodel/colorway補完用マップ
  const productInfoMap = {};
  (products || []).forEach(p => {
    (p.variants || []).forEach(v => {
      productInfoMap[v.sku] = { model: p.model, colorway: v.colorway, sizeType: v.sizeType, price: v.price || 0 };
    });
  });

  try {
    const res = await fetch('/api/shipments');
    const shipments = await res.json();
    if (shipments.length === 0) {
      container.innerHTML = '<div class="no-orders" style="padding:20px">発送履歴はありません</div>';
      return;
    }

    let html = '';

    // まとめボタン
    if (shipments.length > 1) {
      html += `<div class="ship-actions-bar">
        <button id="btn-merge-mode" class="secondary-btn" onclick="toggleMergeMode()">発送をまとめる</button>
        <button id="btn-merge-exec" class="primary-btn" style="display:none" onclick="executeMerge()">選択した発送をまとめる</button>
      </div>`;
    }

    [...shipments].reverse().forEach(s => {
      const dateJST = new Date(new Date(s.createdAt).getTime() + 9 * 60 * 60 * 1000);
      const dateStr = dateJST.toISOString().split('T')[0];
      const timeStr = dateJST.toISOString().substring(11, 16);
      const totalPairs = s.items.reduce((sum, i) => sum + i.quantity, 0);
      // 合計販売金額を計算
      let totalSalesAmount = 0;
      s.items.forEach(i => {
        const info = productInfoMap[i.sku] || {};
        const price = i.price || info.price || 0;
        totalSalesAmount += price * i.quantity;
      });
      const locNames = s.locations.map(l => l.name).join(' + ');

      const isPending = s.pendingShipment;
      html += `<div class="shipment-card ${isPending ? 'shipment-pending' : ''}" id="shipment-card-${s.id}">`;

      // まとめ選択チェックボックス（非表示デフォルト）
      html += `<span class="merge-check" id="merge-check-${s.id}" style="display:none;">
        <input type="checkbox" id="merge-cb-${s.id}" onchange="toggleMergeSelect('${s.id}')">
      </span>`;

      // ヘッダー: 合計を上に表示
      html += `<div class="shipment-header">`;
      html += `<div class="shipment-date">${dateStr} ${timeStr}`;
      if (isPending) html += ` <span class="pending-ship-badge">発送待ち</span>`;
      else html += ` <span class="shipped-badge">発送完了</span>`;
      html += `</div>`;
      html += `<div class="shipment-summary">${locNames} / ${totalPairs}足 / $${totalSalesAmount.toLocaleString()}</div>`;
      if (s.tracking && s.tracking.length > 0) {
        html += `<div class="shipment-tracking-brief">`;
        s.tracking.forEach(t => {
          html += `<span class="tracking-badge">${t.carrier}: ${t.trackingNumber}</span>`;
        });
        html += `</div>`;
      }
      if (s.orderNumbers && s.orderNumbers.length > 0) {
        html += `<div class="shipment-orders">Order: ${s.orderNumbers.join(', ')}</div>`;
      }
      // 発送状態切替ボタン + 支払状態ボタン + 追跡番号編集ボタン
      const isPaid = s.paid;
      html += `<div class="shipment-actions" style="margin-top:4px;display:flex;gap:8px;flex-wrap:wrap;">`;
      if (isPending) {
        html += `<button class="small-btn shipped-btn" onclick="toggleShipmentPending('${s.id}', false)">発送完了にする</button>`;
      } else {
        html += `<button class="small-btn pending-btn" onclick="toggleShipmentPending('${s.id}', true)">発送待ちに戻す</button>`;
      }
      html += `<button class="small-btn ${isPaid ? 'paid-btn' : 'unpaid-btn'}" onclick="toggleShipmentPaid('${s.id}', ${!isPaid})">${isPaid ? '✅ 支払済み' : '❌ 未払い → 支払済みにする'}</button>`;
      html += `<button class="small-btn" onclick="editShipmentTracking('${s.id}')">追跡番号を編集</button>`;
      html += `</div>`;
      html += `</div>`;

      // 合計テーブル（常に表示）
      // アイテムにmodel/colorway補完
      s.items.forEach(i => {
        if ((!i.model || !i.colorway) && productInfoMap[i.sku]) {
          if (!i.model) i.model = productInfoMap[i.sku].model;
          if (!i.colorway) i.colorway = productInfoMap[i.sku].colorway;
          if (!i.sizeType) i.sizeType = productInfoMap[i.sku].sizeType;
        }
      });
      html += buildShipmentDetailTable(s.items);

      // 拠点内訳（プルダウン）
      if (s.locations.length > 1) {
        html += `<details class="shipment-loc-details">
          <summary class="shipment-loc-summary">拠点別内訳を表示</summary>`;
        s.locations.forEach(loc => {
          const locItems = s.items.filter(i => i.locationId === loc.id);
          if (locItems.length === 0) return;
          const locPairs = locItems.reduce((sum, i) => sum + i.quantity, 0);
          html += `<div class="shipment-loc-group">
            <div class="shipment-loc-name">${loc.name}（${locPairs}足）</div>
            ${buildShipmentDetailTable(locItems)}
          </div>`;
        });
        html += `</details>`;
      }

      html += `</div>`;
    });
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = '<p style="color:red;">読み込みエラー (発送履歴)</p>';
  }
}

// 支払状態を切り替え
async function toggleShipmentPaid(shipmentId, paid) {
  try {
    const res = await fetch(`/api/shipments/${shipmentId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ paid })
    });
    if (!res.ok) { alert('更新に失敗しました'); return; }
    showToast(paid ? '支払済みに変更しました' : '未払いに変更しました');
    // 履歴を再描画
    const historyContent = document.getElementById('shipping-history-content');
    if (historyContent) await renderShipmentHistory(historyContent);
  } catch (e) {
    alert('通信エラーが発生しました');
  }
}

// 発送待ち状態を切り替え
async function toggleShipmentPending(shipmentId, pending) {
  try {
    const res = await fetch(`/api/shipments/${shipmentId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pendingShipment: pending })
    });
    if (!res.ok) { alert('更新に失敗しました'); return; }
    showToast(pending ? '発送待ちに変更しました' : '発送完了にしました');
    const content = document.getElementById('shipping-content');
    if (content) await renderShipmentHistory(content);
  } catch (e) {
    alert('通信エラーが発生しました');
  }
}

// 追跡番号編集
async function editShipmentTracking(shipmentId) {
  const res = await fetch('/api/shipments');
  const shipments = await res.json();
  const shipment = shipments.find(s => s.id === shipmentId);
  if (!shipment) return;

  const body = document.getElementById('shipping-modal-body');
  document.getElementById('shipping-modal-title').textContent = '追跡番号を編集';
  let html = '<div class="ship-tracking-section">';
  html += `<div id="edit-tracking-list">`;
  shipment.tracking.forEach((t, i) => {
    html += `<div class="tracking-row" id="edit-tracking-row-${i}">
      <select id="edit-carrier-${i}" class="ship-carrier-select">
        <option value="DHL" ${t.carrier === 'DHL' ? 'selected' : ''}>DHL</option>
        <option value="FedEx" ${t.carrier === 'FedEx' ? 'selected' : ''}>FedEx</option>
        <option value="UPS" ${t.carrier === 'UPS' ? 'selected' : ''}>UPS</option>
        <option value="EMS" ${t.carrier === 'EMS' ? 'selected' : ''}>EMS</option>
        <option value="Other" ${!['DHL','FedEx','UPS','EMS'].includes(t.carrier) ? 'selected' : ''}>その他</option>
      </select>
      <input type="text" id="edit-tracking-${i}" value="${t.trackingNumber}" class="ship-tracking-input">
      ${i > 0 ? `<button class="danger-btn-sm" onclick="document.getElementById('edit-tracking-row-${i}').remove()">✕</button>` : ''}
    </div>`;
  });
  html += `</div>`;
  html += `<button class="secondary-btn" onclick="addEditTrackingRow()" style="margin-top:8px">+ 追跡番号を追加</button>`;
  html += `</div>`;
  html += `<div class="form-actions" style="margin-top:16px;">
    <button class="primary-btn" onclick="saveEditTracking('${shipmentId}')">保存</button>
    <button class="secondary-btn" onclick="closeShippingModal()">キャンセル</button>
  </div>`;
  body.innerHTML = html;
  body.dataset.editTrackingCount = shipment.tracking.length;
  document.getElementById('modal-shipping').classList.add('active');
}

function addEditTrackingRow() {
  const list = document.getElementById('edit-tracking-list');
  const body = document.getElementById('shipping-modal-body');
  const idx = parseInt(body.dataset.editTrackingCount || '0');
  const div = document.createElement('div');
  div.className = 'tracking-row';
  div.id = `edit-tracking-row-${idx}`;
  div.innerHTML = `
    <select id="edit-carrier-${idx}" class="ship-carrier-select">
      <option value="DHL">DHL</option><option value="FedEx">FedEx</option>
      <option value="UPS">UPS</option><option value="EMS">EMS</option>
      <option value="Other">その他</option>
    </select>
    <input type="text" id="edit-tracking-${idx}" placeholder="追跡番号" class="ship-tracking-input">
    <button class="danger-btn-sm" onclick="document.getElementById('edit-tracking-row-${idx}').remove()">✕</button>
  `;
  list.appendChild(div);
  body.dataset.editTrackingCount = idx + 1;
}

async function saveEditTracking(shipmentId) {
  const body = document.getElementById('shipping-modal-body');
  const maxIdx = parseInt(body.dataset.editTrackingCount || '0');
  const tracking = [];
  for (let i = 0; i <= maxIdx; i++) {
    const carrierEl = document.getElementById(`edit-carrier-${i}`);
    const trackEl = document.getElementById(`edit-tracking-${i}`);
    if (carrierEl && trackEl && trackEl.value.trim()) {
      tracking.push({ carrier: carrierEl.value, trackingNumber: trackEl.value.trim() });
    }
  }
  if (tracking.length === 0) { alert('追跡番号を1つ以上入力してください'); return; }
  try {
    await fetch(`/api/shipments/${shipmentId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tracking })
    });
    closeShippingModal();
    showToast('追跡番号を更新しました');
    await showShippingTab('history');
  } catch (e) { alert('保存に失敗しました'); }
}

// まとめモード
function toggleMergeMode() {
  mergeSelectMode = !mergeSelectMode;
  mergeSelected = {};
  const btn = document.getElementById('btn-merge-mode');
  const execBtn = document.getElementById('btn-merge-exec');
  if (mergeSelectMode) {
    btn.textContent = 'キャンセル';
    document.querySelectorAll('.merge-check').forEach(el => el.style.display = 'inline');
  } else {
    btn.textContent = '発送をまとめる';
    if (execBtn) execBtn.style.display = 'none';
    document.querySelectorAll('.merge-check').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.merge-check input').forEach(cb => cb.checked = false);
  }
}

function toggleMergeSelect(shipmentId) {
  const cb = document.getElementById(`merge-cb-${shipmentId}`);
  mergeSelected[shipmentId] = cb.checked;
  const selectedCount = Object.values(mergeSelected).filter(v => v).length;
  const execBtn = document.getElementById('btn-merge-exec');
  if (execBtn) execBtn.style.display = selectedCount >= 2 ? '' : 'none';
}

async function executeMerge() {
  const ids = Object.entries(mergeSelected).filter(([_, v]) => v).map(([id]) => id);
  if (ids.length < 2) { alert('2つ以上選択してください'); return; }
  if (!confirm(`${ids.length}件の発送をまとめますか？`)) return;
  try {
    await fetch('/api/shipments/merge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ shipmentIds: ids })
    });
    showToast('発送をまとめました');
    await showShippingTab('history');
  } catch (e) { alert('エラーが発生しました'); }
}

function buildShipmentDetailTable(items) {
  // アイテムをSKUでグルーピングし、sizeTypeも保持。model/colorwayを商品マスタから補完
  const grouped = {};
  items.forEach(i => {
    if (!grouped[i.sku]) {
      let model = i.model || '', colorway = i.colorway || '', sizeType = i.sizeType || 'unisex';
      // 商品マスタから補完
      if (!model || !colorway) {
        for (const p of (products || [])) {
          const v = (p.variants || []).find(v => v.sku === i.sku);
          if (v) {
            if (!model) model = p.model;
            if (!colorway) colorway = v.colorway;
            sizeType = v.sizeType || sizeType;
            break;
          }
        }
      }
      grouped[i.sku] = { model, colorway, sizeType, sizes: {} };
    }
    grouped[i.sku].sizes[i.size] = (grouped[i.sku].sizes[i.size] || 0) + i.quantity;
  });

  // オーダー管理と同じフォーマットで表示（SKU順ソート）
  const groupedArr = sortItemsBySkuOrder(Object.entries(grouped).map(([sku, data]) => ({ sku, ...data })));
  const unisexItems = groupedArr.filter(g => g.sizeType !== 'womens');
  const womensItems = groupedArr.filter(g => g.sizeType === 'womens');

  let html = '';
  const tables = [];
  if (unisexItems.length > 0) tables.push({ items: unisexItems, sizes: UNISEX_SIZES, label: 'SIZE (UNISEX)' });
  if (womensItems.length > 0) tables.push({ items: womensItems, sizes: WOMENS_SIZES, label: "SIZE (WOMEN'S)" });

  if (tables.length === 0) return '<p>データなし</p>';

  let rowNum = 1;
  tables.forEach(({ items: tItems, sizes, label }) => {
    html += '<div class="finance-spreadsheet"><div class="spreadsheet-scroll"><table>';
    html += `<thead><tr>
      <th class="col-no">No</th><th class="col-product">Products</th>
      <th class="col-color">Color</th><th class="col-sku">Style Code</th>
      <th class="col-qty">QTY</th>
      <th class="col-size-group" colspan="${sizes.length}">${label}</th>
    </tr><tr>
      <th class="col-no"></th><th class="col-product"></th><th class="col-color"></th>
      <th class="col-sku"></th><th class="col-qty"></th>`;
    sizes.forEach(s => html += `<th class="col-size">${s}</th>`);
    html += '</tr></thead><tbody>';

    tItems.forEach(item => {
      const pairs = Object.values(item.sizes).reduce((s, q) => s + q, 0);
      html += `<tr>
        <td class="col-no">${rowNum++}</td>
        <td class="col-product">${item.model}</td>
        <td class="col-color">${item.colorway}</td>
        <td class="col-sku">${item.sku}</td>
        <td class="col-qty">${pairs}</td>`;
      sizes.forEach(s => {
        const qty = item.sizes[s] || 0;
        html += `<td class="col-size ${qty ? 'has-value' : ''}">${qty || ''}</td>`;
      });
      html += '</tr>';
    });
    html += '</tbody></table></div></div>';
  });
  // 旧フォーマット部分を削除し新フォーマットを返す
  return html;
}

function toggleShipmentDetail(id) {
  const el = document.getElementById(`shipment-detail-${id}`);
  if (el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

// =============================================
// クーポン管理（管理者用）
// =============================================

// クーポン管理画面を表示
async function showCouponAdmin() {
  showScreen('screen-coupon');
  await renderCouponAdmin();
}

// クーポン一覧レンダリング
async function renderCouponAdmin() {
  const container = document.getElementById('coupon-admin-content');
  container.innerHTML = '<p>読み込み中...</p>';

  try {
    const res = await fetch('/api/coupons');
    const coupons = await res.json();

    let html = '';

    // 新規登録ボタン
    html += '<button class="primary-btn" style="margin-bottom:16px" onclick="showCouponForm()">+ クーポン追加</button>';

    // 新規登録フォーム（非表示）
    html += `<div id="coupon-form" style="display:none" class="coupon-form-card">
      <h3 id="coupon-form-title">クーポン登録</h3>
      <input type="hidden" id="coupon-edit-id" value="">
      <div class="form-group">
        <label>アカウントID</label>
        <input type="text" id="coupon-accountId" placeholder="アカウントID">
      </div>
      <div class="form-group">
        <label>パスワード</label>
        <input type="text" id="coupon-password" placeholder="パスワード">
      </div>
      <div class="form-group">
        <label>クーポンURL</label>
        <input type="text" id="coupon-url" placeholder="https://...">
      </div>
      <div class="form-group">
        <label>株主番号</label>
        <input type="text" id="coupon-shareholder" placeholder="株主番号">
      </div>
      <div style="display:flex;gap:8px">
        <button class="primary-btn" onclick="saveCoupon()">保存</button>
        <button class="secondary-btn" onclick="hideCouponForm()">キャンセル</button>
      </div>
    </div>`;

    // クーポン一覧テーブル
    if (coupons.length === 0) {
      html += '<p style="text-align:center;color:#888;padding:32px">クーポンが登録されていません</p>';
    } else {
      html += '<div class="table-scroll"><table class="finance-spreadsheet coupon-table"><thead>';
      html += '<tr><th>No.</th><th>アカウントID</th><th>パスワード</th><th>クーポンURL</th><th>株主番号</th><th>使用状況</th><th>拠点</th><th>操作</th></tr>';
      html += '</thead><tbody>';
      // 使用状況で並び替え: 使用中(in_use) → 使用済(used) → 未使用('')
      const statusOrder = { 'in_use': 0, 'used': 1, '': 2 };
      const sortedCoupons = [...coupons].sort((a, b) => {
        const sa = statusOrder[a.status || ''] ?? 2;
        const sb = statusOrder[b.status || ''] ?? 2;
        return sa - sb;
      });
      sortedCoupons.forEach((c, i) => {
        const statusLabel = c.status === 'in_use' ? '使用中' : c.status === 'used' ? '使用済' : '';
        const statusClass = c.status === 'in_use' ? 'coupon-status-inuse' : c.status === 'used' ? 'coupon-status-used' : '';
        const locName = c.locationName || '';
        // クーポンURLは短縮表示＋ハイパーリンク
        const urlShort = c.couponUrl ? (c.couponUrl.length > 30 ? c.couponUrl.substring(0, 30) + '...' : c.couponUrl) : '';
        const urlCell = c.couponUrl
          ? `<a href="${c.couponUrl}" target="_blank" rel="noopener" class="coupon-url-link">${urlShort}</a>`
          : '';

        html += '<tr>';
        html += `<td>${i + 1}</td>`;
        html += `<td>${c.accountId}</td>`;
        html += `<td>${c.password}</td>`;
        html += `<td title="${c.couponUrl || ''}">${urlCell}</td>`;
        html += `<td>${c.shareholderNumber}</td>`;
        html += `<td><span class="${statusClass}">${statusLabel}</span></td>`;
        html += `<td>${locName}</td>`;
        html += `<td>`;
        if (!c.status) {
          // 未使用のみ編集・削除可
          html += `<button class="small-btn" onclick="editCoupon('${c.id}')">編集</button> `;
          html += `<button class="small-btn danger" onclick="deleteCoupon('${c.id}')">削除</button>`;
        } else {
          html += `<span style="color:#888;font-size:12px">${c.status === 'in_use' ? '発行済' : '完了'}</span>`;
        }
        html += `</td>`;
        html += '</tr>';
      });
      html += '</tbody></table></div>';
    }

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = '<p style="color:red">読み込みエラー</p>';
  }
}

// クーポンフォーム表示
function showCouponForm() {
  document.getElementById('coupon-form').style.display = 'block';
  document.getElementById('coupon-form-title').textContent = 'クーポン登録';
  document.getElementById('coupon-edit-id').value = '';
  document.getElementById('coupon-accountId').value = '';
  document.getElementById('coupon-password').value = '';
  document.getElementById('coupon-url').value = '';
  document.getElementById('coupon-shareholder').value = '';
}

function hideCouponForm() {
  document.getElementById('coupon-form').style.display = 'none';
}

// クーポン編集
async function editCoupon(id) {
  const res = await fetch('/api/coupons');
  const coupons = await res.json();
  const c = coupons.find(x => x.id === id);
  if (!c) return;

  document.getElementById('coupon-form').style.display = 'block';
  document.getElementById('coupon-form-title').textContent = 'クーポン編集';
  document.getElementById('coupon-edit-id').value = c.id;
  document.getElementById('coupon-accountId').value = c.accountId;
  document.getElementById('coupon-password').value = c.password;
  document.getElementById('coupon-url').value = c.couponUrl;
  document.getElementById('coupon-shareholder').value = c.shareholderNumber;
}

// クーポン保存
async function saveCoupon() {
  const id = document.getElementById('coupon-edit-id').value;
  const data = {
    accountId: document.getElementById('coupon-accountId').value.trim(),
    password: document.getElementById('coupon-password').value.trim(),
    couponUrl: document.getElementById('coupon-url').value.trim(),
    shareholderNumber: document.getElementById('coupon-shareholder').value.trim()
  };

  if (!data.accountId) {
    alert('アカウントIDを入力してください');
    return;
  }

  try {
    if (id) {
      // 更新
      await fetch(`/api/coupons/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      showToast('クーポンを更新しました');
    } else {
      // 新規登録
      await fetch('/api/coupons', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      showToast('クーポンを登録しました');
    }
    hideCouponForm();
    await renderCouponAdmin();
  } catch (e) {
    alert('保存エラー');
  }
}

// クーポン削除
async function deleteCoupon(id) {
  if (!confirm('このクーポンを削除しますか？')) return;
  try {
    await fetch(`/api/coupons/${id}`, { method: 'DELETE' });
    showToast('クーポンを削除しました');
    await renderCouponAdmin();
  } catch (e) {
    alert('削除エラー');
  }
}

// =============================================
// 仕入ページ - クーポン発行機能
// =============================================

// 仕入ページにクーポンセクションを追加レンダリング
async function renderPurchaseCoupon() {
  try {
    const res = await fetch(`/api/coupons/location/${purchaseLocationId}`);
    const coupon = await res.json();

    let html = '<div class="purchase-coupon-section">';
    html += '<div class="coupon-section-header">クーポン</div>';

    if (coupon) {
      // 現在発行中のクーポン情報を表示
      html += '<div class="coupon-info-card">';
      html += '<div class="coupon-info-row"><span class="coupon-label">アカウントID</span><span class="coupon-value" onclick="copyCouponText(this)">' + coupon.accountId + ' <span class="copy-hint">📋</span></span></div>';
      html += '<div class="coupon-info-row"><span class="coupon-label">パスワード</span><span class="coupon-value" onclick="copyCouponText(this)">' + coupon.password + ' <span class="copy-hint">📋</span></span></div>';
      html += '<div class="coupon-info-row"><span class="coupon-label">クーポンURL</span><a href="' + coupon.couponUrl + '" target="_blank" rel="noopener" class="coupon-value coupon-url-val">' + coupon.couponUrl + ' <span class="copy-hint">🔗</span></a></div>';
      html += '<div class="coupon-info-row"><span class="coupon-label">株主番号</span><span class="coupon-value" onclick="copyCouponText(this)">' + coupon.shareholderNumber + ' <span class="copy-hint">📋</span></span></div>';
      html += '</div>';
    } else {
      html += '<p style="text-align:center;color:#888;padding:16px">現在発行中のクーポンはありません</p>';
    }

    html += '<button class="coupon-issue-btn" onclick="issueCoupon()">新しいクーポンを発行</button>';
    html += '</div>';

    return html;
  } catch (e) {
    return '<div class="purchase-coupon-section"><p style="color:red">クーポン読み込みエラー</p></div>';
  }
}

// クーポンテキストコピー
function copyCouponText(el) {
  // コピーヒントのテキストを除外
  const text = el.textContent.replace('📋', '').trim();
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showToast('コピーしました');
    });
  } else {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('コピーしました');
  }
}

// 新しいクーポン発行
async function issueCoupon() {
  // 注意ポップアップ
  const confirmed = confirm(
    '前回発行したクーポンが10枚すべて利用済みであることを確認してください。\n\n' +
    '未使用のクーポンが残っている場合は、新規発行は行わないでください。\n\n' +
    '問題がなければ、そのまま発行を進めてください。'
  );
  if (!confirmed) return;

  try {
    const res = await fetch('/api/coupons/issue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        locationId: purchaseLocationId,
        locationName: purchaseLocationName
      })
    });

    if (!res.ok) {
      const err = await res.json();
      alert(err.error || 'クーポン発行に失敗しました');
      return;
    }

    showToast('新しいクーポンを発行しました');
    await renderPurchasePage();
  } catch (e) {
    alert('通信エラーが発生しました');
  }
}
