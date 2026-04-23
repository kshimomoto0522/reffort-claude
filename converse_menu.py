"""
Converse MADE IN JAPAN - メニューPDF生成スクリプト v3
・在庫あり16商品のみ
・CANVAS ALL STAR J HI を先頭グループ、残りモデルは後続
・3列レイアウト、複数ページ対応、画像大きめ
"""

import requests
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ===== 在庫あり商品データ（英語カラー名・モデル別グループ順）=====
# グループ1: CANVAS ALL STAR J HI（先頭）
# グループ2: その他モデル（CANVAS 80s / SUEDE / LEATHER）

PRODUCTS = [
    # --- CANVAS ALL STAR J HI ---
    {"title": "CANVAS ALL STAR J HI",      "color": "Tree Green",              "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131731_0_1.jpg"},
    {"title": "CANVAS ALL STAR J HI",      "color": "Burgundy",                "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131671_0_1.jpg"},
    {"title": "CANVAS ALL STAR J HI",      "color": "Maroon / Dark Navy / Mint","img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131547_0_2.jpg"},
    {"title": "CANVAS ALL STAR J HI",      "color": "Graphite",                "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131515_0_1.jpg"},
    {"title": "CANVAS ALL STAR J HI",      "color": "Muscat Green",            "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131425_0_1.jpg"},
    {"title": "CANVAS ALL STAR J HI",      "color": "Purple",                  "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131219_0_1.jpg"},
    {"title": "CANVAS ALL STAR J HI",      "color": "Natural White",           "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/products/3206843_0_1.jpg"},
    {"title": "CANVAS ALL STAR J HI",      "color": "Black",                   "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/products/3206796_1_1.jpg"},
    {"title": "CANVAS ALL STAR J HI",      "color": "White",                   "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/products/3206796_0_1.jpg"},
    # --- CANVAS ALL STAR J 80s HI ---
    {"title": "CANVAS ALL STAR J 80s HI",  "color": "White",                   "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131177_0_1.jpg"},
    {"title": "CANVAS ALL STAR J 80s HI",  "color": "Green",                   "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131110_0_1.jpg"},
    # --- SUEDE ALL STAR J HI ---
    {"title": "SUEDE ALL STAR J HI",       "color": "Grape",                   "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131753_0_1.jpg"},
    {"title": "SUEDE ALL STAR J HI",       "color": "Black",                   "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131543_0_1.jpg"},
    # --- LEATHER ALL STAR J HI ---
    {"title": "LEATHER ALL STAR J HI",     "color": "Brown",                   "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131633_0_1.jpg"},
    {"title": "LEATHER ALL STAR J HI",     "color": "Deep Green",              "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131673_0_1.jpg"},
    {"title": "LEATHER ALL STAR J HI",     "color": "Black",                   "img": "https://cdn.shopify.com/s/files/1/0614/5608/9339/files/3131281_0_1.jpg"},
]

# ===== 画像ダウンロード =====
_img_cache = {}
def download_image(url):
    if url in _img_cache:
        return _img_cache[url]
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if resp.status_code == 200:
            img = ImageReader(io.BytesIO(resp.content))
            _img_cache[url] = img
            return img
    except Exception as e:
        print(f"  画像取得失敗: {e}")
    return None

