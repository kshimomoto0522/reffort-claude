// ウェビナー資料「eBay × AI運営」PowerPoint生成スクリプト
// 16:9横長スライド・ビジュアル重視・日本語対応
// 依存: pptxgenjs のみ

const pptxgen = require("pptxgenjs");
const path = require("path");

// ============================
// カラーパレット — Midnight Executive
// ============================
const C = {
  navy:     "1E2761",  // プライマリ（濃紺）
  ice:      "CADCFC",  // セカンダリ（アイスブルー）
  white:    "FFFFFF",
  offWhite: "F0F4FA",  // スライド背景用
  dark:     "0B1437",  // ほぼ黒
  mid:      "4A5568",  // 本文グレー
  accent:   "F59E0B",  // アンバー（アクセント）
  accentDk: "D97706",
  red:      "EF4444",
  green:    "10B981",
  teal:     "0D9488",
  lightGray:"E2E8F0",
};

// フォント
const F = {
  title:  "Arial Black",
  head:   "Arial Black",
  body:   "Calibri",
  mono:   "Consolas",
};

// ============================
// ヘルパー関数
// ============================

// オプションオブジェクトの再利用防止用（PptxGenJSがmutateするため）
const shadow = () => ({ type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.12 });
const cardShadow = () => ({ type: "outer", color: "000000", blur: 8, offset: 3, angle: 135, opacity: 0.10 });

// ダークスライド背景
function darkBg(slide) {
  slide.background = { color: C.navy };
}
// ライトスライド背景
function lightBg(slide) {
  slide.background = { color: C.offWhite };
}

// ページ番号を全スライドに追加
function addPageNum(slide, num, total, dark = false) {
  slide.addText(`${num} / ${total}`, {
    x: 8.5, y: 5.2, w: 1.2, h: 0.3,
    fontSize: 9, fontFace: F.body,
    color: dark ? "7A8BAD" : C.mid,
    align: "right",
  });
}

// セクションヘッダー（ライトスライド上のパートタイトル）
function addSectionHeader(slide, partNum, title) {
  // 上部にネイビーバー
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.navy }
  });
  // パート番号バッジ
  slide.addShape(pres.shapes.OVAL, {
    x: 0.5, y: 0.35, w: 0.55, h: 0.55, fill: { color: C.navy }
  });
  slide.addText(String(partNum), {
    x: 0.5, y: 0.35, w: 0.55, h: 0.55,
    fontSize: 18, fontFace: F.head, color: C.white,
    align: "center", valign: "middle",
  });
  // タイトル
  slide.addText(title, {
    x: 1.2, y: 0.3, w: 8, h: 0.6,
    fontSize: 28, fontFace: F.head, color: C.navy,
    valign: "middle", margin: 0,
  });
  // アクセントライン
  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.05, w: 9, h: 0,
    line: { color: C.ice, width: 2 }
  });
}

// カードを描画（白い角丸長方形 + シャドウ）
function addCard(slide, x, y, w, h) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: C.white },
    shadow: cardShadow(),
  });
}

// 数字のインパクトカード
function addStatCard(slide, x, y, w, h, number, label, numColor) {
  addCard(slide, x, y, w, h);
  slide.addText(number, {
    x, y: y + 0.15, w, h: h * 0.55,
    fontSize: 36, fontFace: F.head, color: numColor || C.navy,
    align: "center", valign: "middle", bold: true,
  });
  slide.addText(label, {
    x: x + 0.1, y: y + h * 0.55, w: w - 0.2, h: h * 0.4,
    fontSize: 11, fontFace: F.body, color: C.mid,
    align: "center", valign: "top",
  });
}

// ============================
// プレゼンテーション生成
// ============================

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "下元 敬介（株式会社リフォート）";
pres.title = "eBay × AI運営 ウェビナー 2026.04.26";

const TOTAL = 24;
let slideNum = 0;

// ==========================================
// スライド1: 表紙（ダーク）
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  darkBg(s);
  // 装飾：左サイドにアクセントバー
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.12, h: 5.625, fill: { color: C.accent }
  });
  // 右下に大きな円形装飾
  s.addShape(pres.shapes.OVAL, {
    x: 7.5, y: 3.2, w: 3.5, h: 3.5,
    fill: { color: "253380", transparency: 60 }
  });
  // メインタイトル
  s.addText("eBay × AI運営", {
    x: 0.8, y: 1.0, w: 8, h: 1.2,
    fontSize: 44, fontFace: F.title, color: C.white,
    bold: true, margin: 0,
  });
  // サブタイトル
  s.addText("Claude Codeで変わった\neBayビジネスのすべて", {
    x: 0.8, y: 2.2, w: 7, h: 1.0,
    fontSize: 22, fontFace: F.body, color: C.ice,
    margin: 0,
  });
  // 日付・話者
  s.addShape(pres.shapes.LINE, {
    x: 0.8, y: 3.5, w: 3, h: 0,
    line: { color: C.accent, width: 2 }
  });
  s.addText("2026年4月26日（土）", {
    x: 0.8, y: 3.65, w: 5, h: 0.35,
    fontSize: 14, fontFace: F.body, color: C.ice, margin: 0,
  });
  s.addText("下元 敬介 ─ 株式会社リフォート 代表取締役", {
    x: 0.8, y: 4.0, w: 5, h: 0.35,
    fontSize: 13, fontFace: F.body, color: "7A8BAD", margin: 0,
  });
  s.addText("Campersメンバー限定ウェビナー", {
    x: 0.8, y: 4.4, w: 5, h: 0.35,
    fontSize: 12, fontFace: F.body, color: "7A8BAD", margin: 0,
  });
}

