// ================================================================
// 仕入管理表 オーダー自動反映ツール
// eBay Trading APIからオーダーを取得し、仕入管理表に自動反映する
//
// 【機能】
// 1. eBay APIから新規オーダーを取得
// 2. 過去の仕入履歴から型番・仕入先情報を自動反映
// 3. 初回商品はタイトルから型番を自動抽出（型番ルールシート参照）
// 4. キャンセルリクエストを自動検知 → R列に「キャンセル確認」
// 5. O列にタイトル（eBay商品ページのハイパーリンク付き）
// 6. 毎朝10時に自動実行 + ボタンで手動実行
//
// 【セットアップ手順】
// 1. このスクリプトをスプレッドシートのApps Scriptに貼り付ける
// 2. メニュー「eBay仕入管理」→「⚙️ eBay API設定」でAPIキーを入力
// 3. メニュー「eBay仕入管理」→「⏰ 毎朝10時自動実行を設定」でトリガー登録
// ================================================================

// ===== 設定（必要に応じて変更） =====
var SHEET_NAME = '仕入管理（無在庫）';        // メインシート名
var RULES_SHEET_NAME = '型番ルール';          // 型番ルールシート名
var HEADER_ROW = 5;                           // ヘッダー行番号
var HANDLING_BUSINESS_DAYS = 5;               // ハンドリングタイム（営業日）
var FETCH_DAYS_BACK = 2;                      // 何日前からのオーダーを取得するか（毎日実行+停止1日の余裕）
var PROP_LAST_CREATED_TIME = 'LAST_PROCESSED_CREATED_TIME';  // 前回処理した最大CreatedTime（Refunded蘇り防止）
var EBAY_API_URL = 'https://api.ebay.com/ws/api.dll';
var EBAY_COMPAT_LEVEL = '967';                // eBay API互換性レベル
var EBAY_SITE_ID = '0';                       // eBay USサイト

// ===== 列番号マッピング（1始まり） =====
var COL = {
  SHIP_BY: 2,         // B列: 発送期限
  SKU: 3,             // C列: SKU
  MODEL: 6,           // F列: 型番（ヘッダーは「メモ」だが実際は型番）
  SUPPLIER: 7,        // G列: 仕入先
  SUPPLIER_URL: 8,    // H列: 仕入先URL
  PURCHASE_PRICE: 10, // J列: 仕入値
  SIZE: 12,           // L列: サイズ（ヘッダーは「備考」だが実際はサイズ）
  TITLE: 15,          // O列: タイトル（eBayリンク付き）
  ORDER_NO: 17,       // Q列: Order no.
  NOTES: 18,          // R列: 備考（キャンセル確認等）
};


// ================================================================
// メニュー（シートを開いた時に自動で表示される）
// ================================================================
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('eBay仕入管理')
    .addItem('📥 新規オーダー反映', 'fetchAndPopulateOrders')
    .addSeparator()
    .addItem('⚙️ eBay API設定', 'setupApiCredentials')
    .addItem('⏰ 毎朝10時の自動実行を設定', 'setDailyTrigger')
    .addItem('🗑️ 自動実行を解除', 'removeDailyTrigger')
    .addSeparator()
    .addItem('🛡️ 重複安全チェック（本番反映前に推奨）', 'checkDuplicatesSafety')
    .addItem('🔍 特定オーダーのXMLを確認（デバッグ）', 'debugSingleOrder')
    .addItem('⏮️ 前回処理時刻をリセット', 'resetLastProcessedTime')
    .addToUi();
}


// ================================================================
// メイン処理：新規オーダーを取得して仕入管理表に反映
// メニューのボタンクリック & 毎朝10時のトリガーから呼ばれる
// ================================================================
function fetchAndPopulateOrders() {
  // --- 排他ロック（2重実行防止） ---
  // トリガーが万一2回発火しても、同時に書き込まないようにする
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) {  // 5秒待ってもロック取得できなければ中断
    Logger.log('⚠️ 別の実行が進行中のためスキップ');
    return;
  }

  try {
    fetchAndPopulateOrdersMain_();
  } finally {
    lock.releaseLock();
  }
}

// メイン処理（ロック取得後に呼ばれる）
function fetchAndPopulateOrdersMain_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);

  if (!sheet) {
    showMessage_('エラー: シート「' + SHEET_NAME + '」が見つかりません');
    return;
  }

  // --- E3に処理中表示（赤文字でスタッフに行削除しないよう知らせる） ---
  var statusCell = sheet.getRange('E3');
  var statusText = '⏳ オーダー反映中...行の削除はしないでください';
  var richStatus = SpreadsheetApp.newRichTextValue()
    .setText(statusText)
    .setTextStyle(0, statusText.length,
      SpreadsheetApp.newTextStyle().setForegroundColor('#FF0000').setBold(true).build())
    .build();
  statusCell.setRichTextValue(richStatus);
  SpreadsheetApp.flush(); // 即時反映

  try {
    fetchAndPopulateOrdersBody_(ss, sheet);
  } finally {
    // 成功でもエラーでも必ず処理中表示を消す
    statusCell.setValue('');
    SpreadsheetApp.flush();
  }
}

