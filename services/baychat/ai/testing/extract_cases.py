"""
STG DBから「AI Replyが必要なテストケース」を50件抽出するスクリプト
====================================================================
view_chat_ebay（BayChat会話ログ）から (sellerId, buyerEbay) ペアを会話単位にまとめ、
「最新メッセージがバイヤー発信」＝「次はセラーが返信する番」の会話だけを抽出する。

その会話をgpt_request.json 形式（developer商品情報 + system events + user/assistant履歴 +
developer adminプロンプト + 出力フォーマット）に整形して、batch_test.py が消費できる
test_cases/extracted_YYYYMMDD_HHMMSS.json を出力する。

カテゴリ分類（6分類・キーワードベース）:
  - 返品（return/refund keywords）
  - キャンセル（cancel keywords）
  - 追跡（tracking/shipment keywords）
  - 値引き（discount/offer/price keywords）
  - クレーム（damaged/broken/wrong keywords）
  - 一般（上記に該当しないもの）

使い方:
  python extract_cases.py                  # 50件バランス抽出
  python extract_cases.py --limit 100      # 100件に増やす
  python extract_cases.py --per-category 8 # カテゴリあたり8件（合計48件）
"""

import json
import sys
import os
import io
import re
import argparse
import time
from datetime import datetime
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from db_connect import get_tunnel_and_connection
from dotenv import dotenv_values

# ===== 定数 =====
# （旧仕様ではshimomoto本人UIDをハードコードしていたが、複数セラー対応のため
#   動的に msg_row["senderId"] == msg_row["sellerId"] で判定する方針に変更した）
# 会話ケースとして扱う最大メッセージ数（これを超える会話は複雑すぎるためスキップ）
MAX_MESSAGES_PER_CASE = 20

# 出力先フォルダ
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test_cases")

# 標準adminプロンプト（gpt_request_*.jsonの末尾4つのdeveloper blockを流用）
# batch_test.py が差し替えるので、ここでは「ダミー」でもOKだが、テスト実行時の初期状態として
# 社長が現状使っているadminプロンプトv2.3を読み込んでセットする
PROMPT_DIR = os.path.dirname(SCRIPT_DIR)  # services/baychat/ai/


def load_admin_prompt_v23():
    """prompt_admin_v2.3.md から ```...``` で囲まれた本文を取り出す"""
    path = os.path.join(PROMPT_DIR, "prompt_admin_v2.3.md")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"```\n(.*?)```", content, re.DOTALL)
    if not m:
        raise ValueError("prompt_admin_v2.3.md から本文を抽出できませんでした")
    return m.group(1).strip()


def load_base_developer_blocks():
    """
    gpt_request_2.json の末尾3つの developer ブロック（platform compliance / output format /
    admin role prompt）を取り出して流用する。
    adminプロンプトは batch_test.py が差し替えるため、ここでは現状v2.3相当を入れる。
    """
    sample = os.path.join(PROMPT_DIR, "gpt_request_2.json")
    with open(sample, "r", encoding="utf-8") as f:
        data = json.load(f)
    blocks = [m for m in data["input"] if m["role"] == "developer"]
    # 最初は商品情報、残り3つがベースプロンプト群
    base = blocks[1:] if len(blocks) >= 4 else blocks[-3:]
    return base


