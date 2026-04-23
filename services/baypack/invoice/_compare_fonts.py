"""2つのPDFの埋め込みフォントを比較"""
import sys
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

def list_fonts(pdf_path, label):
    print(f"\n=== {label} ===")
    print(f"Path: {pdf_path}")
    try:
        r = PdfReader(pdf_path)
        print(f"Pages: {len(r.pages)}")
        all_fonts = set()
        for i, page in enumerate(r.pages):
            if '/Resources' in page and '/Font' in page['/Resources']:
                fonts = page['/Resources']['/Font']
                for key, ref in fonts.items():
                    try:
                        f = ref.get_object()
                        base = f.get('/BaseFont', 'N/A')
                        enc = f.get('/Encoding', 'N/A')
                        subtype = f.get('/Subtype', 'N/A')
                        all_fonts.add((str(base), str(subtype)))
                    except Exception as e:
                        pass
        for font, subtype in sorted(all_fonts):
            print(f"  {font}  [{subtype}]")
    except Exception as e:
        print(f"ERROR: {e}")

REF = r"C:\Users\KEISUKE SHIMOMOTO\OneDrive - 株式会社リフォート\01.Reffort\BayPack\請求書\自社\共同運営費\2026\【BayPack】共同運営費_請求書（2602）.pdf"
MINE = r"C:\Users\KEISUKE SHIMOMOTO\Desktop\請求書\_test_A_minimal_【BayPack】共同運営費_請求書（2603）.pdf"
ORIG = r"C:\Users\KEISUKE SHIMOMOTO\Desktop\請求書\【BayPack】共同運営費_請求書（2603）.pdf"

list_fonts(REF, "社長が手動で作った 2602（参照）")
list_fonts(ORIG, "初回生成の 2603（パラメータ多め）")
list_fonts(MINE, "最小パラメータ版 2603")