// メイン処理の本体（処理中表示のtry/finallyから呼ばれる）
function fetchAndPopulateOrdersBody_(ss, sheet) {
  // --- APIキーの確認 ---
  var config = getEbayConfig_();
  if (!config.userToken) {
    showMessage_('⚠️ eBay APIが未設定です。\nメニュー → eBay仕入管理 → ⚙️ eBay API設定 から設定してください。');
    return;
  }

  // --- 1. eBay APIでオーダー取得（過去N日分） ---
  Logger.log('📡 eBay APIからオーダーを取得中...');
  var orders;
  try {
    orders = callGetOrders_(config, FETCH_DAYS_BACK);
  } catch (e) {
    showMessage_('❌ eBay API呼び出しエラー:\n' + e.message);
    Logger.log('API Error: ' + e.message + '\n' + e.stack);
    return;
  }
  Logger.log('API取得件数: ' + orders.length);

  if (orders.length === 0) {
    showMessage_('eBay APIから取得したオーダーはありませんでした。');
    return;
  }

  // --- 1.5. 前回処理時刻以降のみにフィルタ（Refunded蘇り防止） ---
  // eBayでSend refundした全額返金オーダーはCanceled扱いにならず、
  // GetOrdersで何日も拾われ続ける。前回処理した最大CreatedTimeより
  // 新しいオーダーのみを処理対象とすることで、古いオーダーの再出現を防ぐ。
  orders = filterByLastProcessedTime_(orders);
  Logger.log('前回処理以降のオーダー数: ' + orders.length);

  if (orders.length === 0) {
    showMessage_('前回処理以降の新しいオーダーはありませんでした。');
    return;
  }

  // --- 2. 既存データとの重複チェック用キーを取得 ---
  // OrderNo + 正規化SKU の組み合わせで判定（同一オーダーで複数商品がある場合に対応）
  // シート側もAPI側も normalizeSkuForCompare_ で正規化してから比較することで
  // 既存データがZ付きSKUで残っていても正しく重複と判定される
  var existingKeys = getExistingOrderKeys_(sheet);
  Logger.log('既存データ件数: ' + existingKeys.size);

  // --- 3. 新規オーダーのみフィルタ（+ 重複疑惑ログ） ---
  var suspiciousCount = 0;
  var newOrders = orders.filter(function(o) {
    var key = o.orderNumber + '|' + normalizeSkuForCompare_(o.sku);
    var isNew = !existingKeys.has(key);

    // 重複疑惑検出: 新規判定されたが、同じorderNumberが既に存在する
    // → Z除去や空白以外の微妙な差異で重複を見逃している可能性あり、要確認
    if (isNew && existingKeys.orderNumbersSet
        && existingKeys.orderNumbersSet.has(o.orderNumber)) {
      suspiciousCount++;
      Logger.log('⚠️ 重複疑惑: ' + o.orderNumber + ' / SKU="' + o.sku
        + '" は新規判定だが、同じorderNumberが既存シートに存在します。要目視確認。');
    }
    return isNew;
  });
  Logger.log('新規オーダー数: ' + newOrders.length
    + (suspiciousCount > 0 ? ' （重複疑惑: ' + suspiciousCount + '件）' : ''));

  if (newOrders.length === 0) {
    showMessage_('新規オーダーはありません（全て反映済みです）');
    return;
  }

  // --- 4. 過去の仕入履歴を読み込み（型番・仕入先の参照用） ---
  Logger.log('📚 過去の仕入履歴を読み込み中...');
  var history = loadHistory_(sheet);

  // --- 5. 型番ルールを読み込み ---
  var modelRules = loadModelRules_(ss);

  // --- 6. 各オーダーの行データを構築 ---
  var rowsData = newOrders.map(function(order) {
    return buildRowData_(order, history, modelRules);
  });

  // --- 7. シートに追記 ---
  Logger.log('📝 ' + rowsData.length + '件をシートに書き込み中...');
  appendRows_(sheet, rowsData);

  // --- 8. 今回API取得した全オーダーの最大CreatedTimeを保存 ---
  // （書き込み成功後に保存する。途中エラー時は保存しないことで次回リカバリ可能に）
  // newOrdersではなくorders全体を使う：同じオーダーが次回も拾われないように
  updateLastProcessedTime_(orders);

  showMessage_('✅ ' + rowsData.length + '件の新規オーダーを反映しました！');
  Logger.log('完了: ' + rowsData.length + '件反映');
}


// ================================================================
// 前回処理した最大CreatedTime以降のオーダーのみに絞り込む
// Refunded（eBay Send refund）で返金したオーダーはCanceled扱いにならず
// GetOrdersで取得され続けるため、前回以降のもののみを新規候補にする。
// プロパティ未設定時（初回）は全件通す。
// ================================================================
function filterByLastProcessedTime_(orders) {
  var props = PropertiesService.getScriptProperties();
  var lastTimeStr = props.getProperty(PROP_LAST_CREATED_TIME);
  if (!lastTimeStr) {
    Logger.log('前回処理時刻が未設定（初回扱い）。全件を対象にします。');
    return orders;
  }

  var lastTime = new Date(lastTimeStr);
  Logger.log('前回処理時刻: ' + lastTime.toISOString() + ' 以降のみ対象');

  return orders.filter(function(o) {
    // createdTimeが無いオーダーは安全側で通す（想定外ケース）
    if (!o.createdTime) return true;
    return o.createdTime.getTime() > lastTime.getTime();
  });
}


// ================================================================
// 今回処理したオーダーの最大CreatedTimeをプロパティに保存
// 次回実行時はこの時刻以降のオーダーだけを対象にする
// ================================================================
function updateLastProcessedTime_(orders) {
  var maxTime = null;
  for (var i = 0; i < orders.length; i++) {
    var ct = orders[i].createdTime;
    if (ct && (!maxTime || ct.getTime() > maxTime.getTime())) {
      maxTime = ct;
    }
  }

  if (maxTime) {
    PropertiesService.getScriptProperties()
      .setProperty(PROP_LAST_CREATED_TIME, maxTime.toISOString());
    Logger.log('最大CreatedTimeを保存: ' + maxTime.toISOString());
  }
}


// ================================================================
// eBay Trading API: GetOrders 呼び出し（ページネーション対応）
// ================================================================
function callGetOrders_(config, daysBack) {
  var now = new Date();
  var from = new Date(now.getTime() - daysBack * 24 * 60 * 60 * 1000);

  var allOrders = [];
  var pageNumber = 1;
  var hasMore = true;

  while (hasMore) {
    // XMLリクエストを構築
    var xmlRequest = buildGetOrdersXml_(config.userToken, from, now, pageNumber);

    // API呼び出し
    var options = {
      method: 'post',
      contentType: 'text/xml',
      headers: {
        'X-EBAY-API-DEV-NAME': config.devId,
        'X-EBAY-API-APP-NAME': config.appId,
        'X-EBAY-API-CERT-NAME': config.certId,
        'X-EBAY-API-CALL-NAME': 'GetOrders',
        'X-EBAY-API-COMPATIBILITY-LEVEL': EBAY_COMPAT_LEVEL,
        'X-EBAY-API-SITEID': EBAY_SITE_ID,
      },
      payload: xmlRequest,
      muteHttpExceptions: true,
    };

    var response = UrlFetchApp.fetch(EBAY_API_URL, options);
    var responseCode = response.getResponseCode();

    if (responseCode !== 200) {
      throw new Error('eBay API HTTP エラー: ' + responseCode + '\n' + response.getContentText().substring(0, 500));
    }

    // XMLレスポンスを解析
    var parsed = parseGetOrdersResponse_(response.getContentText());
    allOrders = allOrders.concat(parsed.orders);

    hasMore = parsed.hasMore;
    pageNumber++;

    // APIレート制限対策（連続リクエスト間に500ms待機）
    if (hasMore) {
      Utilities.sleep(500);
    }
  }

  return allOrders;
}