# ===== カテゴリ分類 =====
CATEGORY_KEYWORDS = {
    # 返品
    "return": [
        r"\breturn(s|ed|ing)?\b", r"\brefund(s|ed|ing)?\b", r"\bsend\s+it\s+back\b",
        r"\brma\b", r"\bship\s+back\b", r"\breturn\s+label\b",
    ],
    # キャンセル（返品より優先）
    "cancel": [
        r"\bcancel(led|lation|ing)?\b", r"\bplaced\s+by\s+mistake\b", r"\bby\s+accident\b",
    ],
    # 追跡
    "tracking": [
        r"\btrack(ing)?\b", r"\bshipment\b", r"\bshipped\b", r"\bwhen\s+will\b",
        r"\bdelivery\b", r"\bdelivered\b", r"\bcustoms\b", r"\bpackage\b",
        r"\barrived?\b", r"\beta\b",
    ],
    # 値引き・オファー
    "discount": [
        r"\bdiscount\b", r"\boffer\b", r"\bnegotia", r"\blower\s+price\b",
        r"\bbest\s+price\b", r"\bdeal\b", r"\bcoupon\b",
    ],
    # クレーム
    "claim": [
        r"\bdamaged?\b", r"\bbroken\b", r"\bwrong\b", r"\bdefect", r"\bscratch",
        r"\btorn\b", r"\bnot\s+as\s+described\b", r"\bfake\b", r"\bcounterfeit\b",
        r"\bmissing\b", r"\bdisappointed\b",
    ],
}

CATEGORY_PRIORITY = ["cancel", "return", "claim", "tracking", "discount", "general"]

# 挨拶のみメッセージ検出用（これに完全一致 or ほぼ一致 で meaningful=False）
GREETING_ONLY_PATTERNS = [
    r"^\s*(thanks?|thank\s*you|thx|ty)[\s.,!]*$",
    r"^\s*(ok|okay|okey|noted|got\s*it|understood)[\s.,!]*$",
    r"^\s*(yes|no|sure|fine|great|cool|nice)[\s.,!]*$",
    r"^\s*(hello|hi|hey)[\s.,!]*$",
    r"^\s*(bye|goodbye|see\s*you)[\s.,!]*$",
    # 「Thanks for the update」系の短い受け答え
    r"^\s*thanks?\s*(for|a lot|so much)?\s*(the\s+(update|info|reply|response|message))?[\s.,!]*$",
    r"^\s*ok[\s.,!]+\s*thanks?\b.{0,30}$",
    r"^\s*thanks?\s*for\s*(your|the)\s*(reply|message|response|info|update|confirmation)[\s.,!]*$",
]


def is_meaningful_buyer_message(text, min_chars=60):
    """
    バイヤーメッセージが「意味のあるテスト対象」か判定。
    条件:
      - 60文字以上（タイムスタンプ等の付随情報を除く本文）
      - 挨拶/感謝/OKだけでない
    """
    if not text:
        return False
    # タイムスタンプ等を除去した実テキスト
    clean = re.sub(r"\[\d{4}-\d{2}-\d{2}T[\d:.]+Z?\]", "", text).strip()
    if len(clean) < min_chars:
        return False
    # 挨拶のみメッセージを排除
    for pat in GREETING_ONLY_PATTERNS:
        if re.match(pat, clean, re.IGNORECASE):
            return False
    return True


def classify(buyer_text, conversation_text):
    """
    バイヤーの最終メッセージ + 会話全体のテキストからカテゴリを判定。
    優先順位: cancel > return > claim > tracking > discount > general
    """
    combined = (buyer_text + "\n" + conversation_text).lower()
    for cat in CATEGORY_PRIORITY:
        if cat == "general":
            continue
        for pat in CATEGORY_KEYWORDS[cat]:
            if re.search(pat, combined, re.IGNORECASE):
                return cat
    return "general"


# ===== 会話グルーピング =====