// ==========================================
// スライド2: アジェンダ（ダーク）
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("AGENDA", {
    x: 0.5, y: 0.3, w: 4, h: 0.6,
    fontSize: 14, fontFace: F.head, color: C.accent,
    charSpacing: 6, margin: 0,
  });
  s.addText("今日お話しすること", {
    x: 0.5, y: 0.8, w: 6, h: 0.6,
    fontSize: 30, fontFace: F.head, color: C.white, margin: 0,
  });

  const items = [
    { num: "01", title: "なぜ今この話をするのか", time: "5分" },
    { num: "02", title: "Claude Codeとは？ChatGPTと何が違うのか", time: "15分" },
    { num: "03", title: "自分がeBay運営で実際にAI化したこと", time: "30分" },
    { num: "04", title: "eBay以外にClaude Codeでやったこと", time: "15分" },
    { num: "05", title: "使う人と使わない人でどれだけ差がつくか", time: "10分" },
    { num: "06", title: "Campers AIコースのご案内", time: "10分" },
    { num: "07", title: "Q&A", time: "自由" },
  ];

  items.forEach((item, i) => {
    const yBase = 1.6 + i * 0.52;
    // 番号
    s.addText(item.num, {
      x: 0.5, y: yBase, w: 0.6, h: 0.42,
      fontSize: 16, fontFace: F.head, color: C.accent,
      valign: "middle", margin: 0,
    });
    // タイトル
    s.addText(item.title, {
      x: 1.2, y: yBase, w: 6.5, h: 0.42,
      fontSize: 16, fontFace: F.body, color: C.white,
      valign: "middle", margin: 0,
    });
    // 時間
    s.addText(item.time, {
      x: 8.2, y: yBase, w: 1.2, h: 0.42,
      fontSize: 13, fontFace: F.body, color: "7A8BAD",
      align: "right", valign: "middle", margin: 0,
    });
    // 区切り線
    if (i < items.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: 1.2, y: yBase + 0.48, w: 8.2, h: 0,
        line: { color: "2D3A6E", width: 0.5 }
      });
    }
  });

  s.addText("約90分", {
    x: 8, y: 5.1, w: 1.5, h: 0.35,
    fontSize: 12, fontFace: F.body, color: "7A8BAD",
    align: "right", margin: 0,
  });
  addPageNum(s, slideNum, TOTAL, true);
}

// ==========================================
// スライド3: パート1 — なぜ今この話をするのか（ダーク）
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  darkBg(s);

  s.addText("PART 1", {
    x: 0.5, y: 0.4, w: 3, h: 0.4,
    fontSize: 12, fontFace: F.head, color: C.accent,
    charSpacing: 4, margin: 0,
  });
  s.addText("なぜ今この話をするのか", {
    x: 0.5, y: 0.85, w: 9, h: 0.7,
    fontSize: 32, fontFace: F.head, color: C.white, margin: 0,
  });

  // 3つの現実カード
  const cards = [
    { stat: "~40名", label: "Campers現在のメンバー数\n（70名→40名に減少）", color: C.accent },
    { stat: "$60K/月", label: "eBay売上【要確認】\n（関税影響で下落）", color: C.red },
    { stat: "1.5ヶ月", label: "AI導入からの期間\n（2026年3月11日〜）", color: C.green },
  ];

  cards.forEach((c, i) => {
    const x = 0.5 + i * 3.1;
    const y = 2.0;
    addCard(s, x, y, 2.8, 2.2);
    s.addText(c.stat, {
      x, y: y + 0.25, w: 2.8, h: 0.8,
      fontSize: 32, fontFace: F.head, color: c.color,
      align: "center", valign: "middle", bold: true,
    });
    s.addText(c.label, {
      x: x + 0.15, y: y + 1.15, w: 2.5, h: 0.85,
      fontSize: 12, fontFace: F.body, color: C.mid,
      align: "center", valign: "top",
    });
  });

  s.addText("「同じやり方を続けているだけでは、生き残れない」", {
    x: 0.5, y: 4.5, w: 9, h: 0.5,
    fontSize: 16, fontFace: F.body, color: C.ice,
    italic: true, align: "center", margin: 0,
  });
  addPageNum(s, slideNum, TOTAL, true);
}

// ==========================================
// スライド4: パート2 タイトル — Claude Codeとは？
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("PART 2", {
    x: 0.5, y: 1.5, w: 3, h: 0.4,
    fontSize: 12, fontFace: F.head, color: C.accent,
    charSpacing: 4, margin: 0,
  });
  s.addText("Claude Codeとは？\nChatGPTと何が違うのか", {
    x: 0.5, y: 2.0, w: 9, h: 1.5,
    fontSize: 36, fontFace: F.head, color: C.white, margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.5, y: 3.6, w: 2, h: 0,
    line: { color: C.accent, width: 3 }
  });
  addPageNum(s, slideNum, TOTAL, true);
}

