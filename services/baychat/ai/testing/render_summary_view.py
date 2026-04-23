"""
要約モードのAI出力JSONをセラー画面相当のHTMLカードに変換するレンダラー
====================================================================
BayChatのブランドカラー（紫ベース）に合わせた配色。
バイヤーメッセージ・返信文は英語＋日本語訳の両方を表示する。

使い方:
    from render_summary_view import render_summary_to_html
    html = render_summary_to_html(
        data=json_dict,
        buyer_message_en="...",
        buyer_message_ja="...",
        attached_images=["url1", "url2"],
    )
"""

import json
import html as html_lib


# ============================================================
# BayChat ブランドカラー（紫ベース）
# ============================================================
COLOR_PRIMARY = "#7c3aed"       # メイン紫
COLOR_PRIMARY_DARK = "#5b21b6"  # 濃紫
COLOR_PRIMARY_LIGHT = "#a78bfa" # 薄紫
COLOR_PRIMARY_BG = "#f5f3ff"    # 極薄紫（背景用）
COLOR_PRIMARY_BG2 = "#ede9fe"   # 薄紫背景
COLOR_TEXT = "#1f2937"
COLOR_TEXT_SUB = "#6b7280"
COLOR_BORDER = "#e5e7eb"
COLOR_BORDER_STRONG = "#d4d4d8"


def _escape(text):
    if text is None:
        return ""
    return html_lib.escape(str(text))


def _render_stars(score, max_score=5):
    try:
        score = int(score)
    except (ValueError, TypeError):
        score = 0
    filled = "★" * score
    empty = "☆" * (max_score - score)
    return f'<span class="stars">{filled}{empty}</span>'


def _complexity_badge(level):
    """複雑度バッジ（紫濃淡のみで表現）"""
    mapping = {
        "low": ("シンプル", COLOR_PRIMARY_LIGHT),
        "medium": ("やや複雑", COLOR_PRIMARY),
        "high": ("複雑", COLOR_PRIMARY_DARK),
    }
    label, color = mapping.get(level, (level or "不明", COLOR_TEXT_SUB))
    return f'<span class="complexity-badge" style="background:{color}">{label}</span>'


def _render_list(value):
    if not value:
        return '<span class="empty">—</span>'
    if isinstance(value, list):
        items = "".join(f"<li>{_escape(item)}</li>" for item in value)
        return f"<ul>{items}</ul>"
    return _escape(value)


def _render_images(images):
    """添付画像のプレビュー枠"""
    if not images:
        return ""
    imgs_html = ""
    for i, src in enumerate(images):
        if src.startswith("http") or src.startswith("data:"):
            imgs_html += f'<a href="{_escape(src)}" target="_blank"><img src="{_escape(src)}" alt="添付{i+1}" /></a>'
        else:
            # プレースホルダ
            imgs_html += f'<div class="img-placeholder">📷 添付画像 {i+1}<br><small>{_escape(src)}</small></div>'
    return f"""
    <div class="attachments">
        <div class="attachments-label">📎 添付画像（{len(images)}枚）</div>
        <div class="attachments-grid">{imgs_html}</div>
    </div>
    """