def fetch_conversation_candidates(conn, since_date="2025-06-01", min_messages=2, max_conversations=5000):
    """
    (sellerId, buyerEbay) 単位で会話候補を取得。
    since_date 以降の会話に絞る（古すぎるデータを避ける）。

    返り値: {(sellerId, buyerEbay): [message_row, ...]}
    """
    cur = conn.cursor()

    # 該当会話のメッセージを全取得
    sql = """
        SELECT id, messages, timeSender, senderId, recipientId, sellerId, buyerEbay,
               buyerFirstName, buyerLastName
        FROM view_chat_ebay
        WHERE timeSender >= %s
          AND buyerEbay IS NOT NULL
          AND buyerEbay != ''
        ORDER BY sellerId, buyerEbay, timeSender ASC
    """
    cur.execute(sql, (since_date,))
    rows = cur.fetchall()

    # (sellerId, buyerEbay) でグループ化
    groups = defaultdict(list)
    for r in rows:
        key = (r["sellerId"], r["buyerEbay"])
        groups[key].append(r)

    # 最低限のメッセージ数に達している会話だけ残す
    groups = {k: v for k, v in groups.items() if len(v) >= min_messages}

    # 件数上限
    if len(groups) > max_conversations:
        # 新しい会話から優先（timeSenderの最大値でソート）
        sorted_items = sorted(
            groups.items(),
            key=lambda kv: kv[1][-1]["timeSender"],
            reverse=True
        )[:max_conversations]
        groups = dict(sorted_items)

    return groups


# ===== メッセージ → OpenAI形式変換 =====

def detect_seller_side_uid(msg_rows):
    """
    1会話ぶんのメッセージ列から、セラー側を表す senderId を特定する。

    BayChatのDB構造:
      - sellerId列はeBayアカウントのUID（会話の属するセラー）
      - senderId列はBayChat上の送信者UID（BayChatユーザー or バイヤー）
      - これらは一致しない

    最も信頼できる手がかり:
      system JSONメッセージ（例:『商品が売れました！』『未着リクエスト』）は
      バイヤー側アクション由来で senderId=buyer_uid, recipientId=seller_side_uid
      になっていることが多い。
      → 最初のsystem JSONの recipientId をセラー側UIDとして採用する。

    フォールバック: system JSONが無い場合、本文に「Best regards」「Thank you for your purchase」
      「Hello {buyerEbay}」等のセラー定型句を含むメッセージの senderId をセラー側UIDとする。
    """
    # 1st priority: system JSONの recipientId
    for r in msg_rows:
        text = (r["messages"] or "").lstrip()
        if text.startswith("{") and r.get("recipientId"):
            return r["recipientId"]

    # 2nd priority: セラー定型句を含むメッセージの senderId
    buyer_ebay = (msg_rows[0].get("buyerEbay") or "").strip().lower()
    seller_signals = ("best regards", "thank you for your purchase",
                      "thank you for purchasing", "wait for delivery",
                      "thank you for contacting us", "thank you for your message")
    for r in msg_rows:
        text = (r["messages"] or "").lower()
        if not text or text.lstrip().startswith("{"):
            continue
        # セラー定型句マッチ
        if any(sig in text for sig in seller_signals):
            if r.get("senderId"):
                return r["senderId"]
        # Hello {buyer_ebay}で始まる → セラー定型自動メッセージ
        if buyer_ebay and text.lstrip().startswith(f"hello {buyer_ebay}"):
            if r.get("senderId"):
                return r["senderId"]
    return None


def classify_message_role(msg_row, seller_side_uid=None):
    """
    メッセージ行 + あらかじめ特定したセラー側UIDから OpenAI role を判定。
    - messages.startswith('{') → system
    - senderId == seller_side_uid → assistant (セラー発信)
    - その他 → user (バイヤー発信)

    注意: 旧仕様ではSELLER_UIDハードコード、または sellerId列との比較だったが、
         BayChatのDB構造上 sellerId != senderId のため機能していなかった。
         会話単位で seller_side_uid を特定する方式に改めた（2026-04-15 修正）。
    """
    text = (msg_row["messages"] or "").lstrip()
    if text.startswith("{"):
        return "system"
    if seller_side_uid and msg_row.get("senderId") == seller_side_uid:
        return "assistant"
    return "user"