// ==========================================
// スライド5: ChatGPT vs Claude Code — 一言比較
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 2, "ChatGPT vs Claude Code");

  // 左カード: ChatGPT
  addCard(s, 0.5, 1.4, 4.2, 3.5);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.4, w: 4.2, h: 0.06, fill: { color: C.mid }
  });
  s.addText("ChatGPT", {
    x: 0.5, y: 1.6, w: 4.2, h: 0.6,
    fontSize: 22, fontFace: F.head, color: C.mid,
    align: "center", valign: "middle",
  });
  s.addText("＝", {
    x: 0.5, y: 2.3, w: 4.2, h: 0.4,
    fontSize: 18, fontFace: F.body, color: C.mid,
    align: "center",
  });
  s.addText("物知りな相談相手", {
    x: 0.5, y: 2.7, w: 4.2, h: 0.7,
    fontSize: 24, fontFace: F.head, color: C.mid,
    align: "center", valign: "middle",
  });
  s.addText([
    { text: "質問すれば答えてくれる", options: { breakLine: true } },
    { text: "でも実行は全部自分", options: {} },
  ], {
    x: 0.8, y: 3.6, w: 3.6, h: 0.8,
    fontSize: 13, fontFace: F.body, color: C.mid,
    align: "center",
  });

  // 右カード: Claude Code
  addCard(s, 5.3, 1.4, 4.2, 3.5);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.3, y: 1.4, w: 4.2, h: 0.06, fill: { color: C.navy }
  });
  s.addText("Claude Code", {
    x: 5.3, y: 1.6, w: 4.2, h: 0.6,
    fontSize: 22, fontFace: F.head, color: C.navy,
    align: "center", valign: "middle",
  });
  s.addText("＝", {
    x: 5.3, y: 2.3, w: 4.2, h: 0.4,
    fontSize: 18, fontFace: F.body, color: C.navy,
    align: "center",
  });
  s.addText("自分の会社専属の\n秘書＋エンジニア", {
    x: 5.3, y: 2.6, w: 4.2, h: 0.9,
    fontSize: 22, fontFace: F.head, color: C.navy,
    align: "center", valign: "middle",
  });
  s.addText([
    { text: "指示すれば全部やってくれる", options: { breakLine: true } },
    { text: "ファイル操作・ツール連携・定期実行", options: {} },
  ], {
    x: 5.6, y: 3.6, w: 3.6, h: 0.8,
    fontSize: 13, fontFace: F.body, color: C.navy,
    align: "center",
  });

  // 中央矢印
  s.addText("VS", {
    x: 4.2, y: 2.6, w: 1.6, h: 0.6,
    fontSize: 18, fontFace: F.head, color: C.accent,
    align: "center", valign: "middle", bold: true,
  });

  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド6: 4つの違い — 比較表
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 2, "4つの決定的な違い");

  const rows = [
    ["", "ChatGPT", "Claude Code"],
    ["記憶", "毎回リセット", "事業を完全に記憶（CLAUDE.md）"],
    ["ファイル操作", "できない", "PCのファイルを直接読み書き"],
    ["ツール連携", "なし", "Chatwork・eBay API・スプレッドシート等"],
    ["定期実行", "なし", "毎週・毎日の自動タスク"],
  ];

  const headerOpts = { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 13, fontFace: F.body, align: "center", valign: "middle" };
  const cellL = { fontSize: 12, fontFace: F.body, color: C.mid, valign: "middle", align: "center" };
  const cellR = { fontSize: 12, fontFace: F.body, color: C.navy, bold: true, valign: "middle", align: "center" };
  const rowLabel = { fontSize: 13, fontFace: F.head, color: C.navy, bold: true, valign: "middle" };

  const tableRows = rows.map((row, ri) => {
    if (ri === 0) {
      return row.map(cell => ({ text: cell, options: headerOpts }));
    }
    return [
      { text: row[0], options: rowLabel },
      { text: row[1], options: cellL },
      { text: row[2], options: cellR },
    ];
  });

  s.addTable(tableRows, {
    x: 0.5, y: 1.3, w: 9, h: 3.5,
    colW: [2.2, 3.0, 3.8],
    border: { pt: 0.5, color: C.lightGray },
    rowH: [0.5, 0.7, 0.7, 0.7, 0.7],
    autoPage: false,
  });

  s.addText("一言でいうと：「答えをもらう」 → 「全部やってもらう」", {
    x: 0.5, y: 4.9, w: 9, h: 0.4,
    fontSize: 14, fontFace: F.body, color: C.accent,
    bold: true, align: "center", margin: 0,
  });
  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド7: パート3 タイトル — 実際にAI化したこと
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("PART 3", {
    x: 0.5, y: 1.2, w: 3, h: 0.4,
    fontSize: 12, fontFace: F.head, color: C.accent,
    charSpacing: 4, margin: 0,
  });
  s.addText("自分がeBay運営で\n実際にAI化したこと", {
    x: 0.5, y: 1.7, w: 9, h: 1.5,
    fontSize: 36, fontFace: F.head, color: C.white, margin: 0,
  });
  s.addText("数字・失敗談も含めて全部お話しします", {
    x: 0.5, y: 3.3, w: 9, h: 0.5,
    fontSize: 16, fontFace: F.body, color: C.ice, margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.5, y: 3.9, w: 2, h: 0,
    line: { color: C.accent, width: 3 }
  });
  addPageNum(s, slideNum, TOTAL, true);
}

