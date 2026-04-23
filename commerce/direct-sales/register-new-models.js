// 新規3モデル（MEXICO 66 SLIP-ON / MOAL 77 NM / MEXICO 66 SD VIN）をproducts.jsonに登録
// 既存3モデル（MEXICO 66, MEXICO 66 SD, MEXICO 66 TGRS）はそのまま、追加登録のみ行う
const fs = require('fs');
const path = require('path');

const PRODUCTS_FILE = path.join(__dirname, 'data', 'products.json');

// 画像URL生成（既存と統一: SB_FR_GLB = 1足正面画像）
function getImageUrl(code) {
  const style = code.replace('.', '_');
  return `https://asics.scene7.com/is/image/asics/${style}_SB_FR_GLB?$otmag_zoom$&qlt=99,1`;
}

// 新規3モデルのデータ定義
const newModels = [
  {
    model: 'MEXICO 66 SLIP-ON',
    displayOrder: 6,  // 既存TGRS(5)の後
    purchasePrice: 10010,  // 仕入値 ¥10,010
    price: 115,            // 販売価格 $115（スプレッドシートI列の社長入力値）
    sizeType: 'unisex',
    supplierBase: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66-slip-on',
    variants: [
      { code: '1183A360.205', color: 'BIRCH/MIDNIGHT',       urlSlug: '1183A360_205' },
      { code: '1183A360.121', color: 'WHITE/TRICOLOR',       urlSlug: '1183A360_121' },
      { code: '1183A360.401', color: 'NAVY/OFF-WHITE',       urlSlug: '1183A360_401' },
      { code: '1183A360.002', color: 'BLACK/BLACK',          urlSlug: '1183A360_002' },
      { code: '1183A360.131', color: 'OFF-WHITE/BEET JUICE', urlSlug: '1183A360_131' },
      { code: '1183A360.132', color: 'WHITE/GINGER PEACH',   urlSlug: '1183A360_132' },
      { code: '1183A746.751', color: 'YELLOW/BLACK',         urlSlug: '1183a746_751' },
      { code: '1183C141.100', color: 'WHITE/WHITE',          urlSlug: '1183c141_100' },
    ],
  },
  {
    model: 'MEXICO 66 SD VIN',
    displayOrder: 7,
    purchasePrice: 13860,  // 仕入値 ¥13,860
    price: 150,            // 販売価格 $150（スプレッドシートI列の社長入力値）
    sizeType: 'unisex',
    supplierBase: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66-sd-vin',
    variants: [
      { code: '1183C015.200', color: 'BIRCH/METROPOLIS',          urlSlug: '1183c015_200' },
      { code: '1183C015.101', color: 'CREAM/BIRCH',               urlSlug: '1183C015_101' },
      { code: '1183C015.104', color: 'WHITE/DIRECTOIRE BLUE',     urlSlug: '1183C015_104' },
      { code: '1183C015.201', color: 'BIRCH/GREEN',               urlSlug: '1183C015_201' },
      { code: '1183C015.202', color: 'BEIGE/BEET JUICE',          urlSlug: '1183C015_202' },
      { code: '1183C015.205', color: 'CLAY CANYON/CREAM',         urlSlug: '1183C015_205' },
      { code: '1183C015.106', color: 'OFF-WHITE/PURPLE SPECTRUM', urlSlug: '1183C015_106' },
      { code: '1183C015.400', color: 'PEACOAT/WHEAT YELLOW',      urlSlug: '1183C015_400' },
    ],
  },
  {
    model: 'MOAL 77 NM',
    displayOrder: 8,
    purchasePrice: 24640,  // 仕入値 ¥24,640
    price: 240,            // 販売価格 $240（スプレッドシートI列の社長入力値）
    sizeType: 'unisex',
    supplierBase: 'https://www.onitsukatiger.com/jp/ja-jp/product/moal-77-nm',
    variants: [
      { code: '1183B761.201', color: 'PAPER BAG/WHITE',    urlSlug: '1183b761_201' },
      { code: '1183B761.301', color: 'BRONZE GREEN/WHITE', urlSlug: '1183B761_301' },
    ],
  },
];

// products.jsonを読み込み
const products = JSON.parse(fs.readFileSync(PRODUCTS_FILE, 'utf-8'));

let added = 0;
let updated = 0;

for (const m of newModels) {
  const variants = m.variants.map(v => ({
    colorway: v.color,
    sku: v.code,
    price: m.price,
    sizeType: m.sizeType,
    image: getImageUrl(v.code),
    supplierUrl: `${m.supplierBase}/${v.urlSlug}.html`,
    purchasePrice: m.purchasePrice,
    excludedSizes: []
  }));

  const idx = products.findIndex(p => p.model === m.model);
  if (idx >= 0) {
    products[idx].variants = variants;
    products[idx].displayOrder = m.displayOrder;
    console.log(`更新: ${m.model} (${variants.length}バリアント)`);
    updated++;
  } else {
    products.push({
      id: Date.now().toString() + '_' + m.model.replace(/\s+/g, '_'),
      model: m.model,
      displayOrder: m.displayOrder,
      variants
    });
    console.log(`新規登録: ${m.model} (${variants.length}バリアント)`);
    added++;
  }
}

fs.writeFileSync(PRODUCTS_FILE, JSON.stringify(products, null, 2), 'utf-8');

console.log('\n==== 完了 ====');
console.log(`新規: ${added}モデル / 更新: ${updated}モデル`);
console.log(`全商品数: ${products.length}`);
products.forEach(p => console.log(` - ${p.model} (displayOrder=${p.displayOrder}, variants=${p.variants.length})`));