def format_message_content(msg_row, role):
    """
    メッセージ本文をgpt_request形式（タイムスタンプ付き）に整形。
    - system: "event: [ISO] event_name" 形式にできれば整形、無理ならそのまま
    - user/assistant: "[ISO] body" 形式
    """
    ts = msg_row["timeSender"]
    iso = ts.strftime("%Y-%m-%dT%H:%M:%S.000Z") if ts else ""

    raw = msg_row["messages"] or ""

    if role == "system":
        # JSONから type / content を抽出してイベント名にする（失敗したら生で返す）
        try:
            data = json.loads(raw)
            event_type = data.get("type") or data.get("content", "")[:60] or "system_event"
            # 改行や余計な空白を削る
            event_label = re.sub(r"\s+", " ", event_type).strip()
            return f"event: [{iso}] {event_label}"
        except Exception:
            return f"event: [{iso}] system_message"
    else:
        # 改行は残してOK（gpt_request_2.json も改行ありのまま）
        return f"[{iso}] {raw.strip()}"


def extract_order_info_from_system(msg_rows):
    """
    system JSONメッセージ群から商品情報を最初に出現したものから抽出する。
    成功時: 商品情報dict (タイトル・SKU・orderID等)
    失敗時: None
    """
    for r in msg_rows:
        text = (r["messages"] or "").lstrip()
        if not text.startswith("{"):
            continue
        try:
            data = json.loads(text)
            content = data.get("content", "")
            # content内の日本語通知から商品名・SKU・orderIDを正規表現で抽出
            order_match = re.search(r"Order number id[:：]\s*([\w\-]+)", content)
            sku_match = re.search(r"SKU[:：]\s*([\w\-\.]+)", content)
            # タイトルは最初の行（「商品が売れました！」の次の行）
            title_match = re.search(r"商品が売れました[！!]\s*\n\s*([^\n]+)", content)
            # 価格
            price_match = re.search(r"([\d.]+)\s*\(\s*\+\s*送料", content)
            if order_match or sku_match or title_match:
                return {
                    "orderID": order_match.group(1) if order_match else None,
                    "SKU": sku_match.group(1) if sku_match else None,
                    "Title": title_match.group(1).strip() if title_match else None,
                    "Price": price_match.group(1) if price_match else None,
                }
        except Exception:
            continue
    return None


def build_product_info_block(msg_rows, order_info):
    """
    商品情報JSONのdeveloperブロックを構築する。
    DB上に商品詳細テーブルがないため、system JSONから抽出した情報 + 汎用情報で構築。
    実際のeBay APIからの詳細情報は取得できないので、シンプルな構造で出す。
    """
    info = {
        "Title": (order_info or {}).get("Title") or "商品情報（要取得）",
        "SKU": (order_info or {}).get("SKU"),
        "orderID": (order_info or {}).get("orderID"),
        "CurrentPrice": (order_info or {}).get("Price"),
        "Currency": "USD",
        "Country": "JP",
    }
    # Noneを除く
    info = {k: v for k, v in info.items() if v is not None}
    return json.dumps(info, ensure_ascii=False)