// ==========================================
// スライド8: 最初の3日間 — 土台を作る
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 3, "最初の3日間 ― 土台を作る");

  // タイムライン
  s.addText("3月11日〜13日", {
    x: 0.5, y: 1.2, w: 3, h: 0.35,
    fontSize: 12, fontFace: F.body, color: C.accent, bold: true, margin: 0,
  });

  // 左：やったこと
  addCard(s, 0.5, 1.7, 4.3, 3.2);
  s.addText("AIに自分の会社を教えた", {
    x: 0.7, y: 1.85, w: 3.9, h: 0.45,
    fontSize: 16, fontFace: F.head, color: C.navy, margin: 0,
  });
  s.addText([
    { text: "会社の事業内容", options: { bullet: true, breakLine: true } },
    { text: "各事業の現状と課題", options: { bullet: true, breakLine: true } },
    { text: "スタッフの役割", options: { bullet: true, breakLine: true } },
    { text: "使っているツール", options: { bullet: true, breakLine: true } },
    { text: "目指している方向性", options: { bullet: true } },
  ], {
    x: 0.9, y: 2.45, w: 3.7, h: 2.2,
    fontSize: 13, fontFace: F.body, color: C.mid,
    paraSpaceAfter: 4,
  });

  // 右：学び
  addCard(s, 5.2, 1.7, 4.3, 3.2);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.7, w: 0.08, h: 3.2, fill: { color: C.accent }
  });
  s.addText("学び", {
    x: 5.5, y: 1.85, w: 3.8, h: 0.45,
    fontSize: 16, fontFace: F.head, color: C.accent, margin: 0,
  });
  s.addText("AIは使い始めが一番大事。\n最初に正しい土台を作れるかどうかで、\nその後の1ヶ月が全て変わる。", {
    x: 5.5, y: 2.45, w: 3.8, h: 1.5,
    fontSize: 14, fontFace: F.body, color: C.dark,
    italic: true,
  });
  s.addText("→ これが「CLAUDE.md」\n   自分の会社専用の指示書", {
    x: 5.5, y: 3.9, w: 3.8, h: 0.7,
    fontSize: 13, fontFace: F.body, color: C.navy, bold: true,
  });

  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド9: eBay週次レポートの完全自動化
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 3, "eBay週次レポートの完全自動化");

  s.addText("毎週月曜 朝10時に、12シートのレポートが自動で届く", {
    x: 0.5, y: 1.2, w: 9, h: 0.4,
    fontSize: 15, fontFace: F.body, color: C.navy, bold: true, margin: 0,
  });

  // 2列のレポート一覧
  const leftItems = [
    "AI総評（今週やるべきこと）",
    "サマリー（売上・CVR・Impressions推移）",
    "コア売れ筋TOP15",
    "コア落ち（急落した商品）",
    "準売れ筋",
    "育成候補",
  ];
  const rightItems = [
    "要調査（異常データ商品）",
    "削除候補",
    "改善追跡",
    "コア月間・削除月間",
    "週次履歴（過去12週分）",
    "+ Googleスプレッドシート同時書込",
  ];

  addCard(s, 0.5, 1.75, 4.3, 3.0);
  leftItems.forEach((item, i) => {
    s.addText([
      { text: `${i + 1}. `, options: { bold: true, color: C.accent } },
      { text: item, options: { color: C.dark } },
    ], {
      x: 0.7, y: 1.9 + i * 0.42, w: 3.9, h: 0.38,
      fontSize: 12, fontFace: F.body, valign: "middle", margin: 0,
    });
  });

  addCard(s, 5.2, 1.75, 4.3, 3.0);
  rightItems.forEach((item, i) => {
    s.addText([
      { text: `${i + 7}. `, options: { bold: true, color: C.accent } },
      { text: item, options: { color: C.dark } },
    ], {
      x: 5.4, y: 1.9 + i * 0.42, w: 3.9, h: 0.38,
      fontSize: 12, fontFace: F.body, valign: "middle", margin: 0,
    });
  });

  s.addText("CSVダウンロード不要 → eBay APIから直接データ取得", {
    x: 0.5, y: 4.9, w: 9, h: 0.4,
    fontSize: 13, fontFace: F.body, color: C.teal,
    bold: true, align: "center", margin: 0,
  });
  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド10: 衝撃の数字
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 3, "レポートで判明した衝撃の数字");

  // 3つの大きな数字カード
  addStatCard(s, 0.5, 1.5, 2.8, 2.2, "92.7%", "出品の9割以上が\n売上ゼロ", C.red);
  addStatCard(s, 3.6, 1.5, 2.8, 2.2, "0.221%", "全体CVR\n（業界平均2〜3%の1/10）", C.red);
  addStatCard(s, 6.7, 1.5, 2.8, 2.2, "2,647件", "売上ゼロの出品数\n（総出品2,856件中）", C.accent);

  // メッセージ
  addCard(s, 0.5, 4.0, 9, 1.2);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.0, w: 0.08, h: 1.2, fill: { color: C.navy }
  });
  s.addText([
    { text: "「なんとなく」で運営していたものが、AIで数字になった。\n", options: { bold: true, color: C.navy, fontSize: 15, breakLine: true } },
    { text: "数字が見えれば、打ち手が見える。", options: { bold: true, color: C.accent, fontSize: 15 } },
  ], {
    x: 0.8, y: 4.1, w: 8.5, h: 1.0,
    fontFace: F.body, valign: "middle",
  });
  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド11: 広告費の実態
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 3, "広告費の実態が初めて見えた話");

  // 左：広告費の内訳（ドーナツチャート）
  s.addChart(pres.charts.DOUGHNUT, [{
    name: "広告費内訳",
    labels: ["PLG $3,446", "PLP $491", "Offsite $1,928"],
    values: [3446, 491, 1928],
  }], {
    x: 0.3, y: 1.3, w: 4.5, h: 3.5,
    showPercent: true,
    showTitle: false,
    showLegend: true,
    legendPos: "b",
    chartColors: [C.navy, C.teal, C.accent],
    dataLabelColor: C.dark,
  });

  // 右：インパクト数字
  addCard(s, 5.2, 1.3, 4.3, 1.2);
  s.addText("$5,865/月", {
    x: 5.2, y: 1.35, w: 4.3, h: 0.65,
    fontSize: 32, fontFace: F.head, color: C.red,
    align: "center", valign: "middle", bold: true,
  });
  s.addText("年間約$70,000 ─ 売上の8.8%", {
    x: 5.2, y: 2.05, w: 4.3, h: 0.4,
    fontSize: 13, fontFace: F.body, color: C.mid,
    align: "center",
  });

  // 発見リスト
  addCard(s, 5.2, 2.7, 4.3, 2.5);
  const findings = [
    { label: "発見①", text: "PLGキャンペーンが10個重複" },
    { label: "発見②", text: "PLG帰属率103%（税金状態）" },
    { label: "発見③", text: "Offsite 2,878商品中売れたの58件" },
    { label: "発見④", text: "$200超の商品は販売率27%に急落" },
  ];
  findings.forEach((f, i) => {
    s.addText([
      { text: f.label + "  ", options: { bold: true, color: C.accent, fontSize: 11 } },
      { text: f.text, options: { color: C.dark, fontSize: 12 } },
    ], {
      x: 5.4, y: 2.85 + i * 0.55, w: 3.9, h: 0.45,
      fontFace: F.body, valign: "middle", margin: 0,
    });
  });

  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド12: 仕入管理ツール自動化
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 3, "仕入管理ツールの自動化");

  // Before/After 2列
  // Before
  addCard(s, 0.5, 1.4, 4.3, 3.3);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.4, w: 4.3, h: 0.5, fill: { color: C.mid }
  });
  s.addText("BEFORE", {
    x: 0.5, y: 1.4, w: 4.3, h: 0.5,
    fontSize: 14, fontFace: F.head, color: C.white,
    align: "center", valign: "middle",
  });
  s.addText([
    { text: "eBay管理画面を手動で確認", options: { bullet: true, breakLine: true } },
    { text: "スプレッドシートに手動転記", options: { bullet: true, breakLine: true } },
    { text: "型番・仕入先を毎回手入力", options: { bullet: true, breakLine: true } },
    { text: "キャンセル検出は目視", options: { bullet: true, breakLine: true } },
    { text: "ミスが頻発", options: { bullet: true } },
  ], {
    x: 0.8, y: 2.1, w: 3.7, h: 2.4,
    fontSize: 13, fontFace: F.body, color: C.mid,
    paraSpaceAfter: 6,
  });

  // After
  addCard(s, 5.2, 1.4, 4.3, 3.3);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.4, w: 4.3, h: 0.5, fill: { color: C.navy }
  });
  s.addText("AFTER", {
    x: 5.2, y: 1.4, w: 4.3, h: 0.5,
    fontSize: 14, fontFace: F.head, color: C.white,
    align: "center", valign: "middle",
  });
  s.addText([
    { text: "eBay API → スプレッドシート自動反映", options: { bullet: true, breakLine: true } },
    { text: "型番・仕入先・仕入価格を自動入力", options: { bullet: true, breakLine: true } },
    { text: "キャンセルリクエスト自動検出", options: { bullet: true, breakLine: true } },
    { text: "発送期限を自動計算", options: { bullet: true, breakLine: true } },
    { text: "商品ページへのリンク自動付与", options: { bullet: true } },
  ], {
    x: 5.5, y: 2.1, w: 3.7, h: 2.4,
    fontSize: 13, fontFace: F.body, color: C.navy,
    paraSpaceAfter: 6,
  });

  s.addText("スタッフの毎日の転記作業がゼロに", {
    x: 0.5, y: 4.9, w: 9, h: 0.4,
    fontSize: 15, fontFace: F.body, color: C.accent,
    bold: true, align: "center", margin: 0,
  });
  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド13: 在庫チェック＋CS返信AI
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 3, "在庫チェック改修 ＆ CS返信AI");

  // 左カード：在庫チェック
  addCard(s, 0.5, 1.4, 4.3, 2.0);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.4, w: 0.08, h: 2.0, fill: { color: C.red }
  });
  s.addText("在庫チェックツール改修", {
    x: 0.8, y: 1.5, w: 3.8, h: 0.4,
    fontSize: 15, fontFace: F.head, color: C.navy, margin: 0,
  });
  s.addText("3日間壊れていたのに誰も気づかなかった\n→ 異常時Chatwork自動通知を追加", {
    x: 0.8, y: 2.0, w: 3.8, h: 0.8,
    fontSize: 12, fontFace: F.body, color: C.mid,
  });
  s.addText("自動化は「作って終わり」じゃない。\n壊れた時に気づく仕組みとセットで完成する。", {
    x: 0.8, y: 2.8, w: 3.8, h: 0.5,
    fontSize: 11, fontFace: F.body, color: C.accent, italic: true,
  });

  // 右カード：CS返信AI
  addCard(s, 5.2, 1.4, 4.3, 2.0);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.4, w: 0.08, h: 2.0, fill: { color: C.teal }
  });
  s.addText("CS返信のAI自動生成", {
    x: 5.5, y: 1.5, w: 3.8, h: 0.4,
    fontSize: 15, fontFace: F.head, color: C.navy, margin: 0,
  });
  s.addText("プロンプトをv1.0→v2.3まで5回改善\nテスト12回以上 / 6モデル比較", {
    x: 5.5, y: 2.0, w: 3.8, h: 0.8,
    fontSize: 12, fontFace: F.body, color: C.mid,
  });
  s.addText("AIへの「指示の出し方」を磨くこと\n＝ AIを使いこなすということ", {
    x: 5.5, y: 2.8, w: 3.8, h: 0.5,
    fontSize: 11, fontFace: F.body, color: C.teal, italic: true,
  });

  // 下部：学びまとめ
  addCard(s, 0.5, 3.7, 9, 1.5);
  s.addText("パート3 まとめ：1ヶ月半で変わったこと", {
    x: 0.7, y: 3.8, w: 8.6, h: 0.4,
    fontSize: 15, fontFace: F.head, color: C.navy, margin: 0,
  });

  const summary = [
    ["売上データ", "目視 → 12シート自動レポート"],
    ["広告費", "不明 → $5,865/月と正確に把握"],
    ["仕入管理", "手動転記 → 完全自動化"],
    ["在庫チェック", "壊れても気づかない → 異常通知"],
  ];
  summary.forEach((item, i) => {
    const xStart = 0.7 + (i % 2) * 4.5;
    const yStart = 4.3 + Math.floor(i / 2) * 0.4;
    s.addText([
      { text: item[0] + "：", options: { bold: true, color: C.navy } },
      { text: item[1], options: { color: C.mid } },
    ], {
      x: xStart, y: yStart, w: 4.2, h: 0.35,
      fontSize: 11, fontFace: F.body, margin: 0,
    });
  });

  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド14: パート4 タイトル — eBay以外
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("PART 4", {
    x: 0.5, y: 1.5, w: 3, h: 0.4,
    fontSize: 12, fontFace: F.head, color: C.accent,
    charSpacing: 4, margin: 0,
  });
  s.addText("eBay以外に\nClaude Codeでやったこと", {
    x: 0.5, y: 2.0, w: 9, h: 1.5,
    fontSize: 36, fontFace: F.head, color: C.white, margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.5, y: 3.6, w: 2, h: 0,
    line: { color: C.accent, width: 3 }
  });
  addPageNum(s, slideNum, TOTAL, true);
}