// ================================================================
// GetOrders XMLリクエスト構築
// ================================================================
function buildGetOrdersXml_(token, fromDate, toDate, page) {
  var fromStr = Utilities.formatDate(fromDate, 'UTC', "yyyy-MM-dd'T'HH:mm:ss'.000Z'");
  var toStr = Utilities.formatDate(toDate, 'UTC', "yyyy-MM-dd'T'HH:mm:ss'.000Z'");

  return '<?xml version="1.0" encoding="utf-8"?>'
    + '<GetOrdersRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
    + '<RequesterCredentials><eBayAuthToken>' + token + '</eBayAuthToken></RequesterCredentials>'
    + '<CreateTimeFrom>' + fromStr + '</CreateTimeFrom>'
    + '<CreateTimeTo>' + toStr + '</CreateTimeTo>'
    + '<OrderRole>Seller</OrderRole>'
    + '<OrderStatus>All</OrderStatus>'  // Cancelled/CancelPendingを含む全ステータスを取得（キャンセル検知漏れ防止）
    + '<DetailLevel>ReturnAll</DetailLevel>'
    + '<Pagination>'
    + '<EntriesPerPage>100</EntriesPerPage>'
    + '<PageNumber>' + page + '</PageNumber>'
    + '</Pagination>'
    + '</GetOrdersRequest>';
}


// ================================================================
// GetOrders XMLレスポンス解析
// 各トランザクション（商品単位）をオーダーオブジェクトに変換
// ================================================================
function parseGetOrdersResponse_(xmlText) {
  var doc = XmlService.parse(xmlText);
  var root = doc.getRootElement();
  var ns = root.getNamespace();

  // --- エラーチェック ---
  var ack = getChildText_(root, 'Ack', ns);
  if (ack !== 'Success' && ack !== 'Warning') {
    var errorsEl = root.getChild('Errors', ns);
    var msg = errorsEl ? getChildText_(errorsEl, 'ShortMessage', ns) : 'Unknown';
    var detail = errorsEl ? getChildText_(errorsEl, 'LongMessage', ns) : '';
    throw new Error('eBay API: ' + msg + ' - ' + detail);
  }

  var orders = [];
  var orderArray = root.getChild('OrderArray', ns);

  if (orderArray) {
    var orderElements = orderArray.getChildren('Order', ns);

    for (var oi = 0; oi < orderElements.length; oi++) {
      var orderEl = orderElements[oi];

      // オーダーID（ExtendedOrderIDを優先 = Seller Hubで表示される形式）
      var orderId = getChildText_(orderEl, 'ExtendedOrderID', ns)
                 || getChildText_(orderEl, 'OrderID', ns) || '';

      // キャンセル状態の確認（複数フィールドをチェック）
      var isCancelRequested = false;

      // 方法0: OrderStatus自体がCancelled/CancelPending（最も確実）
      var orderStatus = getChildText_(orderEl, 'OrderStatus', ns) || '';
      if (orderStatus === 'Cancelled' || orderStatus === 'CancelPending') {
        isCancelRequested = true;
      }

      // 方法1: CancelStatus > CancelState
      var cancelStatusEl = orderEl.getChild('CancelStatus', ns);
      if (!isCancelRequested && cancelStatusEl) {
        var cancelState = getChildText_(cancelStatusEl, 'CancelState', ns) || '';
        if (cancelState === 'CancelRequested'
         || cancelState === 'CancelPending'
         || cancelState === 'CancelClosedForCommitment'
         || cancelState === 'CancelComplete') {
          isCancelRequested = true;
        }
      }
      // 方法2: BuyerRequestedCancel（バイヤーからのキャンセルリクエスト）
      if (!isCancelRequested) {
        var buyerCancelEl = orderEl.getChild('BuyerRequestedCancel', ns);
        if (buyerCancelEl && getChildText_(buyerCancelEl, '', ns) === 'true') {
          isCancelRequested = true;
        }
      }
      // 方法3: CancelReason が存在する場合もキャンセルと判定
      if (!isCancelRequested && cancelStatusEl) {
        var cancelReason = getChildText_(cancelStatusEl, 'CancelReason', ns) || '';
        if (cancelReason) {
          isCancelRequested = true;
        }
      }
      // 方法4: EIAS CancelStatus（一部のキャンセル処理中オーダーで設定）
      if (!isCancelRequested) {
        var eiasCancelStatus = getChildText_(orderEl, 'EIASToken', ns);
        var cancelReasonTop = getChildText_(orderEl, 'CancelReason', ns) || '';
        if (cancelReasonTop) {
          isCancelRequested = true;
        }
      }

      // 支払日時（ShipByDate計算のベース）
      var paidTimeStr = getChildText_(orderEl, 'PaidTime', ns);
      var createdTimeStr = getChildText_(orderEl, 'CreatedTime', ns);
      var baseTime = paidTimeStr ? new Date(paidTimeStr)
                   : (createdTimeStr ? new Date(createdTimeStr) : new Date());
      // 前回処理時刻フィルタ用のオーダー作成日時
      var orderCreatedTime = createdTimeStr ? new Date(createdTimeStr) : null;

      // --- 各トランザクション（商品）をループ ---
      var transArray = orderEl.getChild('TransactionArray', ns);
      if (!transArray) continue;

      var transactions = transArray.getChildren('Transaction', ns);

      for (var ti = 0; ti < transactions.length; ti++) {
        var trans = transactions[ti];
        var itemEl = trans.getChild('Item', ns);
        if (!itemEl) continue;

        // 商品情報
        var itemId = getChildText_(itemEl, 'ItemID', ns) || '';
        var title = getChildText_(itemEl, 'Title', ns) || '';
        var sku = getChildText_(itemEl, 'SKU', ns) || '';

        // バリエーション情報（ある場合はSKUを上書き）
        var variationDetails = '';
        var variationEl = trans.getChild('Variation', ns);
        if (variationEl) {
          var varSku = getChildText_(variationEl, 'SKU', ns);
          if (varSku) sku = varSku;
          variationDetails = parseVariationSpecifics_(variationEl, ns);
        }

        // 有在庫判定: サイズ部分にZがあるか（親SKU先頭のZは除外）
        // 例: V0126-8.5Z-30 → 有在庫, Z0196-11-23 → 無在庫, Z0196-11Z-23 → 有在庫
        var hasStock = /-\d+\.?\d*Z(?:-|$)/.test(sku);

        // ※ Z除去はしない（シートにはZ付きSKUをそのまま保持する運用）
        //   重複チェック時のみ normalizeSkuForCompare_ でZ除去正規化して比較する

        // 発送期限を営業日で計算
        var shipByDate = addBusinessDays_(baseTime, HANDLING_BUSINESS_DAYS);

        orders.push({
          orderNumber: orderId,
          itemId: itemId,
          title: title,
          sku: sku,
          variationDetails: variationDetails,
          shipByDate: shipByDate,
          isCancelRequested: isCancelRequested,
          hasStock: hasStock,
          createdTime: orderCreatedTime,   // 前回処理時刻との比較用
        });
      }
    }
  }

  // ページネーション判定
  var hasMoreStr = getChildText_(root, 'HasMoreOrders', ns);
  var hasMore = (hasMoreStr === 'true');

  return { orders: orders, hasMore: hasMore };
}