def build_test_case(conv_key, msg_rows, base_dev_blocks):
    """
    1会話分のメッセージ列から gpt_request.json 形式の1テストケースを構築する。

    構造:
      [0]        developer: 商品情報JSON
      [1..k]     system:    event ログ（sold / cancel_request など）
      [k+1..n]   user/assistant: 会話履歴（時系列）
      [n+1..]    developer: ベース3ブロック（platform / output format / admin prompt）

    返り値: { id, category, buyer_message, messages: [...] } または None（スキップ対象）
    """
    sellerId, buyerEbay = conv_key

    # まずこの会話のセラー側UIDを特定する
    seller_side_uid = detect_seller_side_uid(msg_rows)

    # ロール判定（特定したセラー側UIDを使う）
    classified = []
    for r in msg_rows:
        role = classify_message_role(r, seller_side_uid=seller_side_uid)
        content = format_message_content(r, role)
        classified.append({"role": role, "content": content, "_raw": r})

    # 最後のメッセージがバイヤー（user）でない場合はスキップ
    non_system = [m for m in classified if m["role"] != "system"]
    if not non_system:
        return None
    if non_system[-1]["role"] != "user":
        return None

    # 本当にアシスタント（セラー）が過去に返信したことがあるか確認
    has_assistant = any(m["role"] == "assistant" for m in classified)
    # STAGE 1（初回応答）もテストに含めたいので、has_assistant=False も許容

    # 最終buyerメッセージ本文（タイムスタンプを除いたテキスト）
    last_buyer_raw = non_system[-1]["_raw"]["messages"] or ""
    # 会話全体テキスト（カテゴリ分類用）
    conv_text = "\n".join(
        (m["_raw"]["messages"] or "")
        for m in classified if m["role"] in ("user", "assistant")
    )

    # カテゴリ分類
    category = classify(last_buyer_raw, conv_text)

    # 商品情報抽出
    order_info = extract_order_info_from_system(msg_rows)
    product_json = build_product_info_block(msg_rows, order_info)

    # セラーID（文字列）を取得。動的置換に使うバイヤー名もここで作る
    # sellerId は UID なので使えず、会話中のセラー名は取れない（DB仕様）。
    # ただしCowatechのテンプレートに vipuv_81 / rioxxrinaxjapan がハードコードされているので、
    # せめて buyer_name をそのケースの buyer_ebay に置換することで、AIが誤ったバイヤー名を
    # 返信に使うリスクを下げる。
    buyer_name_for_prompt = buyerEbay or "buyer"
    seller_name_for_prompt = "seller"  # DBからは取得できないため汎用プレースホルダ

    # メッセージ配列を組み立て
    messages = []
    # [0] 商品情報
    messages.append({"role": "developer", "content": product_json})
    # [1..] system events（JSONメッセージ）
    for m in classified:
        if m["role"] == "system":
            messages.append({"role": "system", "content": m["content"]})
    # [k+1..] user/assistant 履歴
    for m in classified:
        if m["role"] in ("user", "assistant"):
            messages.append({"role": m["role"], "content": m["content"]})
    # [n+1..] ベースdeveloperブロック（vipuv_81 等のハードコード値を動的置換）
    for block in base_dev_blocks:
        content = block["content"]
        # Cowatechテンプレートの既知ハードコードを置換
        content = content.replace("vipuv_81", buyer_name_for_prompt)
        content = content.replace("rioxxrinaxjapan", seller_name_for_prompt)
        messages.append({"role": "developer", "content": content})

    # バイヤー最終メッセージ（タイムスタンプ除去）
    buyer_message_clean = last_buyer_raw.strip()

    return {
        "id": f"{buyerEbay}_{msg_rows[-1]['id'][:8]}",
        "category": category,
        "buyer_ebay": buyerEbay,
        "seller_account": sellerId,
        "buyer_message": buyer_message_clean,
        "num_messages": len(msg_rows),
        "has_seller_history": has_assistant,
        "messages": messages,
    }


# ===== バランス抽出 =====

def balance_by_category(cases, per_category_target):
    """
    カテゴリごとに per_category_target 件までバランス抽出する。
    返り値: フィルタされたcaseリスト
    """
    by_cat = defaultdict(list)
    for c in cases:
        by_cat[c["category"]].append(c)

    selected = []
    for cat in CATEGORY_PRIORITY:
        pool = by_cat.get(cat, [])
        # 新しい会話を優先（messages数が多い方が情報量が多いので若干優先）
        pool.sort(key=lambda c: (-c["num_messages"], c["id"]))
        selected.extend(pool[:per_category_target])

    # カテゴリあたり足りない場合は generalから補充
    total_target = per_category_target * len(CATEGORY_PRIORITY)
    if len(selected) < total_target:
        remaining = []
        used_ids = {c["id"] for c in selected}
        for cat in CATEGORY_PRIORITY:
            for c in by_cat.get(cat, []):
                if c["id"] not in used_ids:
                    remaining.append(c)
        remaining.sort(key=lambda c: -c["num_messages"])
        selected.extend(remaining[: total_target - len(selected)])

    return selected