// ==========================================
// スライド15: Webアプリ ＋ X情報ダイジェスト
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 4, "Webアプリ開発 ＆ 情報収集自動化");

  // 左カード：Webアプリ
  addCard(s, 0.5, 1.4, 4.3, 3.8);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.4, w: 4.3, h: 0.5, fill: { color: C.navy }
  });
  s.addText("注文管理Webアプリ", {
    x: 0.5, y: 1.4, w: 4.3, h: 0.5,
    fontSize: 15, fontFace: F.head, color: C.white,
    align: "center", valign: "middle",
  });
  s.addText([
    { text: "バイヤーがスマホから商品を選んで注文", options: { bullet: true, breakLine: true } },
    { text: "注文→管理画面に自動反映", options: { bullet: true, breakLine: true } },
    { text: "仕入指示→仕入完了→発送管理まで一気通貫", options: { bullet: true, breakLine: true } },
    { text: "拠点ごとの在庫管理", options: { bullet: true, breakLine: true } },
    { text: "クーポン管理機能", options: { bullet: true } },
  ], {
    x: 0.8, y: 2.1, w: 3.7, h: 2.3,
    fontSize: 12, fontFace: F.body, color: C.mid,
    paraSpaceAfter: 6,
  });
  s.addText("プログラミング経験ゼロで作った", {
    x: 0.5, y: 4.6, w: 4.3, h: 0.4,
    fontSize: 12, fontFace: F.body, color: C.accent,
    bold: true, align: "center",
  });

  // 右カード：X情報ダイジェスト
  addCard(s, 5.2, 1.4, 4.3, 1.7);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.4, w: 0.08, h: 1.7, fill: { color: C.teal }
  });
  s.addText("X情報ダイジェスト", {
    x: 5.5, y: 1.5, w: 3.8, h: 0.4,
    fontSize: 15, fontFace: F.head, color: C.navy, margin: 0,
  });
  s.addText("毎朝9:40にChatworkの自分のDMに届く\nSNSを開く時間ゼロで重要情報だけ受取\nコスト：月150〜300円", {
    x: 5.5, y: 2.0, w: 3.8, h: 0.9,
    fontSize: 12, fontFace: F.body, color: C.mid,
  });

  // その他
  addCard(s, 5.2, 3.3, 4.3, 1.9);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 3.3, w: 0.08, h: 1.9, fill: { color: C.accent }
  });
  s.addText("その他の活用", {
    x: 5.5, y: 3.4, w: 3.8, h: 0.4,
    fontSize: 15, fontFace: F.head, color: C.navy, margin: 0,
  });
  s.addText([
    { text: "会社HPの管理を自分で", options: { bullet: true, breakLine: true } },
    { text: "スタッフへのClaude Code展開準備", options: { bullet: true, breakLine: true } },
    { text: "Campersメンバー管理の自動化", options: { bullet: true } },
  ], {
    x: 5.5, y: 3.9, w: 3.8, h: 1.1,
    fontSize: 12, fontFace: F.body, color: C.mid,
    paraSpaceAfter: 4,
  });

  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド16: セキュリティ
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 4, "セキュリティ対策（避けて通れない話）");

  const items = [
    { title: "APIトークンの安全管理", desc: "最初はコードに直書き→GitHubに上げてしまった → .envファイルに移行", icon: "!" },
    { title: "機密情報漏洩防止", desc: ".gitignoreで.envファイルをブロック。コードに秘密情報を書かない", icon: "!" },
    { title: "プロンプトインジェクション対策", desc: "悪意あるWebページがAIを騙して情報送信させるリスクへの対策", icon: "!" },
  ];

  items.forEach((item, i) => {
    const y = 1.4 + i * 1.2;
    addCard(s, 0.5, y, 9, 1.0);
    // 警告マーク
    s.addShape(pres.shapes.OVAL, {
      x: 0.7, y: y + 0.2, w: 0.6, h: 0.6,
      fill: { color: C.red }
    });
    s.addText("!", {
      x: 0.7, y: y + 0.2, w: 0.6, h: 0.6,
      fontSize: 20, fontFace: F.head, color: C.white,
      align: "center", valign: "middle", bold: true,
    });
    s.addText(item.title, {
      x: 1.5, y: y + 0.1, w: 7.8, h: 0.4,
      fontSize: 15, fontFace: F.head, color: C.navy, margin: 0,
    });
    s.addText(item.desc, {
      x: 1.5, y: y + 0.5, w: 7.8, h: 0.4,
      fontSize: 12, fontFace: F.body, color: C.mid, margin: 0,
    });
  });

  addCard(s, 0.5, 4.3, 9, 0.9);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.3, w: 0.08, h: 0.9, fill: { color: C.green }
  });
  s.addText("対策は簡単。知っているかどうかの問題。AIコースではここもしっかり教えます。", {
    x: 0.8, y: 4.3, w: 8.5, h: 0.9,
    fontSize: 14, fontFace: F.body, color: C.dark,
    valign: "middle", bold: true,
  });

  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド17: パート5 タイトル — 差がつく
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("PART 5", {
    x: 0.5, y: 1.5, w: 3, h: 0.4,
    fontSize: 12, fontFace: F.head, color: C.accent,
    charSpacing: 4, margin: 0,
  });
  s.addText("使う人と使わない人で\nどれだけ差がつくか", {
    x: 0.5, y: 2.0, w: 9, h: 1.5,
    fontSize: 36, fontFace: F.head, color: C.white, margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.5, y: 3.6, w: 2, h: 0,
    line: { color: C.accent, width: 3 }
  });
  addPageNum(s, slideNum, TOTAL, true);
}

