// スプレッドシートのデータをもとにMexico 66の全バリアントを商品登録するスクリプト
const fs = require('fs');
const path = require('path');

const PRODUCTS_FILE = path.join(__dirname, 'data', 'products.json');

// Mexico 66の全27バリアント（スプレッドシートから）
const mexico66Variants = [
  { code: '1183C102.002', name: 'BLACK/BLACK',               url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_002.html' },
  { code: '1183C102.100', name: 'WHITE/BLUE',                url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_100.html' },
  { code: '1183C102.201', name: 'BIRCH/GREEN',               url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_201.html' },
  { code: '1183C102.200', name: 'BIRCH/PEACOAT',             url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_200.html' },
  { code: '1183C102.751', name: 'YELLOW/BLACK',              url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_751.html' },
  { code: '1183C102.001', name: 'BLACK/WHITE',               url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_001.html' },
  { code: '1183C102.250', name: 'BEIGE/GRASS GREEN',         url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_250.html' },
  { code: '1183C102.104', name: 'WHITE/WHITE',               url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_104.html' },
  { code: '1183C102.752', name: 'IVORY/BLACK',               url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_752.html' },
  { code: '1183C102.204', name: 'BIRCH/RUST ORANGE',         url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_204.html' },
  { code: '1183C102.203', name: 'CLAY CANYON/PAPER BAG',     url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_203.html' },
  { code: '1183C102.701', name: 'DRAGON FRUIT/BLACK',        url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_701.html' },
  { code: '1183C102.105', name: 'WHITE/CLASSIC RED',         url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_105.html' },
  { code: '1183C102.600', name: 'CLASSIC RED/BLACK',         url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_600.html' },
  { code: '1183C102.005', name: 'BLACK/DRAGON FRUIT',        url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183C102_005.html' },
  { code: '1183B566.700', name: 'ROSE GOLD/CREAM',           url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B566_700.html' },
  { code: '1183B566.020', name: 'PURE SILVER/BLACK',         url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B566_020.html' },
  { code: '1183B566.200', name: 'GOLD/BLACK',                url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B566_200.html' },
  { code: '1183B566.021', name: 'SILVER/OFF WHITE',          url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B566_021.html' },
  { code: '1183B566.201', name: 'GOLD/WHITE',                url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B566_201.html' },
  { code: '1183B566.022', name: 'GUNMETAL/BLACK',            url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B566_022.html' },
  { code: '1183A201.254', name: 'OATMEAL/GINGER PEACH',      url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_254.html' },
  { code: '1183A201.304', name: 'AIRY GREEN/VERDIGRIS GREEN', url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_304.html' },
  { code: '1183A201.003', name: 'BLACK/YELLOW',              url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_003.html' },
  { code: '1183A201.305', name: 'GARDEN GREEN/PURE SILVER',  url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_305.html' },
  { code: '1183A201.126', name: 'WHITE/BLACK',               url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_126.html' },
  { code: '1183A201.127', name: 'CREAM/LIGHT SAGE',          url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183A201_127.html' },
  { code: '1183B511.100', name: 'WHITE/DARK BLUE',           url: 'https://www.onitsukatiger.com/jp/ja-jp/product/mexico-66/1183B511_100.html' },
];

// 画像URL生成（2足並んだペア画像）
function getImageUrl(code) {
  const style = code.replace('.', '_');
  return `https://asics.scene7.com/is/image/asics/${style}_SB_TP_GLB?$otmag_zoom$&qlt=99,1`;
}

// メイン処理
const products = JSON.parse(fs.readFileSync(PRODUCTS_FILE, 'utf-8'));

// 既存のMEXICO 66エントリを探す
const mexIdx = products.findIndex(p => p.model === 'MEXICO 66');

// バリアントデータ生成
const variants = mexico66Variants.map(v => ({
  colorway: v.name,
  sku: v.code,
  price: 125,            // 販売価格 $125（既存設定を踏襲）
  sizeType: 'unisex',
  image: getImageUrl(v.code),
  supplierUrl: v.url,
  purchasePrice: 11550,  // 仕入値 ¥11,550
  excludedSizes: []
}));

if (mexIdx >= 0) {
  // 既存エントリを更新
  products[mexIdx].variants = variants;
  console.log(`MEXICO 66を更新: ${variants.length}バリアント`);
} else {
  // 新規作成
  products.push({
    id: Date.now().toString(),
    model: 'MEXICO 66',
    displayOrder: products.length,
    variants
  });
  console.log(`MEXICO 66を新規登録: ${variants.length}バリアント`);
}

fs.writeFileSync(PRODUCTS_FILE, JSON.stringify(products, null, 2), 'utf-8');
console.log('products.json 更新完了');
console.log(`全商品数: ${products.length}`);
console.log(`MEXICO 66バリアント数: ${variants.length}`);