# ===== PDF生成 =====
def create_menu():
    output_path = r"C:\Users\KEISUKE SHIMOMOTO\Desktop\converse_japan_menu_v3.pdf"
    W, H = A4  # 595 x 842 pt (210 x 297 mm)

    # カラー定義
    COLOR_BG       = colors.HexColor("#F5F4F1")
    COLOR_BLACK    = colors.HexColor("#1A1A1A")
    COLOR_ACCENT   = colors.HexColor("#C8112E")
    COLOR_DIVIDER  = colors.HexColor("#E0E0E0")
    COLOR_SUB      = colors.HexColor("#666666")
    COLOR_SEC_BG   = colors.HexColor("#EFEFED")  # セクションヘッダー背景

    FONT      = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

    # レイアウト定数
    COLS       = 3
    MARGIN     = 10 * mm
    GAP        = 4 * mm          # セル間隔
    HEADER_H   = 10 * mm         # ページ上部ヘッダー
    SEC_H      = 7 * mm          # セクション区切り高さ
    TEXT_H     = 14 * mm         # テキストエリア（モデル名+カラー）

    # セル幅（固定）
    cell_w = (W - 2 * MARGIN - (COLS - 1) * GAP) / COLS

    # セル高さ：画像をなるべく大きく（テキスト領域 + 画像）
    # ページ内に3行収める設計
    # 利用可能高さ = H - HEADER_H - MARGIN(top) - MARGIN(bottom)
    avail_h  = H - HEADER_H - 2 * MARGIN
    # 3行 + 2ギャップ分でセル高さを決定
    ROWS_PER_PAGE = 3
    cell_h   = (avail_h - (ROWS_PER_PAGE - 1) * GAP) / ROWS_PER_PAGE
    IMG_H    = cell_h - TEXT_H   # 画像の高さ

    c = canvas.Canvas(output_path, pagesize=A4)

    # ===== ページ描画ヘルパー =====
    def start_page():
        """新ページを開始して背景・ヘッダーを描画、コンテンツ開始y座標を返す"""
        c.setFillColor(COLOR_BG)
        c.rect(0, 0, W, H, fill=True, stroke=False)
        # ヘッダーバー
        c.setFillColor(COLOR_ACCENT)
        c.rect(0, H - HEADER_H, W, HEADER_H, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont(FONT_BOLD, 8)
        c.drawCentredString(W / 2, H - 6.5 * mm,
                            "CONVERSE  MADE IN JAPAN  —  Hi-Cut Collection  (April 2026)")
        # コンテンツ開始y（ヘッダー下端からMARGIN下）
        return H - HEADER_H - MARGIN

    def draw_section_header(title, y):
        """セクション区切り（モデル名ラベル）を描画してy消費量を返す"""
        c.setFillColor(COLOR_SEC_BG)
        c.rect(MARGIN, y - SEC_H, W - 2 * MARGIN, SEC_H, fill=True, stroke=False)
        c.setFillColor(COLOR_ACCENT)
        c.rect(MARGIN, y - SEC_H, 3, SEC_H, fill=True, stroke=False)  # 左端の赤ライン
        c.setFont(FONT_BOLD, 7.5)
        c.setFillColor(COLOR_BLACK)
        c.drawString(MARGIN + 5, y - SEC_H + 2.5 * mm, title)
        return SEC_H + 2 * mm  # 消費高さ（下の余白込み）

    def draw_card(product, x, y):
        """1商品カードを描画"""
        print(f"  {product['title']} / {product['color']}")
        # カード背景
        c.setFillColor(colors.white)
        c.setStrokeColor(COLOR_DIVIDER)
        c.setLineWidth(0.4)
        c.roundRect(x, y, cell_w, cell_h, 2 * mm, fill=True, stroke=True)

        # 画像
        img = download_image(product["img"])
        img_x = x + 1.5 * mm
        img_y = y + TEXT_H
        img_w = cell_w - 3 * mm

        if img:
            try:
                c.drawImage(img, img_x, img_y, width=img_w, height=IMG_H,
                            preserveAspectRatio=True, anchor='c')
            except Exception as e:
                print(f"    描画失敗: {e}")
                c.setFillColor(colors.HexColor("#EEEEEE"))
                c.rect(img_x, img_y, img_w, IMG_H, fill=True, stroke=False)
        else:
            c.setFillColor(colors.HexColor("#EEEEEE"))
            c.rect(img_x, img_y, img_w, IMG_H, fill=True, stroke=False)

        # モデル名
        c.setFillColor(COLOR_BLACK)
        c.setFont(FONT_BOLD, 6)
        title_str = product["title"]
        title_w = c.stringWidth(title_str, FONT_BOLD, 6)
        max_w = cell_w - 4 * mm
        if title_w > max_w:
            # 2行に折り返す
            mid = title_str.rfind(" ", 0, len(title_str) // 2 + 4)
            if mid == -1:
                mid = len(title_str) // 2
            c.drawString(x + 2 * mm, y + TEXT_H - 4 * mm, title_str[:mid])
            c.drawString(x + 2 * mm, y + TEXT_H - 7.5 * mm, title_str[mid:].strip())
        else:
            c.drawString(x + 2 * mm, y + TEXT_H - 4 * mm, title_str)

        # カラー名（英語）
        c.setFont(FONT, 6)
        c.setFillColor(COLOR_SUB)
        c.drawString(x + 2 * mm, y + 3 * mm, product["color"])

    # ===== レイアウト制御 =====
    # モデルグループを検出してセクション区切りを挿入
    groups = []
    current_group = []
    current_title = None
    for p in PRODUCTS:
        if p["title"] != current_title:
            if current_group:
                groups.append((current_title, current_group))
            current_title = p["title"]
            current_group = [p]
        else:
            current_group.append(p)
    if current_group:
        groups.append((current_title, current_group))

    # 描画開始
    top_y = start_page()
    y_cursor = top_y   # 現在の描画位置（上端）
    col_idx  = 0       # 現在の列位置

    def flush_row_if_needed():
        """行が中途半端に終わった場合にy_cursorを更新"""
        nonlocal y_cursor, col_idx
        if col_idx > 0:
            y_cursor -= cell_h + GAP
            col_idx = 0

    def ensure_space(needed_h):
        """指定高さ分の空きがなければ改ページ"""
        nonlocal y_cursor, col_idx
        if y_cursor - needed_h < MARGIN:
            flush_row_if_needed()
            c.showPage()
            y_cursor = start_page()
            col_idx = 0

    total = sum(len(items) for _, items in groups)
    print(f"在庫あり商品数: {total}")

    for group_title, items in groups:
        # 行の途中ならまず行を締める
        flush_row_if_needed()

        # セクションヘッダーのスペース確保
        ensure_space(SEC_H + 2 * mm + cell_h + GAP)

        # セクションヘッダー描画
        consumed = draw_section_header(group_title, y_cursor)
        y_cursor -= consumed

        # グループ内の商品を描画
        for p in items:
            # 行末まで来たら次の行へ
            if col_idx == COLS:
                y_cursor -= cell_h + GAP
                col_idx = 0
                # ページをまたぐ場合
                if y_cursor - cell_h < MARGIN:
                    c.showPage()
                    y_cursor = start_page()
                    col_idx = 0

            x = MARGIN + col_idx * (cell_w + GAP)
            y = y_cursor - cell_h

            draw_card(p, x, y)
            col_idx += 1

    # 最終行の後処理
    flush_row_if_needed()

    c.save()
    print(f"\nPDF作成完了: {output_path}")


if __name__ == "__main__":
    create_menu()