// ==========================================
// スライド18: AI未使用 vs AI活用 比較表
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 5, "eBay運営で具体的にどう差がつくか");

  const rows = [
    ["業務", "AI未使用", "AI活用"],
    ["売上分析", "Seller Hub目視（週1時間+）", "自動レポートが届く（0分）"],
    ["商品改善", "感覚で判断", "データで4分類→アクション明確"],
    ["広告最適化", "一律5%で放置", "商品ごとに最適レートをAI提案"],
    ["CS対応", "1件10〜15分", "AI下書き→確認→送信（2〜3分）"],
    ["仕入管理", "手動転記", "注文→スプレッドシート自動反映"],
    ["情報収集", "SNS手動巡回", "AIが毎朝まとめて配信"],
  ];

  const hdr = { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 12, fontFace: F.body, align: "center", valign: "middle" };
  const cL = { fontSize: 11, fontFace: F.body, color: C.mid, valign: "middle" };
  const cR = { fontSize: 11, fontFace: F.body, color: C.navy, bold: true, valign: "middle" };
  const rL = { fontSize: 12, fontFace: F.head, color: C.navy, valign: "middle" };

  const tableRows = rows.map((row, ri) => {
    if (ri === 0) return row.map(c => ({ text: c, options: hdr }));
    return [
      { text: row[0], options: rL },
      { text: row[1], options: cL },
      { text: row[2], options: cR },
    ];
  });

  s.addTable(tableRows, {
    x: 0.5, y: 1.3, w: 9, h: 3.2,
    colW: [1.8, 3.2, 4.0],
    border: { pt: 0.5, color: C.lightGray },
    autoPage: false,
  });

  // インパクト数字
  addCard(s, 0.5, 4.6, 9, 0.7);
  s.addText("週あたりの運営時間：10〜15時間  →  3〜5時間に圧縮できる可能性", {
    x: 0.5, y: 4.6, w: 9, h: 0.7,
    fontSize: 16, fontFace: F.body, color: C.accent,
    bold: true, align: "center", valign: "middle",
  });

  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド19: eBay以外でも使えるスキル
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 5, "eBay以外でも使えるスキル");

  const skills = [
    { title: "物販全般", desc: "Amazon・メルカリ・ヤフオクでも同じデータ分析が可能" },
    { title: "どんなビジネスでも", desc: "レポート作成・CS対応・データ管理はどの事業にもある" },
    { title: "Webアプリ開発", desc: "プログラミング未経験でもツールが作れる" },
    { title: "副業・独立", desc: "AIを使ったサービス提供、コンサル、教育コンテンツ" },
    { title: "転職市場", desc: "「AIを業務に組み込める人材」の需要は爆発的に増加" },
  ];

  skills.forEach((sk, i) => {
    const y = 1.3 + i * 0.75;
    addCard(s, 0.5, y, 9, 0.65);
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 0.08, h: 0.65, fill: { color: C.navy }
    });
    s.addText(sk.title, {
      x: 0.8, y, w: 2.2, h: 0.65,
      fontSize: 14, fontFace: F.head, color: C.navy, valign: "middle", margin: 0,
    });
    s.addText(sk.desc, {
      x: 3.0, y, w: 6.3, h: 0.65,
      fontSize: 13, fontFace: F.body, color: C.mid, valign: "middle", margin: 0,
    });
  });

  s.addText("eBayセラーがAIを使いこなせるようになったら、そのスキル自体が価値になる", {
    x: 0.5, y: 4.9, w: 9, h: 0.4,
    fontSize: 14, fontFace: F.body, color: C.accent,
    bold: true, align: "center", italic: true, margin: 0,
  });

  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド20: 時代の話 — 先行者になれる
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  darkBg(s);

  s.addText("2026年の今、", {
    x: 0.8, y: 0.8, w: 8, h: 0.6,
    fontSize: 18, fontFace: F.body, color: C.ice, margin: 0,
  });
  s.addText("eBayセラーでAIを本格的に\n業務に組み込んでいる人は", {
    x: 0.8, y: 1.4, w: 9, h: 1.0,
    fontSize: 24, fontFace: F.head, color: C.white, margin: 0,
  });
  s.addText("ほぼいない。", {
    x: 0.8, y: 2.5, w: 9, h: 0.8,
    fontSize: 44, fontFace: F.head, color: C.accent, bold: true, margin: 0,
  });

  s.addShape(pres.shapes.LINE, {
    x: 0.8, y: 3.5, w: 3, h: 0,
    line: { color: C.accent, width: 2 }
  });

  s.addText("だから今始めれば、先行者になれる。", {
    x: 0.8, y: 3.7, w: 9, h: 0.6,
    fontSize: 20, fontFace: F.body, color: C.white, margin: 0,
  });
  s.addText("「あの時やっておけばよかった」ではなく\n「あの時始めてよかった」にしましょう。", {
    x: 0.8, y: 4.3, w: 9, h: 0.8,
    fontSize: 16, fontFace: F.body, color: C.ice, margin: 0,
  });

  addPageNum(s, slideNum, TOTAL, true);
}