def render_summary_to_html(
    data,
    buyer_message_en="",
    buyer_message_ja="",
    attached_images=None,
    model_name="",
    elapsed=0,
    cost_jpy=0,
    seller_reply_en="",
    seller_reply_ja="",
):
    """
    AI出力JSONをセラー画面風のHTMLに変換

    Args:
        data: AI出力dict
        buyer_message_en: バイヤーメッセージ（英語）
        buyer_message_ja: バイヤーメッセージ（日本語訳）
        attached_images: 添付画像URLまたはプレースホルダ文字列のリスト
        model_name, elapsed, cost_jpy: テスト用メタ情報
        seller_reply_en, seller_reply_ja: Call-2で生成した返信（あれば末尾に表示）
    """
    attached_images = attached_images or []
    summary = data.get("summary", {}) or {}
    complexity = data.get("complexityLevel", "")
    patterns = data.get("patterns", []) or []
    recommended = data.get("recommendedPattern", "")
    decision = data.get("sellerDecisionNeeded", "")
    emotion = summary.get("buyerEmotion", "")

    # パターンカード
    pattern_cards_html = ""
    for p in patterns:
        pid = p.get("id", "")
        name = p.get("name", "")
        desc = p.get("description", "")
        merits = p.get("merits", []) or []
        demerits = p.get("demerits", []) or []
        rec = p.get("recommendation", 0)
        rec_reason = p.get("recommendationReason", "")
        is_recommended = (pid == recommended)

        merits_html = "".join(f"<li>◎ {_escape(m)}</li>" for m in merits)
        demerits_html = "".join(f"<li>△ {_escape(d)}</li>" for d in demerits)

        recommended_badge = '<span class="rec-badge">推奨</span>' if is_recommended else ""

        pattern_cards_html += f"""
        <div class="pattern-card {'recommended' if is_recommended else ''}">
            <div class="pattern-header">
                <span class="pattern-id">パターン{_escape(pid)}</span>
                {recommended_badge}
                {_render_stars(rec)}
            </div>
            <h3 class="pattern-name">{_escape(name)}</h3>
            <p class="pattern-desc">{_escape(desc)}</p>
            <div class="pros-cons">
                <div class="pros-cons-col">
                    <div class="pros-cons-label">メリット</div>
                    <ul>{merits_html}</ul>
                </div>
                <div class="pros-cons-col">
                    <div class="pros-cons-label">デメリット</div>
                    <ul>{demerits_html}</ul>
                </div>
            </div>
            <div class="rec-reason">{_escape(rec_reason)}</div>
            <button class="select-btn">このパターンで返信文を生成</button>
        </div>
        """

    # メタ情報
    meta_html = ""
    if model_name or elapsed or cost_jpy:
        meta_parts = []
        if model_name:
            meta_parts.append(f'<span class="meta-item">🤖 {_escape(model_name)}</span>')
        if elapsed:
            meta_parts.append(f'<span class="meta-item">⏱️ {elapsed:.1f}秒</span>')
        if cost_jpy:
            meta_parts.append(f'<span class="meta-item">💴 ¥{cost_jpy:.3f}</span>')
        meta_html = f'<div class="meta-bar">{"".join(meta_parts)}</div>'

    # バイヤーメッセージ（英日併記）
    buyer_html = ""
    if buyer_message_en or buyer_message_ja:
        buyer_html = f"""
        <div class="message-card buyer">
            <div class="message-header">📩 バイヤーからのメッセージ</div>
            <div class="bilingual">
                <div class="lang-block">
                    <div class="lang-label">🇺🇸 English</div>
                    <div class="lang-body">{_escape(buyer_message_en) or '—'}</div>
                </div>
                <div class="lang-block">
                    <div class="lang-label">🇯🇵 日本語訳</div>
                    <div class="lang-body">{_escape(buyer_message_ja) or '—'}</div>
                </div>
            </div>
            {_render_images(attached_images)}
        </div>
        """

    # セラー返信（Call-2で生成した場合のみ）
    reply_html = ""
    if seller_reply_en or seller_reply_ja:
        reply_html = f"""
        <div class="message-card seller">
            <div class="message-header">✉️ AI生成返信文</div>
            <div class="bilingual">
                <div class="lang-block">
                    <div class="lang-label">🇺🇸 English</div>
                    <div class="lang-body">{_escape(seller_reply_en) or '—'}</div>
                </div>
                <div class="lang-block">
                    <div class="lang-label">🇯🇵 日本語訳</div>
                    <div class="lang-body">{_escape(seller_reply_ja) or '—'}</div>
                </div>
            </div>
        </div>
        """

    html_doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>要約モード プレビュー</title>
<style>
* {{ box-sizing: border-box; }}
body {{
    font-family: -apple-system, 'Segoe UI', 'Yu Gothic UI', sans-serif;
    max-width: 960px;
    margin: 30px auto;
    padding: 0 20px;
    background: #fafafa;
    color: {COLOR_TEXT};
    line-height: 1.6;
}}

.meta-bar {{
    background: {COLOR_PRIMARY_DARK};
    color: #f5f3ff;
    padding: 8px 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    display: flex;
    gap: 20px;
    font-size: 0.85em;
}}