// ================================================================
// バリエーション詳細（サイズ等）を文字列に変換
// 例: "US8.5/JP26.5"
// ebaymag経由の他国サイト（独/仏/伊/西等）のサイズラベルにも対応
// ================================================================
function parseVariationSpecifics_(variationEl, ns) {
  var specificsEl = variationEl.getChild('VariationSpecifics', ns);
  if (!specificsEl) return '';

  var nameValueLists = specificsEl.getChildren('NameValueList', ns);
  var parts = [];

  // サイズを示す多言語キーワード（すべて小文字で比較）
  var sizeKeywords = [
    'size', 'サイズ',
    'schuhgröße', 'schuhgrosse', 'größe', 'grosse',  // ドイツ語（Schuhgröße等）
    'pointure', 'taille',                              // フランス語
    'taglia', 'numero',                                // イタリア語
    'talla', 'número', 'numero',                       // スペイン語
    'maat',                                            // オランダ語
  ];

  for (var i = 0; i < nameValueLists.length; i++) {
    var nvl = nameValueLists[i];
    var name = (getChildText_(nvl, 'Name', ns) || '').toLowerCase();
    var value = getChildText_(nvl, 'Value', ns) || '';

    // ラベル名が多言語サイズキーワードに一致するか
    var isSizeByName = false;
    for (var k = 0; k < sizeKeywords.length; k++) {
      if (name.indexOf(sizeKeywords[k]) >= 0) { isSizeByName = true; break; }
    }
    // 保険: 値が US10 / JP28 / EU42 / UK8 等のパターンを含む場合もサイズと判定
    // （未知の言語ラベルが返ってきてもサイズを拾い逃さないため）
    var isSizeByValue = /\b(US|JP|EU|UK)\s*\d/i.test(value);

    if (isSizeByName || isSizeByValue) {
      // eBayから返された値をそのまま使用（他国表記もそのまま反映）
      parts.push(value);
    }
  }

  return parts.join('/');
}


// ================================================================
// タイトルから New Balance のWidth（D, 2E, 4E, 6E, B 等）を抽出
// 例: "New Balance 990v6 Width D" → "D"
// ================================================================
function extractWidth_(title) {
  if (!title) return '';
  // "Width D", "Width: 2E", "Width-4E" 等に対応
  // キャプチャ対象: 英大文字1-3文字 もしくは 数字+英字（2E/4E/6E）
  var match = title.match(/\bWidth[\s:：\-]+([0-9]?[A-Z]{1,3})\b/i);
  return match ? match[1].toUpperCase() : '';
}


// ================================================================
// 過去の仕入履歴を読み込み
// 親SKU → 各フィールドの最新値をマッピング
// ================================================================
function loadHistory_(sheet) {
  var lastRow = findLastDataRow_(sheet);
  if (lastRow <= HEADER_ROW) return {};

  var dataRows = lastRow - HEADER_ROW;

  // 必要な列だけ一括読み込み（高速化のため）
  var skuData = sheet.getRange(HEADER_ROW + 1, COL.SKU, dataRows, 1).getValues();
  var modelData = sheet.getRange(HEADER_ROW + 1, COL.MODEL, dataRows, 1).getValues();
  var supplierData = sheet.getRange(HEADER_ROW + 1, COL.SUPPLIER, dataRows, 1).getValues();
  var urlData = sheet.getRange(HEADER_ROW + 1, COL.SUPPLIER_URL, dataRows, 1).getValues();
  var priceData = sheet.getRange(HEADER_ROW + 1, COL.PURCHASE_PRICE, dataRows, 1).getValues();

  // 親SKU → 履歴レコード配列（新しい順）
  var history = {};

  // 下（新しい）から上（古い）に走査 → 最新情報が先頭にくる
  for (var i = dataRows - 1; i >= 0; i--) {
    var sku = skuData[i][0] ? skuData[i][0].toString().trim() : '';
    if (!sku) continue;

    var parentSku = extractParentSKU_(sku);
    if (!parentSku) continue;

    if (!history[parentSku]) {
      history[parentSku] = [];
    }

    history[parentSku].push({
      model: modelData[i][0] ? modelData[i][0].toString().trim() : '',
      supplier: supplierData[i][0] ? supplierData[i][0].toString().trim() : '',
      supplierUrl: urlData[i][0] ? urlData[i][0].toString().trim() : '',
      purchasePrice: priceData[i][0] ? priceData[i][0].toString().trim() : '',
    });
  }

  return history;
}


// ================================================================
// 履歴から最も完全な情報を取得
// 各フィールドを個別に最新のものから探す
// （仕入先が空でも型番はある、等のケースに対応）
// ================================================================
function findBestHistory_(history, parentSku) {
  var records = history[parentSku];
  if (!records || records.length === 0) return null;

  var model = '';
  var supplier = '';
  var supplierUrl = '';
  var purchasePrice = '';

  // 新しい順に走査し、各フィールドで最初に見つかった値を採用
  for (var i = 0; i < records.length; i++) {
    var rec = records[i];
    if (!model && rec.model) model = rec.model;
    if (!supplier && rec.supplier) supplier = rec.supplier;
    if (!supplierUrl && rec.supplierUrl) supplierUrl = rec.supplierUrl;
    if (!purchasePrice && rec.purchasePrice) purchasePrice = rec.purchasePrice;

    // 全部揃ったら終了
    if (model && supplier && supplierUrl && purchasePrice) break;
  }

  return {
    model: model,
    supplier: supplier,
    supplierUrl: supplierUrl,
    purchasePrice: purchasePrice,
  };
}


// ================================================================
// SKUから親SKUを抽出
// 例: "V0265-12.5Z-44" → "V0265"
// 最初のハイフンより前の英数字部分
// ================================================================
function extractParentSKU_(sku) {
  if (!sku) return '';
  sku = sku.toString().trim();
  var match = sku.match(/^([A-Za-z]*\d+)/);
  return match ? match[1] : sku;
}


// ================================================================
// 型番ルールシートを読み込み
// ================================================================
function loadModelRules_(ss) {
  var rulesSheet = ss.getSheetByName(RULES_SHEET_NAME);
  if (!rulesSheet) {
    Logger.log('型番ルールシートが見つかりません: ' + RULES_SHEET_NAME);
    return [];
  }

  var data = rulesSheet.getDataRange().getValues();
  var rules = [];

  // ヘッダー行（行2）をスキップしてデータ行を読み込み
  for (var i = 2; i < data.length; i++) {
    var brand = data[i][1] ? data[i][1].toString().trim() : '';
    var titleModel = data[i][3] ? data[i][3].toString().trim() : '';
    var sheetModel = data[i][4] ? data[i][4].toString().trim() : '';

    if (brand) {
      rules.push({
        brand: brand,
        titleModel: titleModel,
        sheetModel: sheetModel,
      });
    }
  }

  return rules;
}