// ==========================================
// スライド21: パート6 タイトル — AIコース案内
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText("PART 6", {
    x: 0.5, y: 1.5, w: 3, h: 0.4,
    fontSize: 12, fontFace: F.head, color: C.accent,
    charSpacing: 4, margin: 0,
  });
  s.addText("Campers AIコース\nのご案内", {
    x: 0.5, y: 2.0, w: 9, h: 1.5,
    fontSize: 36, fontFace: F.head, color: C.white, margin: 0,
  });
  s.addText("「実際にやっている人が、やりながら教える」", {
    x: 0.5, y: 3.6, w: 9, h: 0.5,
    fontSize: 16, fontFace: F.body, color: C.ice, italic: true, margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.5, y: 4.2, w: 2, h: 0,
    line: { color: C.accent, width: 3 }
  });
  addPageNum(s, slideNum, TOTAL, true);
}

// ==========================================
// スライド22: カリキュラム
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 6, "カリキュラム");

  const units = [
    { num: "1", title: "Claude Code入門", desc: "インストール・CLAUDE.md・セキュリティ設定" },
    { num: "2", title: "eBayデータ分析", desc: "レポートの読み方・CVR/CTR/Impressionsの改善" },
    { num: "3", title: "パフォーマンス管理", desc: "商品分類・広告最適化・週次レポート自動生成" },
    { num: "4", title: "業務自動化", desc: "eBay API・Chatwork連携・定期実行タスク" },
    { num: "5", title: "CS対応 × AI", desc: "バイヤー返信AI生成・返品対応・多言語対応" },
    { num: "6", title: "応用編", desc: "収支可視化・Webアプリ開発・自分の事業への応用" },
  ];

  units.forEach((u, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.5 + col * 3.1;
    const y = 1.3 + row * 2.0;

    addCard(s, x, y, 2.8, 1.7);
    // ユニット番号バッジ
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.15, y: y + 0.15, w: 0.5, h: 0.5,
      fill: { color: C.navy }
    });
    s.addText(u.num, {
      x: x + 0.15, y: y + 0.15, w: 0.5, h: 0.5,
      fontSize: 16, fontFace: F.head, color: C.white,
      align: "center", valign: "middle",
    });
    s.addText(u.title, {
      x: x + 0.75, y: y + 0.15, w: 1.9, h: 0.5,
      fontSize: 14, fontFace: F.head, color: C.navy,
      valign: "middle", margin: 0,
    });
    s.addText(u.desc, {
      x: x + 0.15, y: y + 0.8, w: 2.5, h: 0.7,
      fontSize: 11, fontFace: F.body, color: C.mid, margin: 0,
    });
  });

  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド23: 提供するもの＋費用
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  lightBg(s);
  addSectionHeader(s, 6, "提供するもの ＆ 費用");

  // 左：提供するもの
  addCard(s, 0.5, 1.3, 4.3, 3.5);
  s.addText("提供するもの", {
    x: 0.7, y: 1.4, w: 3.9, h: 0.45,
    fontSize: 16, fontFace: F.head, color: C.navy, margin: 0,
  });
  const provides = [
    "CLAUDE.mdテンプレート（eBayセラー用）",
    "セットアップガイド（実際の試行錯誤から作成）",
    "分析スクリプト・レポートテンプレート",
    "Chatworkグループでの質問対応",
    "定期講義 or 録画配信【要確認】",
  ];
  provides.forEach((p, i) => {
    s.addText([
      { text: "✓ ", options: { bold: true, color: C.green } },
      { text: p, options: { color: C.dark } },
    ], {
      x: 0.9, y: 2.0 + i * 0.5, w: 3.7, h: 0.4,
      fontSize: 12, fontFace: F.body, margin: 0,
    });
  });

  // 右：費用
  addCard(s, 5.2, 1.3, 4.3, 2.0);
  s.addText("必要な費用", {
    x: 5.4, y: 1.4, w: 3.9, h: 0.45,
    fontSize: 16, fontFace: F.head, color: C.navy, margin: 0,
  });
  s.addText([
    { text: "Claude Pro：月$20（約3,000円）", options: { breakLine: true } },
    { text: "eBay API：無料", options: { breakLine: true } },
    { text: "GitHub：無料", options: { breakLine: true } },
    { text: "Google系ツール：無料", options: {} },
  ], {
    x: 5.6, y: 2.0, w: 3.7, h: 1.2,
    fontSize: 12, fontFace: F.body, color: C.mid,
  });

  // コース料金（要確認）
  addCard(s, 5.2, 3.5, 4.3, 1.3);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 3.5, w: 4.3, h: 0.5, fill: { color: C.accent }
  });
  s.addText("コース料金【社長が決定】", {
    x: 5.2, y: 3.5, w: 4.3, h: 0.5,
    fontSize: 13, fontFace: F.head, color: C.white,
    align: "center", valign: "middle",
  });
  s.addText("月額制 or 一括払い\n金額は社長が決定", {
    x: 5.4, y: 4.1, w: 3.9, h: 0.6,
    fontSize: 12, fontFace: F.body, color: C.mid,
    align: "center",
  });

  s.addText("月3,000円で「自分の事業を理解している秘書＋エンジニア」が手に入る", {
    x: 0.5, y: 4.95, w: 9, h: 0.4,
    fontSize: 13, fontFace: F.body, color: C.accent,
    bold: true, align: "center", margin: 0,
  });

  addPageNum(s, slideNum, TOTAL);
}