.message-card {{
    background: #fff;
    border-left: 4px solid {COLOR_PRIMARY};
    padding: 16px 20px;
    border-radius: 6px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
.message-card.seller {{ border-left-color: {COLOR_PRIMARY_LIGHT}; }}
.message-header {{
    font-weight: bold;
    color: {COLOR_PRIMARY_DARK};
    margin-bottom: 12px;
    font-size: 0.95em;
}}
.bilingual {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}}
.lang-block {{
    background: {COLOR_PRIMARY_BG};
    padding: 10px 14px;
    border-radius: 6px;
}}
.lang-label {{
    font-size: 0.75em;
    color: {COLOR_TEXT_SUB};
    font-weight: bold;
    margin-bottom: 4px;
    letter-spacing: 0.05em;
}}
.lang-body {{
    color: {COLOR_TEXT};
    white-space: pre-wrap;
    font-size: 0.95em;
}}

.attachments {{
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px dashed {COLOR_BORDER};
}}
.attachments-label {{
    font-size: 0.85em;
    color: {COLOR_TEXT_SUB};
    margin-bottom: 8px;
}}
.attachments-grid {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}}
.attachments-grid img {{
    width: 120px;
    height: 120px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid {COLOR_BORDER};
    cursor: pointer;
}}
.img-placeholder {{
    width: 120px;
    height: 120px;
    background: {COLOR_PRIMARY_BG2};
    border: 1px dashed {COLOR_PRIMARY_LIGHT};
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: {COLOR_PRIMARY_DARK};
    font-size: 0.8em;
    text-align: center;
    padding: 8px;
}}

.summary-card {{
    background: #fff;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 24px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    border: 1px solid {COLOR_BORDER};
}}
.summary-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid {COLOR_PRIMARY_BG2};
    padding-bottom: 12px;
    margin-bottom: 16px;
}}
.summary-title {{ font-size: 1.15em; font-weight: bold; color: {COLOR_PRIMARY_DARK}; }}
.complexity-badge {{
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
}}
.summary-grid {{
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 12px 16px;
    align-items: start;
}}
.summary-label {{
    color: {COLOR_TEXT_SUB};
    font-weight: bold;
    padding-top: 2px;
    font-size: 0.9em;
}}
.summary-value {{ color: {COLOR_TEXT}; }}
.summary-value ul {{ margin: 0; padding-left: 20px; }}
.summary-value li {{ margin-bottom: 4px; }}
.empty {{ color: #d1d5db; font-style: italic; }}

.decision-box {{
    margin-top: 16px;
    background: {COLOR_PRIMARY_BG2};
    border-left: 3px solid {COLOR_PRIMARY};
    padding: 12px 16px;
    border-radius: 6px;
    font-weight: bold;
    color: {COLOR_PRIMARY_DARK};
    font-size: 0.95em;
}}

.patterns-section-title {{
    font-size: 1.05em;
    margin: 32px 0 16px;
    color: {COLOR_PRIMARY_DARK};
    font-weight: bold;
}}

.pattern-card {{
    background: #fff;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border: 1px solid {COLOR_BORDER};
}}
.pattern-card.recommended {{
    border: 2px solid {COLOR_PRIMARY};
    background: linear-gradient(to right, {COLOR_PRIMARY_BG} 0%, #fff 40%);
}}
.pattern-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
}}
.pattern-id {{
    background: {COLOR_PRIMARY};
    color: white;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 0.85em;
    font-weight: bold;
}}
.rec-badge {{
    background: {COLOR_PRIMARY_DARK};
    color: white;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.75em;
    font-weight: bold;
}}
.stars {{
    color: {COLOR_PRIMARY};
    margin-left: auto;
    font-size: 1em;
    letter-spacing: 0.1em;
}}
.pattern-name {{
    margin: 4px 0 8px;
    font-size: 1.05em;
    color: {COLOR_TEXT};
}}
.pattern-desc {{
    color: {COLOR_TEXT_SUB};
    margin-bottom: 14px;
    font-size: 0.95em;
}}
.pros-cons {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 12px;
}}
.pros-cons-col ul {{
    list-style: none;
    padding: 0;
    margin: 0;
    font-size: 0.9em;
}}
.pros-cons-label {{
    font-size: 0.8em;
    color: {COLOR_TEXT_SUB};
    font-weight: bold;
    margin-bottom: 4px;
    letter-spacing: 0.05em;
}}
.pros-cons-col ul li {{ margin-bottom: 4px; color: {COLOR_TEXT}; }}

.rec-reason {{
    color: {COLOR_TEXT_SUB};
    font-size: 0.85em;
    font-style: italic;
    margin-bottom: 12px;
    padding-left: 12px;
    border-left: 2px solid {COLOR_PRIMARY_BG2};
}}

.select-btn {{
    background: {COLOR_PRIMARY};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9em;
    font-weight: bold;
}}
.select-btn:hover {{ background: {COLOR_PRIMARY_DARK}; }}