// ================================================================
// eBayタイトルから型番を抽出
// ブランドを検出し、ブランドごとのルールで変換
// ================================================================
function extractModelFromTitle_(title, rules) {
  if (!title) return '';

  var upperTitle = title.toUpperCase();

  // --- オニツカタイガー / アシックス ---
  // タイトル内の型番: "1183A201 003" → 仕入管理表: "1183A201.003"（スペースをドットに）
  if (upperTitle.indexOf('ONITSUKA') >= 0 || upperTitle.indexOf('ASICS') >= 0) {
    // パターン1: 数字4桁+英字1+数字3桁 + スペース/ハイフン + 数字3桁（カラーコード）
    var matchAsics = title.match(/(\d{4}[A-Za-z]\d{3})\s*[-\s]\s*(\d{3})/);
    if (matchAsics) {
      return matchAsics[1].toUpperCase() + '.' + matchAsics[2];
    }
    // パターン2: 型番 + 英字カラーコード（例: "1083A001 BRW"）
    var matchColor = title.match(/(\d{4}[A-Za-z]\d{3})\s+([A-Za-z]{2,4})\b/);
    if (matchColor) {
      return matchColor[1].toUpperCase() + ' ' + matchColor[2].toUpperCase();
    }
    // パターン3: 型番のみ（カラーコードなし）
    var matchOnly = title.match(/(\d{4}[A-Za-z]\d{3})/);
    if (matchOnly) {
      return matchOnly[1].toUpperCase();
    }
  }

  // --- ナイキ / ジョーダン ---
  // タイトル内の型番: "IQ3417-100" → そのまま
  if (upperTitle.indexOf('NIKE') >= 0
   || upperTitle.indexOf('JORDAN') >= 0
   || upperTitle.indexOf('AIR MAX') >= 0
   || upperTitle.indexOf('DUNK') >= 0) {
    // パターン: 英字2-3桁 + 数字4桁 + ハイフン + 数字3桁
    var matchNike = title.match(/\b([A-Za-z]{2,3}\d{4}-\d{3})\b/);
    if (matchNike) {
      return matchNike[1].toUpperCase();
    }
    // パターン2: 英字1桁 + 数字5桁 + ハイフン + 数字3桁（例: "D1234-001"）
    var matchNike2 = title.match(/\b([A-Za-z]\d{5}-\d{3})\b/);
    if (matchNike2) {
      return matchNike2[1].toUpperCase();
    }
  }

  // --- アディダス ---
  // タイトル内の型番: "KI8571" → そのまま
  if (upperTitle.indexOf('ADIDAS') >= 0) {
    var matchAdidas = title.match(/\b([A-Za-z]{2}\d{4,5})\b/);
    if (matchAdidas) {
      return matchAdidas[1].toUpperCase();
    }
  }

  // --- ミズノ ---
  if (upperTitle.indexOf('MIZUNO') >= 0) {
    var matchMizuno = title.match(/\b([A-Za-z]\d[A-Za-z]{2}\d{4})\b/);
    if (matchMizuno) {
      return matchMizuno[1].toUpperCase();
    }
  }

  // --- コンバース ---
  if (upperTitle.indexOf('CONVERSE') >= 0) {
    var matchConverse = title.match(/\b(\d{7,8})\b/);
    if (matchConverse) {
      return matchConverse[1];
    }
  }

  // --- プーマ ---
  if (upperTitle.indexOf('PUMA') >= 0) {
    var matchPuma = title.match(/\b(\d{6}-\d{2})\b/);
    if (matchPuma) {
      return matchPuma[1];
    }
  }

  // --- 汎用パターン: 英数字ハイフン形式 ---
  var generalMatch = title.match(/\b([A-Za-z]{1,3}\d{3,5}-\d{2,3})\b/);
  if (generalMatch) {
    return generalMatch[1].toUpperCase();
  }

  // 抽出できない場合は空欄
  return '';
}


// ================================================================
// 1つのオーダーから仕入管理表の行データを構築
// ================================================================
function buildRowData_(order, history, modelRules) {
  var parentSku = extractParentSKU_(order.sku);
  var hist = findBestHistory_(history, parentSku);

  // 型番の決定: 履歴 > タイトルから抽出
  var model = '';
  if (hist && hist.model) {
    model = hist.model;
  } else {
    model = extractModelFromTitle_(order.title, modelRules);
  }

  // New Balance等のWidth情報をサイズ末尾に付加
  // 例: "US10/JP28" + "　D" → "US10/JP28　D"（全角スペース区切り）
  var size = order.variationDetails || '';
  var width = extractWidth_(order.title);
  if (width) {
    size = size ? (size + '　' + width) : width;
  }

  return {
    shipBy: formatDateMD_(order.shipByDate),              // B: 発送期限（例: "4/16"）
    sku: order.sku,                                        // C: SKU
    model: model,                                          // F: 型番
    supplier: (hist && hist.supplier) || '',                // G: 仕入先
    supplierUrl: (hist && hist.supplierUrl) || '',          // H: 仕入先URL
    purchasePrice: (hist && hist.purchasePrice) || '',      // J: 仕入値
    size: size,                                            // L: サイズ（Width付き）
    hasStock: order.hasStock,                              // 有在庫フラグ
    title: order.title,                                    // O: タイトル
    itemUrl: 'https://www.ebay.com/itm/' + order.itemId,   // eBay商品ページURL
    orderNo: order.orderNumber,                            // Q: Order no.
    notes: order.isCancelRequested ? 'キャンセル確認' : '', // R: 備考
  };
}


