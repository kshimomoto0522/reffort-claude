"""
商品マッチング層

【役割】
1. eBay 商品タイトルから「日本サイトで検索すべきキーワード」を生成する
2. 楽天/Yahoo 検索結果と eBay 商品の「同一商品らしさ」をスコアリングする
3. 型番・GTIN・ブランド一致を加点する

【設計】
Ver.1 は外部 LLM API なしで動く（regex + 文字列類似度）。
Ver.2 で Claude API による semantic matching を追加。

【マッチング段階】
- 段階 1: GTIN（JAN）一致 → 100 点満点
- 段階 2: 型番（DD9682-100 等）一致 → 90 点
- 段階 3: ブランド + モデル名 + キーワード共通数 → 0-80 点
"""

import re
from difflib import SequenceMatcher

# 型番パターン（広めに用意）
# - スニーカー: ABC1234-100 / DD9682-100 / DZ4458-100 / FQ8250-200
# - カメラ: ILCE-7CM2, EOS R5, Z 7II
# - 楽器: GT-1000, MX25, X32
MODEL_CODE_PATTERNS = [
    re.compile(r'\b([A-Z]{2,4}\d{3,5}-\d{3,4})\b'),     # Nike 風（DZ4458-100, DD1391-100）
    re.compile(r'\b([A-Z]\d{4,6}-[A-Z\d]{3,4})\b'),     # Mizuno 風（A12345-AB1）
    re.compile(r'\b(\d{4}[A-Z]\d{3})\b'),                # Onitsuka 風（1183C102, 1183A360）
    re.compile(r'\b(ILCE-[A-Z0-9]+)\b'),                 # Sony α
    re.compile(r'\b(α\s*\d+[A-Z]*)\b'),                  # Sony α7C
    re.compile(r'\b(EOS\s*[A-Z]?\d+[A-Z]?)\b'),          # Canon EOS
    re.compile(r'\b(Z\s*\d{1,2}[A-Z]{0,2})\b'),          # Nikon Z
    re.compile(r'\b(GP-?\d+)\b'),                        # Tamiya GP-424
    re.compile(r'\b(GP\.?\d+)\b'),                       # Tamiya GP.424
    re.compile(r'\b([A-Z]{2,4}-?\d{3,5})\b'),            # 一般型番
]

# JAN/UPC（13桁/12桁の数字）
GTIN_RE = re.compile(r'\b(\d{12,14})\b')

# ブランドリスト（タイトルから抽出 → 検索ヒント生成）
KNOWN_BRANDS = [
    'nike', 'jordan', 'air jordan', 'adidas', 'new balance', 'asics',
    'onitsuka', 'onitsuka tiger', 'reebok', 'puma', 'converse', 'vans',
    'mizuno', 'yonex', 'shimano', 'daiwa', 'snap-on', 'tamiya',
    'sony', 'canon', 'nikon', 'fujifilm', 'leica', 'olympus', 'panasonic',
    'casio', 'seiko', 'grand seiko', 'citizen',
    'pokemon', 'bandai', 'tamashii', 'good smile', 'kotobukiya',
    'lego', 'gundam', 'yamaha', 'roland', 'boss', 'korg', 'fender', 'gibson',
]

# 検索キーワード生成時に「日本検索で必ず付けたい和訳ペア」
EN_TO_JP_HINTS = {
    'onitsuka tiger': 'オニツカタイガー',
    'mexico 66': 'メキシコ66',
    'mini 4wd': 'ミニ四駆',
    'pokemon': 'ポケモン',
    'gunpla': 'ガンプラ',
    'gundam': 'ガンダム',
    'figure': 'フィギュア',
}

# 不要な装飾語（検索キーワードから除外）
STOPWORDS = set([
    'new', 'used', 'mens', 'womens', "men's", "women's", 'men', 'women',
    'size', 'us', 'uk', 'eu', 'jp', 'pair', 'pcs', 'piece', 'in box',
    'with', 'box', 'shoes', 'sneaker', 'sneakers', 'shoe',
    'genuine', 'authentic', 'original', 'brand new', 'limited',
    'fast shipping', 'free shipping', 'ship', 'from', 'japan',
    'rare', 'vintage', 'retro', 'sealed', 'unopened',
    'the', 'a', 'and', 'or', 'of', 'for', 'to',
])

WORD_RE = re.compile(r"[A-Za-z0-9\-']+")


def extract_gtin(text: str) -> str | None:
    """13桁のJAN/UPC/EANらしき数字列を抽出（誤検知あり・参考程度）。"""
    m = GTIN_RE.search(text or '')
    if not m:
        return None
    code = m.group(1)
    # チェックディジット検算は省略（誤マッチを許容しつつ後段で確認）
    if len(code) not in (12, 13, 14):
        return None
    return code


def extract_model_code(title: str) -> str | None:
    """タイトルから型番を抽出（最初にマッチしたもの）。"""
    if not title:
        return None
    for pat in MODEL_CODE_PATTERNS:
        m = pat.search(title)
        if m:
            return m.group(1).strip()
    return None