@media (max-width: 640px) {{
    .bilingual, .pros-cons {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
{meta_html}
{buyer_html}

<div class="summary-card">
    <div class="summary-header">
        <div class="summary-title">AIサマリー</div>
        {_complexity_badge(complexity)}
    </div>
    <div class="summary-grid">
        <div class="summary-label">感情</div>
        <div class="summary-value">{_escape(emotion) or '<span class="empty">—</span>'}</div>

        <div class="summary-label">事実</div>
        <div class="summary-value">{_render_list(summary.get("factsStated"))}</div>

        <div class="summary-label">要望</div>
        <div class="summary-value">{_escape(summary.get("requestMade")) or '<span class="empty">—</span>'}</div>

        <div class="summary-label">制約</div>
        <div class="summary-value">{_escape(summary.get("constraints")) or '<span class="empty">—</span>'}</div>

        <div class="summary-label">背景</div>
        <div class="summary-value">{_escape(summary.get("hiddenContext")) or '<span class="empty">—</span>'}</div>
    </div>
    {f'<div class="decision-box">決めること: {_escape(decision)}</div>' if decision else ''}
</div>

<div class="patterns-section-title">対応パターン（{len(patterns)}件）</div>
{pattern_cards_html}

{reply_html}

</body>
</html>
"""
    return html_doc


if __name__ == "__main__":
    sample = {
        "summary": {
            "buyerEmotion": "不満（強度4/5）",
            "factsStated": [
                "商品到着後、シューズのソールに傷を発見",
                "写真を添付済み",
                "4日前に受け取ったと記載"
            ],
            "requestMade": "全額返金またはディスカウント",
            "constraints": "返送は希望していない（送料負担を避けたい旨示唆）",
            "hiddenContext": "推測：初めての購入でeBayの返品プロセスに不慣れ。悪評を付ける意志は薄く、柔軟な解決を求めている"
        },
        "complexityLevel": "medium",
        "patterns": [
            {
                "id": "A",
                "name": "部分返金（20-30%）で継続所有",
                "description": "商品はバイヤー手元に残し、傷相当分の部分返金で合意する",
                "merits": ["送料負担なし", "評価リスク最小", "迅速解決"],
                "demerits": ["金額交渉の可能性", "傷の度合い次第で不十分"],
                "recommendation": 5,
                "recommendationReason": "バイヤーの示唆に沿う・コスト最小・再発防止にも有効"
            },
            {
                "id": "B",
                "name": "返品・全額返金",
                "description": "商品を返送してもらい全額返金。送料はセラー負担",
                "merits": ["eBay標準手続き", "バイヤー満足度高"],
                "demerits": ["往復送料負担", "商品が傷む可能性", "リサイクル不能"],
                "recommendation": 2,
                "recommendationReason": "コスト大・バイヤー希望と乖離"
            },
            {
                "id": "C",
                "name": "ディスカウントコード提供（次回購入）",
                "description": "今回は現状維持、次回購入時のディスカウントコードを提供",
                "merits": ["今回コスト0", "リピーター化機会"],
                "demerits": ["不満未解決・悪評リスク", "初回購入者には弱い"],
                "recommendation": 1,
                "recommendationReason": "現状不満への直接対応になっていない"
            }
        ],
        "recommendedPattern": "A",
        "sellerDecisionNeeded": "部分返金の金額確定（20%/25%/30%のいずれか）"
    }

    buyer_en = "Hello, I received my shoes 4 days ago but when I opened the box, I found a scratch on the sole. I'm attaching photos. I'd like a refund or a discount. I don't want to ship them back since shipping is expensive for me. Thanks."
    buyer_ja = "こんにちは、4日前にシューズを受け取ったのですが、箱を開けたらソールに傷がありました。写真を添付しています。返金かディスカウントをお願いしたいです。送料が高いので返送はしたくありません。よろしくお願いします。"

    html_output = render_summary_to_html(
        sample,
        buyer_message_en=buyer_en,
        buyer_message_ja=buyer_ja,
        attached_images=[
            "シューズのソール傷 - 画像1.jpg",
            "シューズのソール傷 - 画像2.jpg",
        ],
        model_name="Gemini 2.5 Flash (サンプル)",
        elapsed=1.8,
        cost_jpy=0.51,
    )

    import os
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "prompt_summary_v0.1_preview.html")
    out_path = os.path.abspath(out_path)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"プレビュー生成完了: {out_path}")