// ================================================================
// シートに新規行データを一括追記
// O列（タイトル）はeBay商品ページへのハイパーリンク付き
// ※ ツールが管理する列のみに書き込み、N列（申告額USD）等の既存数式を保護する
// ================================================================
function appendRows_(sheet, rowsData) {
  if (rowsData.length === 0) return;

  // 実データの最終行を探す（SKU列=C列で判定。空行・書式のみの行をスキップ）
  var startRow = findLastDataRow_(sheet) + 1;
  var numRows = rowsData.length;
  var maxCol = COL.NOTES; // R列 = 18

  // --- 行が足りない場合、既存行のフォーマットをコピーして自動追加 ---
  var sheetLastRow = sheet.getMaxRows();
  var neededLastRow = startRow + numRows - 1;
  if (neededLastRow > sheetLastRow) {
    var rowsToAdd = neededLastRow - sheetLastRow;
    // 既存の最終行（フォーマットの元になる行）
    var templateRow = startRow - 1;
    if (templateRow < HEADER_ROW + 1) templateRow = HEADER_ROW + 1;
    // 行を追加
    sheet.insertRowsAfter(sheetLastRow, rowsToAdd);
    // フォーマット（書式・条件付き書式・数式）をコピー
    var srcRange = sheet.getRange(templateRow, 1, 1, maxCol);
    var dstRange = sheet.getRange(sheetLastRow + 1, 1, rowsToAdd, maxCol);
    srcRange.copyTo(dstRange, SpreadsheetApp.CopyPasteType.PASTE_FORMAT, false);
    // 数式もコピー（N列のGOOGLEFINANCE等）
    srcRange.copyTo(dstRange, SpreadsheetApp.CopyPasteType.PASTE_FORMULA, false);
    Logger.log(rowsToAdd + '行を自動追加（フォーマット継承）');
  }

  // --- ツールが書き込む列の定義（N列=14を含まない） ---
  // 列ごとにデータ配列を作成して個別に書き込む
  var writeCols = [
    { col: COL.SHIP_BY,         key: 'shipBy' },         // B列(2)  発送期限
    { col: COL.SKU,             key: 'sku' },             // C列(3)  SKU
    { col: COL.MODEL,           key: 'model' },           // F列(6)  型番
    { col: COL.SUPPLIER,        key: 'supplier' },        // G列(7)  仕入先
    { col: COL.SUPPLIER_URL,    key: 'supplierUrl' },     // H列(8)  仕入先URL
    { col: COL.PURCHASE_PRICE,  key: 'purchasePrice' },   // J列(10) 仕入値
    { col: COL.SIZE,            key: 'size' },            // L列(12) サイズ
    { col: COL.TITLE,           key: 'title' },           // O列(15) タイトル（後でリッチテキスト上書き）
    { col: COL.ORDER_NO,        key: 'orderNo' },         // Q列(17) Order No.
    { col: COL.NOTES,           key: 'notes' }            // R列(18) 備考
  ];

  // --- 列ごとに一括書き込み（N列等の既存数式を保護） ---
  for (var c = 0; c < writeCols.length; c++) {
    var colDef = writeCols[c];
    var colValues = [];
    for (var i = 0; i < numRows; i++) {
      colValues.push([rowsData[i][colDef.key] || '']);
    }
    sheet.getRange(startRow, colDef.col, numRows, 1).setValues(colValues);
  }

  // --- O列にハイパーリンクを設定（リッチテキストは個別設定が必要） ---
  for (var i = 0; i < numRows; i++) {
    var row = rowsData[i];
    if (row.title && row.itemUrl) {
      var richText = SpreadsheetApp.newRichTextValue()
        .setText(row.title)
        .setLinkUrl(row.itemUrl)
        .build();
      var titleCell = sheet.getRange(startRow + i, COL.TITLE);
      titleCell.setRichTextValue(richText);
      titleCell.setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP); // セルからはみ出さない
    }
  }

  // --- L列：有在庫の場合「※有在庫」を赤文字で追加（リッチテキスト） ---
  for (var i = 0; i < numRows; i++) {
    var row = rowsData[i];
    if (row.hasStock) {
      var sizeText = row.size || '';
      var stockLabel = '　※有在庫'; // 全角スペース + ラベル
      var fullText = sizeText + stockLabel;
      var richText = SpreadsheetApp.newRichTextValue()
        .setText(fullText)
        .setTextStyle(sizeText.length, fullText.length,
          SpreadsheetApp.newTextStyle().setForegroundColor('#FF0000').build())
        .build();
      sheet.getRange(startRow + i, COL.SIZE).setRichTextValue(richText);
    }
  }

  // --- E列：同一オーダーで複数商品がある場合、送料セルを結合 ---
  var COL_SHIPPING = 5; // E列 = 送料
  var i = 0;
  while (i < numRows) {
    var currentOrder = rowsData[i].orderNo;
    var groupStart = i;
    // 同じオーダー番号の連続行を探す
    while (i + 1 < numRows && rowsData[i + 1].orderNo === currentOrder) {
      i++;
    }
    var groupEnd = i;
    // 2行以上あれば結合
    if (groupEnd > groupStart) {
      var mergeRange = sheet.getRange(startRow + groupStart, COL_SHIPPING, groupEnd - groupStart + 1, 1);
      mergeRange.merge();
    }
    i++;
  }

  Logger.log(numRows + '行を行' + startRow + 'から書き込み完了');
}


// ================================================================
// 実データの最終行を取得（SKU列=C列で判定）
// 空行・書式のみ・チェックボックスのみの行をスキップする
// ================================================================
function findLastDataRow_(sheet) {
  var lastRow = sheet.getLastRow();
  if (lastRow <= HEADER_ROW) return HEADER_ROW;

  // SKU列（C列）を一括読み込みして、下から上に走査
  var dataRows = lastRow - HEADER_ROW;
  var skuValues = sheet.getRange(HEADER_ROW + 1, COL.SKU, dataRows, 1).getValues();

  for (var i = dataRows - 1; i >= 0; i--) {
    var val = skuValues[i][0];
    if (val !== '' && val !== null && val !== undefined) {
      return HEADER_ROW + i + 1; // 実データの最終行番号を返す
    }
  }

  return HEADER_ROW; // データなし
}


// ================================================================
// SKUを重複チェック用に正規化（比較時のみZ除去。シート書き込みはZ付きのまま）
//
// 運用: シートにはZ付きSKU（有在庫フラグ）をそのまま保持する。
// ただし過去に一時的にZ無しで書き込まれたデータがある可能性があるため、
// 重複判定時はAPI側・シート側の両方をこの関数でZ除去正規化して比較する。
//
// 例:
//   V0126-8.5Z-30 → V0126-8.5-30  （サイズ部分のZを除去）
//   Z0196-11-23   → Z0196-11-23   （親SKU先頭のZは温存）
//   V0126-8.5Z    → V0126-8.5     （末尾のZも除去）
// ================================================================
function normalizeSkuForCompare_(sku) {
  if (sku === null || sku === undefined) return '';
  var s = sku.toString().trim();
  // サイズ部分のZ（数字直後のZが「-」または末尾の前）を除去
  return s.replace(/(\d+\.?\d*)Z(?=-|$)/, '$1');
}


// ================================================================
// 既存オーダーのキー一覧を取得（重複防止用）
// OrderNo + SKU（正規化後）の組み合わせでユニークキーを作る
// （1つのオーダーに複数商品がある場合に対応）
// ※ シート側・API側の両方をnormalizeSkuForCompare_でZ除去正規化して比較するため
//   過去のZ無しデータとZ付きデータが混在していても正しく重複判定できる
// ================================================================
function getExistingOrderKeys_(sheet) {
  var lastRow = findLastDataRow_(sheet);
  var keys = new Set();
  var existingOrderNumbers = new Set();  // 対策G: orderNumber単位の存在チェック用

  if (lastRow > HEADER_ROW) {
    var dataRows = lastRow - HEADER_ROW;
    var orderNos = sheet.getRange(HEADER_ROW + 1, COL.ORDER_NO, dataRows, 1).getValues();
    var skus = sheet.getRange(HEADER_ROW + 1, COL.SKU, dataRows, 1).getValues();

    for (var i = 0; i < dataRows; i++) {
      var orderNo = orderNos[i][0] ? orderNos[i][0].toString().trim() : '';
      var sku = normalizeSkuForCompare_(skus[i][0]);  // Z除去正規化
      if (orderNo) {
        keys.add(orderNo + '|' + sku);
        existingOrderNumbers.add(orderNo);
      }
    }
  }

  // orderNumber単位の存在チェックも返す（重複疑惑検出用）
  keys.orderNumbersSet = existingOrderNumbers;
  return keys;
}


