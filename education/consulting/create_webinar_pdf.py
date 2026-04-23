# -*- coding: utf-8 -*-
"""
ウェビナー資料（Markdown）→ PDF変換スクリプト
日本語対応（NotoSansJP使用）
"""

import os
import re
import urllib.request

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ============================
# フォント設定（日本語対応）
# ============================
# Windows標準の游ゴシックを使用
pdfmetrics.registerFont(TTFont("NotoSansJP", "C:/Windows/Fonts/YuGothR.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("NotoSansJP-Bold", "C:/Windows/Fonts/YuGothB.ttc", subfontIndex=0))

# ============================
# カラー定義
# ============================
COLOR_PRIMARY = HexColor("#1a56db")    # 見出しの青
COLOR_ACCENT = HexColor("#e74c3c")     # 強調の赤
COLOR_BG_LIGHT = HexColor("#f0f4ff")   # 薄い青背景
COLOR_BG_TABLE = HexColor("#f8f9fa")   # テーブル背景
COLOR_BORDER = HexColor("#d1d5db")     # テーブル罫線
COLOR_DARK = HexColor("#1f2937")       # 本文

# ============================
# スタイル定義
# ============================
def create_styles():
    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title", fontName="NotoSansJP-Bold", fontSize=28,
        leading=38, textColor=COLOR_PRIMARY, alignment=TA_CENTER,
        spaceAfter=10
    )
    styles["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle", fontName="NotoSansJP", fontSize=14,
        leading=20, textColor=COLOR_DARK, alignment=TA_CENTER,
        spaceAfter=6
    )
    styles["cover_info"] = ParagraphStyle(
        "cover_info", fontName="NotoSansJP", fontSize=11,
        leading=16, textColor=HexColor("#6b7280"), alignment=TA_CENTER,
        spaceAfter=4
    )
    styles["h1"] = ParagraphStyle(
        "h1", fontName="NotoSansJP-Bold", fontSize=20,
        leading=28, textColor=COLOR_PRIMARY, spaceBefore=20, spaceAfter=12,
        borderWidth=0, borderPadding=0
    )
    styles["h2"] = ParagraphStyle(
        "h2", fontName="NotoSansJP-Bold", fontSize=16,
        leading=22, textColor=COLOR_DARK, spaceBefore=16, spaceAfter=8
    )
    styles["h3"] = ParagraphStyle(
        "h3", fontName="NotoSansJP-Bold", fontSize=13,
        leading=18, textColor=HexColor("#374151"), spaceBefore=12, spaceAfter=6
    )
    styles["body"] = ParagraphStyle(
        "body", fontName="NotoSansJP", fontSize=10.5,
        leading=17, textColor=COLOR_DARK, spaceBefore=2, spaceAfter=4
    )
    styles["body_bold"] = ParagraphStyle(
        "body_bold", fontName="NotoSansJP-Bold", fontSize=10.5,
        leading=17, textColor=COLOR_DARK, spaceBefore=2, spaceAfter=4
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", fontName="NotoSansJP", fontSize=10.5,
        leading=17, textColor=COLOR_DARK, leftIndent=18,
        firstLineIndent=-12, spaceBefore=1, spaceAfter=1
    )
    styles["sub_bullet"] = ParagraphStyle(
        "sub_bullet", fontName="NotoSansJP", fontSize=10,
        leading=16, textColor=HexColor("#4b5563"), leftIndent=34,
        firstLineIndent=-12, spaceBefore=1, spaceAfter=1
    )
    styles["quote"] = ParagraphStyle(
        "quote", fontName="NotoSansJP-Bold", fontSize=11,
        leading=18, textColor=COLOR_PRIMARY, leftIndent=16,
        borderColor=COLOR_PRIMARY, borderWidth=2, borderPadding=(8, 8, 8, 12),
        backColor=COLOR_BG_LIGHT, spaceBefore=8, spaceAfter=8
    )
    styles["confirm"] = ParagraphStyle(
        "confirm", fontName="NotoSansJP-Bold", fontSize=10.5,
        leading=16, textColor=COLOR_ACCENT, leftIndent=16,
        borderColor=COLOR_ACCENT, borderWidth=2, borderPadding=(6, 6, 6, 10),
        backColor=HexColor("#fef2f2"), spaceBefore=6, spaceAfter=6
    )
    styles["table_header"] = ParagraphStyle(
        "th", fontName="NotoSansJP-Bold", fontSize=9.5,
        leading=13, textColor=white, alignment=TA_CENTER
    )
    styles["table_cell"] = ParagraphStyle(
        "tc", fontName="NotoSansJP", fontSize=9.5,
        leading=13, textColor=COLOR_DARK
    )
    styles["table_cell_center"] = ParagraphStyle(
        "tcc", fontName="NotoSansJP", fontSize=9.5,
        leading=13, textColor=COLOR_DARK, alignment=TA_CENTER
    )
    styles["footer"] = ParagraphStyle(
        "footer", fontName="NotoSansJP", fontSize=8,
        leading=11, textColor=HexColor("#9ca3af"), alignment=TA_CENTER
    )
    styles["part_label"] = ParagraphStyle(
        "part_label", fontName="NotoSansJP-Bold", fontSize=12,
        leading=16, textColor=white, alignment=TA_CENTER
    )
    return styles


def escape_html(text):
    """HTMLタグ文字をエスケープ（reportlabのParagraph用）"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def apply_bold(text):
    """**太字**をreportlabの<b>タグに変換"""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return text


def parse_table(lines):
    """Markdownのテーブルをパースして2D配列で返す"""
    rows = []
    for line in lines:
        line = line.strip()
        if line.startswith("|") and not re.match(r'^\|[\s\-:|]+\|$', line):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            rows.append(cells)
    return rows


def build_table(rows, styles):
    """パースしたテーブル行からreportlab Tableを作成"""
    if not rows or len(rows) < 1:
        return None

    header = rows[0]
    data_rows = rows[1:] if len(rows) > 1 else []
    num_cols = len(header)

    # ヘッダー行
    table_data = [[Paragraph(apply_bold(escape_html(c)), styles["table_header"]) for c in header]]

    # データ行
    for row in data_rows:
        while len(row) < num_cols:
            row.append("")
        table_data.append([Paragraph(apply_bold(escape_html(c)), styles["table_cell"]) for c in row[:num_cols]])

    # 列幅の計算（A4幅に収まるように）
    avail_width = A4[0] - 50 * mm
    col_width = avail_width / num_cols

    t = Table(table_data, colWidths=[col_width] * num_cols)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "NotoSansJP-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9.5),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    # ゼブラストライプ
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), COLOR_BG_TABLE))

    t.setStyle(TableStyle(style_cmds))
    return t


def create_part_banner(text, styles):
    """パート見出しのバナーを作成"""
    banner_data = [[Paragraph(text, styles["part_label"])]]
    t = Table(banner_data, colWidths=[A4[0] - 50 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    return t


def md_to_elements(md_path, styles):
    """Markdownファイルを読んでreportlabのFlowable要素リストに変換"""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    elements = []

    # === 表紙 ===
    elements.append(Spacer(1, 60 * mm))
    elements.append(Paragraph("eBay × AI運営", styles["cover_title"]))
    elements.append(Paragraph("ウェビナー資料（草案）", styles["cover_subtitle"]))
    elements.append(Spacer(1, 15 * mm))
    elements.append(Paragraph("2026年4月26日（土）", styles["cover_info"]))
    elements.append(Paragraph("対象：Campersメンバー", styles["cover_info"]))
    elements.append(Paragraph("話者：下元 敬介（株式会社Reffort 代表）", styles["cover_info"]))
    elements.append(Spacer(1, 20 * mm))
    elements.append(Paragraph("※ 草案第2版。【要確認】箇所は社長確認後に修正", styles["cover_info"]))
    elements.append(PageBreak())

    # === 本文パース ===
    i = 0
    in_table = False
    table_lines = []

    while i < len(lines):
        line = lines[i].rstrip("\n")
        stripped = line.strip()

        # 空行
        if not stripped:
            if in_table and table_lines:
                rows = parse_table(table_lines)
                tbl = build_table(rows, styles)
                if tbl:
                    elements.append(tbl)
                    elements.append(Spacer(1, 4 * mm))
                table_lines = []
                in_table = False
            i += 1
            continue

        # テーブル行
        if stripped.startswith("|"):
            in_table = True
            table_lines.append(stripped)
            i += 1
            continue
        elif in_table and table_lines:
            rows = parse_table(table_lines)
            tbl = build_table(rows, styles)
            if tbl:
                elements.append(tbl)
                elements.append(Spacer(1, 4 * mm))
            table_lines = []
            in_table = False

        # メタ行をスキップ
        if stripped.startswith(">") and ("草案" in stripped or "日時" in stripped or "対象" in stripped or "話者" in stripped or "第2版" in stripped or "穴あき" in stripped):
            i += 1
            continue

        # 水平線 → 改ページ（連続---はスキップ）
        if re.match(r'^-{3,}$', stripped):
            # 連続する---はスキップ
            next_i = i + 1
            while next_i < len(lines) and re.match(r'^-{3,}$', lines[next_i].strip()):
                next_i += 1
            # 本文の冒頭あたりの---はスキップ
            if i > 10:
                pass  # ページ区切りとしては使わない（パート見出しで区切る）
            i = next_i
            continue

        # # 見出し
        if stripped.startswith("# "):
            text = stripped[2:].strip()
            # 最初のタイトル行はスキップ（表紙で対応済み）
            if "ウェビナー資料" in text:
                i += 1
                continue
            # 「パートN：」を含む大見出しはページブレーク＋バナー
            if re.match(r'パート\d', text):
                elements.append(PageBreak())
                elements.append(create_part_banner(text, styles))
                elements.append(Spacer(1, 8 * mm))
            else:
                elements.append(PageBreak())
                elements.append(Paragraph(escape_html(text), styles["h1"]))
            i += 1
            continue

        # ## 見出し
        if stripped.startswith("## "):
            text = stripped[3:].strip()
            # 「全体構成」は特別扱いしない
            elements.append(Spacer(1, 4 * mm))
            elements.append(Paragraph(apply_bold(escape_html(text)), styles["h2"]))
            i += 1
            continue

        # ### 見出し
        if stripped.startswith("### "):
            text = stripped[4:].strip()
            elements.append(Spacer(1, 3 * mm))
            elements.append(Paragraph(apply_bold(escape_html(text)), styles["h3"]))
            i += 1
            continue

        # > 引用
        if stripped.startswith("> "):
            text = stripped[2:].strip()
            if "【要確認" in text or "【社長確認" in text:
                elements.append(Paragraph(apply_bold(escape_html(text)), styles["confirm"]))
            else:
                elements.append(Paragraph(apply_bold(escape_html(text)), styles["quote"]))
            i += 1
            continue

        # 【要確認】行
        if "【要確認" in stripped or "【社長確認" in stripped:
            elements.append(Paragraph(apply_bold(escape_html(stripped)), styles["confirm"]))
            i += 1
            continue

        # 箇条書き（- で始まる）
        if re.match(r'^- ', stripped):
            text = stripped[2:].strip()
            elements.append(Paragraph("・ " + apply_bold(escape_html(text)), styles["bullet"]))
            i += 1
            continue

        # サブ箇条書き（  - で始まる）
        if re.match(r'^  - ', stripped):
            text = stripped[4:].strip()
            elements.append(Paragraph("  - " + apply_bold(escape_html(text)), styles["sub_bullet"]))
            i += 1
            continue

        # 数字付きリスト
        m = re.match(r'^(\d+)\. (.+)', stripped)
        if m:
            num = m.group(1)
            text = m.group(2)
            elements.append(Paragraph(f"{num}. " + apply_bold(escape_html(text)), styles["bullet"]))
            i += 1
            continue

        # *で始まるフッター的な行
        if stripped.startswith("*") and stripped.endswith("*"):
            text = stripped.strip("*").strip()
            elements.append(Spacer(1, 4 * mm))
            elements.append(Paragraph(escape_html(text), styles["footer"]))
            i += 1
            continue

        # 通常の本文
        text = stripped
        elements.append(Paragraph(apply_bold(escape_html(text)), styles["body"]))
        i += 1

    # テーブルが残っている場合
    if in_table and table_lines:
        rows = parse_table(table_lines)
        tbl = build_table(rows, styles)
        if tbl:
            elements.append(tbl)

    return elements


def add_page_number(canvas_obj, doc):
    """ページ番号を各ページ下部に追加"""
    page_num = canvas_obj.getPageNumber()
    if page_num == 1:
        return  # 表紙にはページ番号なし
    canvas_obj.saveState()
    canvas_obj.setFont("NotoSansJP", 8)
    canvas_obj.setFillColor(HexColor("#9ca3af"))
    canvas_obj.drawCentredString(A4[0] / 2, 15 * mm, f"— {page_num} —")
    canvas_obj.restoreState()


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    md_path = os.path.join(script_dir, "webinar-draft-20260426.md")
    pdf_path = os.path.join(script_dir, "webinar-draft-20260426.pdf")

    styles = create_styles()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=25 * mm,
        leftMargin=25 * mm,
        rightMargin=25 * mm
    )

    elements = md_to_elements(md_path, styles)

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF作成完了: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    main()