# ===== メイン =====

def translate_to_japanese(texts, batch_size=10):
    """
    英語のバイヤーメッセージリストを日本語に一括翻訳する（GPT-4.1-Mini使用）。
    texts: [str, ...]
    返り値: [ja_str, ...] 同じ長さのリスト
    """
    env = dotenv_values(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
    api_key = env.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY未設定。翻訳をスキップ")
        return [""] * len(texts)

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        # 番号付きJSON形式で翻訳させる
        numbered = "\n\n".join(f"[{j+1}] {t}" for j, t in enumerate(batch))
        prompt = f"""以下の英語メッセージを1件ずつ自然な日本語に翻訳してください。
出力は必ず次のJSON形式で、各翻訳を番号順に配列で返してください：
{{"translations": ["翻訳1", "翻訳2", ...]}}

英語メッセージ:
{numbered}"""

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            trans = data.get("translations", [])
            if len(trans) != len(batch):
                # 長さが合わない場合、パディング
                trans = (trans + [""] * len(batch))[:len(batch)]
            results.extend(trans)
            print(f"  翻訳 {i+len(batch)}/{len(texts)} 完了")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ バッチ {i} 翻訳失敗: {e}")
            results.extend([""] * len(batch))

    return results


def main(args):
    print("=== BayChat STGからテストケース抽出 ===")
    print(f"最低メッセージ数: {args.min_messages}")
    print(f"取得対象日付: {args.since} 以降")
    print(f"カテゴリあたり上限: {args.per_category}")
    print(f"意味あるケースのみ: {args.only_meaningful} (最低{args.min_chars}文字)")
    print(f"日本語訳を追加: {args.translate}")
    print()

    base_dev_blocks = load_base_developer_blocks()
    print(f"ベースdeveloperブロック: {len(base_dev_blocks)}個")

    with get_tunnel_and_connection(database="ebay_stg") as (tunnel, conn):
        print("DBに接続しました。会話候補を取得中...")
        groups = fetch_conversation_candidates(
            conn,
            since_date=args.since,
            min_messages=args.min_messages,
            max_conversations=args.pool_size,
        )
        print(f"会話候補: {len(groups)}件（(sellerId, buyerEbay)ペア単位）")

    # テストケースに変換
    cases = []
    skipped_reasons = defaultdict(int)
    for key, rows in groups.items():
        # メッセージ数が多すぎる会話（例: 35件超の多言語ごちゃ混ぜケース）はスキップ
        if len(rows) > args.max_messages:
            skipped_reasons[f"メッセージ数が{args.max_messages}件超"] += 1
            continue
        case = build_test_case(key, rows, base_dev_blocks)
        if case is None:
            skipped_reasons["最終メッセージが非buyer"] += 1
            continue
        # 意味あるケースフィルタ
        if args.only_meaningful:
            if not is_meaningful_buyer_message(case["buyer_message"], min_chars=args.min_chars):
                skipped_reasons["短い挨拶等のバイヤーメッセージ"] += 1
                continue
        cases.append(case)

    print(f"変換成功: {len(cases)}件 / スキップ: {dict(skipped_reasons)}")

    # カテゴリ分布
    cat_dist = defaultdict(int)
    for c in cases:
        cat_dist[c["category"]] += 1
    print("\n【カテゴリ分布（変換後）】")
    for cat in CATEGORY_PRIORITY:
        print(f"  {cat:10s}: {cat_dist[cat]:>5d}件")

    # バランス抽出
    selected = balance_by_category(cases, args.per_category)
    print(f"\n選抜結果: {len(selected)}件")
    sel_dist = defaultdict(int)
    for c in selected:
        sel_dist[c["category"]] += 1
    for cat in CATEGORY_PRIORITY:
        print(f"  {cat:10s}: {sel_dist[cat]:>3d}件")

    # 日本語訳を生成（バイヤー最終メッセージ）
    translations = [""] * len(selected)
    if args.translate and selected:
        print(f"\n【日本語翻訳】 バイヤー最終メッセージ{len(selected)}件をGPT-4.1-Miniで翻訳中...")
        translations = translate_to_japanese([c["buyer_message"] for c in selected])

    # 会話履歴全体の日本語翻訳（user/assistantメッセージ単位で翻訳）
    history_translations = [[] for _ in selected]
    if args.translate_history and selected:
        # 全メッセージをフラットにして一括翻訳し、後で分割して返す
        flat_texts = []
        index_map = []  # (case_idx, msg_idx_in_case) のリスト
        per_case_texts = []
        for ci, c in enumerate(selected):
            case_msgs = []
            for mi, m in enumerate(c["messages"]):
                if m["role"] in ("user", "assistant"):
                    # タイムスタンプ除去
                    raw = re.sub(r"^\[[^\]]+\]\s*", "", m["content"])
                    case_msgs.append(raw)
                    index_map.append((ci, len(case_msgs) - 1))
                    flat_texts.append(raw)
            per_case_texts.append(case_msgs)
            history_translations[ci] = [""] * len(case_msgs)

        if flat_texts:
            print(f"\n【履歴日本語翻訳】 合計{len(flat_texts)}メッセージをGPT-4.1-Miniで翻訳中...")
            ja_flat = translate_to_japanese(flat_texts, batch_size=15)
            for (ci, local_mi), ja in zip(index_map, ja_flat):
                history_translations[ci][local_mi] = ja

    # 出力
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = os.path.join(OUTPUT_DIR, f"extracted_{timestamp}.json")

    # batch_test.py が消費する形式（リスト、各要素に input キー）
    output = [{
        "id": c["id"],
        "category": c["category"],
        "buyer_ebay": c["buyer_ebay"],
        "buyer_message": c["buyer_message"],
        "buyer_message_ja": translations[i] if i < len(translations) else "",
        "history_ja": history_translations[i] if i < len(history_translations) else [],
        "num_messages": c["num_messages"],
        "has_seller_history": c["has_seller_history"],
        "input": c["messages"],
    } for i, c in enumerate(selected)]

    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n保存完了: {outpath}")
    print(f"ファイルサイズ: {os.path.getsize(outpath) / 1024:.1f} KB")

    return outpath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BayChat STG DBからAI Replyテストケースを抽出")
    parser.add_argument("--per-category", type=int, default=9,
                        help="カテゴリあたりの抽出件数（デフォルト:9 → 6カテゴリ×9 = 54件前後）")
    parser.add_argument("--min-messages", type=int, default=2,
                        help="会話ペアに必要な最低メッセージ数（デフォルト:2）")
    parser.add_argument("--since", type=str, default="2025-06-01",
                        help="この日付以降の会話を対象にする（デフォルト:2025-06-01）")
    parser.add_argument("--pool-size", type=int, default=5000,
                        help="DBから取得する会話ペア数の上限（デフォルト:5000）")
    parser.add_argument("--only-meaningful", action="store_true",
                        help="挨拶・短いメッセージを除外して意味あるケースのみ抽出")
    parser.add_argument("--min-chars", type=int, default=60,
                        help="--only-meaningful時の最低文字数（デフォルト:60）")
    parser.add_argument("--translate", action="store_true",
                        help="バイヤー最終メッセージを日本語に翻訳して buyer_message_ja に入れる")
    parser.add_argument("--translate-history", action="store_true",
                        help="会話履歴（user/assistant全メッセージ）も日本語翻訳して history_ja に入れる")
    parser.add_argument("--max-messages", type=int, default=20,
                        help="1会話あたりの最大メッセージ数。これを超える会話はスキップ（デフォルト:20）")

    args = parser.parse_args()
    main(args)