// ================================================================
// 営業日を加算（土日を除く）
// ================================================================
function addBusinessDays_(startDate, businessDays) {
  var date = new Date(startDate.getTime());
  var added = 0;

  while (added < businessDays) {
    date.setDate(date.getDate() + 1);
    var dayOfWeek = date.getDay();
    // 0=日曜, 6=土曜 はスキップ
    if (dayOfWeek !== 0 && dayOfWeek !== 6) {
      added++;
    }
  }

  return date;
}


// ================================================================
// 日付を M/D 形式にフォーマット（例: "4/16"）
// ================================================================
function formatDateMD_(date) {
  return (date.getMonth() + 1) + '/' + date.getDate();
}


// ================================================================
// XML子要素のテキストを安全に取得するヘルパー
// ================================================================
function getChildText_(element, childName, ns) {
  var child = element.getChild(childName, ns);
  return child ? child.getText() : '';
}


// ================================================================
// メッセージ表示（UI利用可能時はダイアログ、不可時はログ）
// トリガー実行時はUIが使えないためtry/catch
// ================================================================
function showMessage_(message) {
  Logger.log(message);
  try {
    SpreadsheetApp.getUi().alert(message);
  } catch (e) {
    // トリガー実行時はUIが使えない → ログのみ
  }
}


// ================================================================
// eBay API設定をScript Propertiesから取得
// ================================================================
function getEbayConfig_() {
  var props = PropertiesService.getScriptProperties();
  return {
    devId: props.getProperty('EBAY_DEV_ID') || '',
    appId: props.getProperty('EBAY_APP_ID') || '',
    certId: props.getProperty('EBAY_CERT_ID') || '',
    userToken: props.getProperty('EBAY_USER_TOKEN') || '',
  };
}


// ================================================================
// eBay API認証情報の設定（メニューから呼ばれる）
// Script Propertiesに保存 → コードに直書きしない（セキュリティ対策）
// ================================================================
function setupApiCredentials() {
  var ui = SpreadsheetApp.getUi();

  var result = ui.alert(
    'eBay API設定',
    'eBay APIの認証情報を設定します。\n'
    + '4つの値を順番に入力します。\n\n'
    + '1. DEV_ID\n'
    + '2. APP_ID\n'
    + '3. CERT_ID\n'
    + '4. USER_TOKEN\n\n'
    + '続けますか？',
    ui.ButtonSet.YES_NO
  );

  if (result !== ui.Button.YES) return;

  var props = PropertiesService.getScriptProperties();

  var fields = [
    { key: 'EBAY_DEV_ID', label: 'DEV_ID' },
    { key: 'EBAY_APP_ID', label: 'APP_ID' },
    { key: 'EBAY_CERT_ID', label: 'CERT_ID' },
    { key: 'EBAY_USER_TOKEN', label: 'USER_TOKEN' },
  ];

  for (var fi = 0; fi < fields.length; fi++) {
    var field = fields[fi];
    var current = props.getProperty(field.key);
    var displayCurrent = current
      ? (current.length > 30 ? current.substring(0, 30) + '...' : current)
      : '(未設定)';

    var response = ui.prompt(
      field.label + ' を入力してください',
      '現在の値: ' + displayCurrent + '\n\n空欄でOKを押すと変更しません。',
      ui.ButtonSet.OK_CANCEL
    );

    if (response.getSelectedButton() !== ui.Button.OK) {
      ui.alert('設定をキャンセルしました。');
      return;
    }

    var value = response.getResponseText().trim();
    if (value) {
      props.setProperty(field.key, value);
    }
  }

  ui.alert('✅ eBay API設定が完了しました！\n\n'
    + '「📥 新規オーダー反映」ボタンでテストしてください。');
}


// ================================================================
// 毎朝10時の自動実行トリガーを設定
// ================================================================
function setDailyTrigger() {
  // 既存のトリガーがあれば削除（重複防止）
  removeDailyTrigger();

  // 毎朝9:45頃のトリガーを作成（9:30〜10:00の間に実行される）
  // スタッフが10時から仕入れ開始するため、10時前に完了させる
  ScriptApp.newTrigger('fetchAndPopulateOrders')
    .timeBased()
    .atHour(9)
    .nearMinute(45)
    .everyDays(1)
    .create();

  showMessage_('✅ 毎朝9:45頃の自動実行を設定しました！\n\n'
    + 'Google側の仕様で、実行時刻は9:30〜10:00の間になります。\n'
    + '10時のスタッフ始業前に完了します。');
}


// ================================================================
// 自動実行トリガーを解除
// ================================================================
function removeDailyTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'fetchAndPopulateOrders') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
}


// ================================================================
// 【デバッグ用】特定オーダーの生XMLを取得してログに出力
// キャンセル情報がXMLのどこに入っているかを調査するための関数
// ================================================================
function debugSingleOrder() {
  var ui = SpreadsheetApp.getUi();
  var response = ui.prompt(
    '特定オーダーのXML確認',
    '調査したいOrder番号を入力してください\n（例: 13-14513-64889）',
    ui.ButtonSet.OK_CANCEL
  );
  if (response.getSelectedButton() !== ui.Button.OK) return;

  var orderId = response.getResponseText().trim();
  if (!orderId) { ui.alert('Order番号が空です'); return; }

  var config = getEbayConfig_();
  if (!config.userToken) {
    ui.alert('⚠️ eBay APIが未設定です。');
    return;
  }

  var xmlRequest = '<?xml version="1.0" encoding="utf-8"?>'
    + '<GetOrdersRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
    + '<RequesterCredentials><eBayAuthToken>' + config.userToken + '</eBayAuthToken></RequesterCredentials>'
    + '<OrderIDArray><OrderID>' + orderId + '</OrderID></OrderIDArray>'
    + '<OrderStatus>All</OrderStatus>'
    + '<DetailLevel>ReturnAll</DetailLevel>'
    + '</GetOrdersRequest>';

  var options = {
    method: 'post',
    contentType: 'text/xml',
    headers: {
      'X-EBAY-API-DEV-NAME': config.devId,
      'X-EBAY-API-APP-NAME': config.appId,
      'X-EBAY-API-CERT-NAME': config.certId,
      'X-EBAY-API-CALL-NAME': 'GetOrders',
      'X-EBAY-API-COMPATIBILITY-LEVEL': EBAY_COMPAT_LEVEL,
      'X-EBAY-API-SITEID': EBAY_SITE_ID,
    },
    payload: xmlRequest,
    muteHttpExceptions: true,
  };

  var apiResponse = UrlFetchApp.fetch(EBAY_API_URL, options);
  var xmlText = apiResponse.getContentText();

  // ログに全文出力（Apps Scriptエディタの実行ログで確認）
  Logger.log('===== ' + orderId + ' の生XML =====');
  Logger.log(xmlText);

  ui.alert('✅ XMLをログに出力しました。\n\n'
    + 'Apps Scriptエディタ → 「実行数」→ 最新の実行 → ログ で確認してください。\n\n'
    + '特に以下のタグを重点確認:\n'
    + '・OrderStatus\n'
    + '・CancelStatus / CancelState / CancelReason\n'
    + '・BuyerRequestedCancel\n'
    + '・MonetaryDetails (Refund情報)');
}