def extract_brand(title: str) -> str | None:
    """タイトルからブランド名（既知リスト）を抽出。"""
    lower = (title or '').lower()
    for b in KNOWN_BRANDS:
        if b in lower:
            return b
    return None


def build_search_keyword(ebay_title: str, max_words: int = 5) -> str:
    """
    eBay 英語タイトルから日本側検索キーワードを構築する。
    優先度: 型番 > ブランド + 主要トークン + 和訳ヒント
    """
    if not ebay_title:
        return ''
    title = ebay_title.strip()
    title_lower = title.lower()

    # 1) 型番が取れた場合 → ブランド + 型番（最強）
    code = extract_model_code(title)
    if code:
        brand = extract_brand(title)
        if brand:
            return f'{brand} {code}'
        return code

    # 2) 型番なし → ブランド + 主要トークン + 和訳
    brand = extract_brand(title) or ''
    tokens = WORD_RE.findall(title)
    cleaned: list[str] = []
    for t in tokens:
        low = t.lower()
        if low in STOPWORDS:
            continue
        if low == brand:
            continue
        if len(low) <= 1:
            continue
        cleaned.append(t)
        if len(cleaned) >= max_words:
            break
    parts: list[str] = []
    if brand:
        parts.append(brand)
    parts.extend(cleaned[:max_words])

    # 3) EN→JP の和訳ヒントがあれば付加（検索ヒット率向上）
    for en, jp in EN_TO_JP_HINTS.items():
        if en in title_lower:
            parts.append(jp)
            break

    return ' '.join(parts).strip()


def title_similarity(a: str, b: str) -> float:
    """正規化したタイトル同士の類似度（0.0-1.0）。"""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, _normalize_for_match(a), _normalize_for_match(b)).ratio()


def _normalize_for_match(text: str) -> str:
    text = (text or '').lower()
    # 全角→半角に変換
    text = text.replace('ナイキ', 'nike').replace('ジョーダン', 'jordan')
    text = text.replace('アディダス', 'adidas').replace('ニューバランス', 'new balance')
    text = text.replace('ソニー', 'sony').replace('キヤノン', 'canon')
    # 英数だけに絞る
    text = re.sub(r'[^a-z0-9]+', ' ', text).strip()
    return text


def match_score(ebay_title: str, supplier_item: dict) -> float:
    """
    eBay タイトルと仕入候補（rakuten/yahoo の正規化後 dict）の一致度を 0-100 で返す。
    """
    base = 0.0
    sup_name = supplier_item.get('name') or ''

    ebay_code = extract_model_code(ebay_title)
    sup_code = extract_model_code(sup_name)

    # 型番一致（強）
    if ebay_code and sup_code and ebay_code.upper() == sup_code.upper():
        base += 70.0

    # JAN/UPC 一致（型番より弱め: GTIN 抽出は誤検知が多い）
    ebay_gtin = extract_gtin(ebay_title)
    sup_jan = supplier_item.get('jan')
    if ebay_gtin and sup_jan and ebay_gtin == sup_jan:
        base += 60.0

    # ブランド一致
    e_brand = extract_brand(ebay_title)
    s_brand = extract_brand(sup_name)
    if e_brand and s_brand and e_brand == s_brand:
        base += 10.0

    # タイトル類似度（残りで底上げ・最大 30 点）
    sim = title_similarity(ebay_title, sup_name)
    base += sim * 30.0

    return min(100.0, base)


def best_supplier_match(ebay_title: str, candidates: list[dict], min_score: float = 35.0) -> dict | None:
    """
    候補の中で最も一致度が高いものを返す（min_score 未満は不採用）。
    """
    if not candidates:
        return None
    scored = sorted(
        ((match_score(ebay_title, c), c) for c in candidates),
        key=lambda x: -x[0],
    )
    if scored and scored[0][0] >= min_score:
        item = dict(scored[0][1])
        item['match_score'] = round(scored[0][0], 1)
        return item
    return None


if __name__ == '__main__':
    # 動作確認
    title_jp = '【期間限定プライス】NIKE DUNK LOW RETRO PANDA BLACK WHITE DD1391-100'
    title_en = "Nike Dunk Low Retro 'Panda' DD1391-100 Men's New In Box"
    print(f'EN title    : {title_en}')
    print(f'JP supplier : {title_jp}')
    print(f'extract_model_code(EN) = {extract_model_code(title_en)}')
    print(f'extract_model_code(JP) = {extract_model_code(title_jp)}')
    print(f'extract_brand(EN)      = {extract_brand(title_en)}')
    print(f'build_search_keyword   = {build_search_keyword(title_en)}')
    fake_supplier = {'name': title_jp, 'jan': None}
    print(f'match_score            = {match_score(title_en, fake_supplier):.1f}')

    # 別商品（不一致）
    diff_supplier = {'name': '靴紐 100cm シューレース', 'jan': None}
    print(f'match_score (diff)     = {match_score(title_en, diff_supplier):.1f}')