// ==========================================
// スライド24: クロージング
// ==========================================
slideNum++;
{
  const s = pres.addSlide();
  darkBg(s);

  // 装飾
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.12, h: 5.625, fill: { color: C.accent }
  });
  s.addShape(pres.shapes.OVAL, {
    x: 7.5, y: 3.2, w: 3.5, h: 3.5,
    fill: { color: "253380", transparency: 60 }
  });

  s.addText("ありがとうございました", {
    x: 0.8, y: 1.0, w: 8, h: 0.8,
    fontSize: 36, fontFace: F.head, color: C.white, margin: 0,
  });

  s.addShape(pres.shapes.LINE, {
    x: 0.8, y: 2.0, w: 3, h: 0,
    line: { color: C.accent, width: 2 }
  });

  s.addText("この資料自体、Claude Codeが作成しました。", {
    x: 0.8, y: 2.3, w: 8, h: 0.5,
    fontSize: 16, fontFace: F.body, color: C.ice, margin: 0,
  });

  s.addText([
    { text: "実践ログ：約950行", options: { breakLine: true } },
    { text: "メモリファイル：15件以上", options: { breakLine: true } },
    { text: "各部門の指示書：8ファイル", options: {} },
  ], {
    x: 0.8, y: 2.9, w: 8, h: 1.0,
    fontSize: 14, fontFace: F.body, color: "7A8BAD",
  });

  s.addText("蓄積してきた情報が、必要な時に必要な形で出力される。\nこれがClaude Codeの真価です。", {
    x: 0.8, y: 4.0, w: 8, h: 0.8,
    fontSize: 16, fontFace: F.body, color: C.white,
    italic: true, margin: 0,
  });

  s.addText("Q&Aへ", {
    x: 8, y: 5.0, w: 1.5, h: 0.4,
    fontSize: 14, fontFace: F.body, color: C.accent,
    align: "right", margin: 0,
  });
}

// ============================
// ファイル出力
// ============================
const outputPath = path.join(__dirname, "webinar_20260426.pptx");
pres.writeFile({ fileName: outputPath })
  .then(() => {
    console.log("PPTX生成完了: " + outputPath);
  })
  .catch(err => {
    console.error("エラー:", err);
    process.exit(1);
  });