// ================================================================
// 【対策H】重複安全チェック（本番反映前に実行推奨）
// 既存シート内に、Z除去正規化後に同一キーになる行が複数無いかを事前検査する。
// 本番でバージョンアップ後の初回実行による重複書き込みリスクをゼロにするため、
// 転送直後・初回実行前に手動で一度実行しておくことを推奨。
//
// チェック内容:
//   1. OrderNo+正規化SKU で重複している既存行（既に重複が発生している = 手動削除対象）
//   2. Z付きSKUとZ無しSKUが混在しているorderNumber（将来の重複リスク）
// ================================================================
function checkDuplicatesSafety() {
  var ui = SpreadsheetApp.getUi();
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);

  if (!sheet) {
    ui.alert('エラー: シート「' + SHEET_NAME + '」が見つかりません');
    return;
  }

  var lastRow = findLastDataRow_(sheet);
  if (lastRow <= HEADER_ROW) {
    ui.alert('データがありません。チェック不要です。');
    return;
  }

  var dataRows = lastRow - HEADER_ROW;
  var orderNos = sheet.getRange(HEADER_ROW + 1, COL.ORDER_NO, dataRows, 1).getValues();
  var skus = sheet.getRange(HEADER_ROW + 1, COL.SKU, dataRows, 1).getValues();

  // 1. 正規化後キーの重複検出
  var keyToRows = {};   // 正規化キー → 行番号配列
  // 2. orderNumber 単位での Z混在検出
  var orderToSkus = {}; // orderNumber → 生SKU配列

  for (var i = 0; i < dataRows; i++) {
    var rowNo = HEADER_ROW + 1 + i;
    var orderNo = orderNos[i][0] ? orderNos[i][0].toString().trim() : '';
    var rawSku = skus[i][0] ? skus[i][0].toString().trim() : '';
    if (!orderNo) continue;

    var key = orderNo + '|' + normalizeSkuForCompare_(rawSku);
    if (!keyToRows[key]) keyToRows[key] = [];
    keyToRows[key].push(rowNo);

    if (!orderToSkus[orderNo]) orderToSkus[orderNo] = [];
    orderToSkus[orderNo].push(rawSku);
  }

  // 既存重複（正規化キーが2回以上出現する行）を抽出
  var existingDuplicates = [];
  for (var k in keyToRows) {
    if (keyToRows[k].length > 1) {
      existingDuplicates.push({ key: k, rows: keyToRows[k] });
    }
  }

  // Z混在（同じorderNumberでZ付きとZ無しのSKUが混在）を抽出
  var zMixedOrders = [];
  for (var on in orderToSkus) {
    var skuList = orderToSkus[on];
    var hasZ = false, hasNonZ = false;
    for (var j = 0; j < skuList.length; j++) {
      if (/(\d+\.?\d*)Z(?=-|$)/.test(skuList[j])) { hasZ = true; }
      else { hasNonZ = true; }
    }
    if (hasZ && hasNonZ) {
      zMixedOrders.push({ orderNo: on, skus: skuList });
    }
  }

  // 結果出力
  var report = '【重複安全チェック結果】\n\n';
  report += '総データ件数: ' + dataRows + '\n';
  report += 'ユニークキー数: ' + Object.keys(keyToRows).length + '\n\n';

  if (existingDuplicates.length === 0) {
    report += '✅ 既存の重複行: なし\n\n';
  } else {
    report += '⚠️ 既存の重複行: ' + existingDuplicates.length + '組\n';
    report += '（以下の行は同じOrder+SKUです。手動で整理してください）\n';
    for (var d = 0; d < Math.min(existingDuplicates.length, 10); d++) {
      report += '  - キー: ' + existingDuplicates[d].key
        + ' → 行 ' + existingDuplicates[d].rows.join(', ') + '\n';
    }
    if (existingDuplicates.length > 10) {
      report += '  （他' + (existingDuplicates.length - 10) + '組。詳細はログ参照）\n';
    }
    report += '\n';
  }

  if (zMixedOrders.length === 0) {
    report += '✅ Z付き/Z無し混在オーダー: なし\n';
    report += '→ 本番反映後の初回実行で重複書き込みは発生しません。\n';
  } else {
    report += '⚠️ Z付き/Z無し混在オーダー: ' + zMixedOrders.length + '件\n';
    report += '（本番反映時の新ロジックでは正規化後に同一扱いされるため問題なし）\n';
  }

  Logger.log(report);
  // 詳細は全てログ出力
  for (var d2 = 0; d2 < existingDuplicates.length; d2++) {
    Logger.log('重複: ' + existingDuplicates[d2].key
      + ' at rows ' + existingDuplicates[d2].rows.join(','));
  }
  for (var z = 0; z < zMixedOrders.length; z++) {
    Logger.log('Z混在: ' + zMixedOrders[z].orderNo
      + ' SKUs=' + zMixedOrders[z].skus.join(','));
  }

  ui.alert(report);
}


// ================================================================
// 前回処理時刻プロパティをリセット（初期化）
// リカバリ・再反映したい場合に使用
// ================================================================
function resetLastProcessedTime() {
  var ui = SpreadsheetApp.getUi();
  var props = PropertiesService.getScriptProperties();
  var current = props.getProperty(PROP_LAST_CREATED_TIME) || '(未設定)';

  var response = ui.alert(
    '前回処理時刻をリセット',
    '現在の値: ' + current + '\n\n'
    + 'リセットすると、次回実行時は過去' + FETCH_DAYS_BACK + '日分全てが候補になります。\n'
    + '（既に反映済みのオーダーは重複チェックで除外されます）\n\n'
    + 'リセットしますか？',
    ui.ButtonSet.YES_NO
  );

  if (response === ui.Button.YES) {
    props.deleteProperty(PROP_LAST_CREATED_TIME);
    ui.alert('✅ リセットしました。');
  }
}
