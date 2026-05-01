"""
HTML レポート生成

【方針】
- Ver.1 は外部ライブラリ不使用・標準 string テンプレートで吐き出す
- 「手段（どこから取った）・根拠（販売実績の証拠）・結果（利益試算）」が一目で分かる構造
"""

import html
from datetime import datetime


def _badge(text: str, color: str) -> str:
    return f'<span class="badge" style="background:{color}">{html.escape(text)}</span>'


def _format_jpy(v) -> str:
    try:
        return f'¥{int(v):,}'
    except Exception:
        return ''


def _format_usd(v) -> str:
    try:
        return f'${float(v):,.2f}'
    except Exception:
        return ''


def _profit_color(usd: float) -> str:
    if usd >= 30:
        return '#4ade80'  # green
    if usd >= 0:
        return '#fbbf24'  # amber
    return '#f87171'      # red


def render_html(records: list[dict], out_path: str, *, generated_at: str = '') -> None:
    rows_html: list[str] = []
    profitable_count = sum(1 for r in records if r['net_profit_usd'] > 0)

    if records:
        fx_rate = records[0].get('fx_rate_usd_jpy', '-')
    else:
        fx_rate = '-'

    for i, r in enumerate(records, 1):
        profit_color = _profit_color(r['net_profit_usd'])
        match_color = '#22c55e' if r['match_score'] >= 80 else ('#eab308' if r['match_score'] >= 60 else '#f59e0b')
        ebay_img = r.get('ebay_image', '')
        img_html = f'<img src="{html.escape(ebay_img)}" loading="lazy">' if ebay_img else ''

        rows_html.append(f'''
        <div class="card">
          <div class="rank">#{i}</div>
          <div class="thumb">{img_html}</div>
          <div class="body">
            <div class="title"><a href="{html.escape(r["ebay_url"])}" target="_blank" rel="noopener">{html.escape(r["ebay_title"])}</a></div>
            <div class="meta">
              キーワード: <code>{html.escape(r["keyword"])}</code> ／
              出品者: <a href="https://www.ebay.com/usr/{html.escape(r["ebay_seller"])}" target="_blank">{html.escape(r["ebay_seller"])}</a>
              <span class="muted">({r["ebay_seller_feedback"]}% / {r["ebay_seller_score"]})</span>
              {_badge(f'FVF: {r["fvf_category"]}', '#475569')}
              {_badge(f'関税: {r["duty_category"]}', '#7c3aed')}
              {_badge(f'重量推定: {r["weight_kg"]}kg', '#0ea5e9')}
            </div>
            <div class="grid">
              <div class="col">
                <h4>① eBay 売価（収入）</h4>
                <p class="big">{_format_usd(r["ebay_price_usd"])}<small> ＋ 送料 {_format_usd(r["ebay_buyer_shipping_usd"])}</small></p>
                <p>合計 <b>{_format_usd(r["gross_revenue_usd"])}</b></p>
              </div>
              <div class="col">
                <h4>② 日本仕入候補</h4>
                <p class="big">{_format_jpy(r["supplier_price_jpy"])} <small>({_format_usd(r["purchase_price_usd"])})</small></p>
                <p>
                  <a href="{html.escape(r["supplier_url"])}" target="_blank" rel="noopener">{html.escape(r["supplier_source"])}</a>
                  ／ {html.escape(r["supplier_shop"] or '-')}
                  ／ {_badge(f'一致 {r["match_score"]}点', match_color)}
                </p>
                <p class="muted">{html.escape(r["supplier_name"][:80])}</p>
              </div>
              <div class="col">
                <h4>③ コスト内訳</h4>
                <table>
                  <tr><td>eBay 手数料合計</td><td>{_format_usd(r["total_ebay_fees_usd"])}</td></tr>
                  <tr><td>国際送料 ({_format_jpy(r["shipping_cost_jpy"])})</td><td>{_format_usd(r["shipping_cost_usd"])}</td></tr>
                  <tr><td>仕入価格 (税抜)</td><td>{_format_usd(r["purchase_price_usd"])}</td></tr>
                  <tr><td>為替差損 (Wise)</td><td>{_format_usd(r["fx_loss_usd"])}</td></tr>
                  <tr class="muted"><td>輸入関税 (買い手払い参考)</td><td>{_format_usd(r["us_import_duty_usd_buyer_pays"])} ({r["us_import_duty_rate"]*100:.0f}%)</td></tr>
                </table>
              </div>
              <div class="col profit" style="border-color:{profit_color}">
                <h4>④ 純利益</h4>
                <p class="huge" style="color:{profit_color}">{_format_usd(r["net_profit_usd"])}</p>
                <p class="big">{_format_jpy(r["net_profit_jpy"])}</p>
                <p>マージン <b>{r["profit_margin_pct"]}%</b></p>
                <p class="muted">損益分岐仕入: {_format_jpy(r["breakeven_purchase_jpy"])}</p>
              </div>
            </div>
          </div>
        </div>
        ''')

    html_doc = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>eBay 無在庫リサーチツール — 結果レポート</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", "Hiragino Sans", "Yu Gothic", system-ui, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:0; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
  h1 {{ color: #a78bfa; border-bottom: 3px solid #a78bfa; padding-bottom: 8px; }}
  .summary {{ background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 24px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
  .summary .item {{ text-align: center; }}
  .summary .item .label {{ font-size: 12px; color:#94a3b8; }}
  .summary .item .val {{ font-size: 24px; font-weight: bold; color: #a78bfa; }}
  .card {{ background: #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 16px; display: grid; grid-template-columns: 60px 140px 1fr; gap: 16px; }}
  .rank {{ font-size: 32px; font-weight: bold; color: #a78bfa; }}
  .thumb img {{ width: 140px; max-height: 140px; object-fit: contain; border-radius: 8px; background: #0f172a; }}
  .title a {{ color: #f1f5f9; text-decoration: none; font-size: 16px; font-weight: 600; }}
  .title a:hover {{ color: #a78bfa; }}
  .meta {{ font-size: 12px; color: #94a3b8; margin: 8px 0 12px; }}
  .meta a {{ color: #c4b5fd; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; color: white; margin-right: 4px; }}
  .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
  .col {{ background: #0f172a; border-radius: 8px; padding: 12px; border: 2px solid transparent; }}
  .col.profit {{ background: #0c1426; }}
  .col h4 {{ margin: 0 0 8px; font-size: 11px; color: #94a3b8; text-transform: uppercase; }}
  .col p {{ margin: 4px 0; }}
  .col .big {{ font-size: 18px; font-weight: 600; color: #f1f5f9; }}
  .col .huge {{ font-size: 28px; font-weight: bold; }}
  .col small {{ font-size: 12px; color: #94a3b8; }}
  .col table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  .col table td {{ padding: 2px 0; }}
  .col table td:last-child {{ text-align: right; font-weight: 500; }}
  .muted {{ color: #64748b; font-size: 11px; }}
  code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; }}
  .footer {{ margin-top: 32px; padding: 16px; color: #64748b; font-size: 11px; line-height: 1.6; }}
  .footer h4 {{ color: #94a3b8; }}
</style>
</head>
<body>
<div class="container">
  <h1>🔎 eBay 無在庫リサーチツール — 結果レポート</h1>
  <div class="summary">
    <div class="item"><div class="label">候補総数</div><div class="val">{len(records)}</div></div>
    <div class="item"><div class="label">黒字候補</div><div class="val" style="color:#4ade80">{profitable_count}</div></div>
    <div class="item"><div class="label">USD/JPY</div><div class="val">{fx_rate}</div></div>
    <div class="item"><div class="label">生成日時</div><div class="val" style="font-size:14px">{html.escape(generated_at)}</div></div>
  </div>

  {''.join(rows_html)}

  <div class="footer">
    <h4>本ツールについて（Ver.1）</h4>
    <p>
      <b>手段</b>:<br>
      ① eBay Browse API（公式・OAuth Application Token）で「米国マーケットに日本セラーが出している商品」を取得<br>
      ② タイトルから型番（例: DD1391-100）・ブランド・キーワードを抽出<br>
      ③ 楽天市場 + Yahoo!ショッピングの検索ページ（HTML 内 __INITIAL_STATE__ / __NEXT_DATA__ JSON 抽出）で同一商品を探索<br>
      ④ 一致スコア 45 点以上の最安候補を採用<br>
      ⑤ 全コスト（FVF・送料・関税・為替・国内コスト）を入れた純利益を試算
    </p>
    <p>
      <b>2026 年版の重要前提</b>:<br>
      ・米国 De Minimis $800 免税は <b>2025/8/29 廃止・継続中</b> → 全パッケージ関税対象<br>
      ・Section 122 全国 10% 追加関税は <b>2026/2/24 施行・2026/7/24 失効予定</b><br>
      ・スニーカー $150 以上は <b>FVF 8% / per-order 免除</b>（StockX 対抗で 2024 年導入）<br>
      ・売上税は eBay が買い手から徴収して州に直接送金 → セラー粗利には含めない
    </p>
    <p>
      <b>限界・Ver.2 で改善予定</b>:<br>
      ・SOLD（実販売）データは Marketplace Insights API 申請後に追加（現状は「ライバル日本セラーが出品中」を需要シグナルとして使用）<br>
      ・楽天/Yahoo は公式 API キー登録後に切替（取得安定性 + JAN 直叩き）<br>
      ・Amazon.co.jp / メルカリ / 駿河屋 / モノタロウ等の追加仕入先<br>
      ・Claude API による商品画像・タイトル類似性のセマンティック判定<br>
      ・カテゴリ ID と HTS コードの対応表精緻化（重量推定 / 関税精度向上）
    </p>
  </div>
</div>
</body>
</html>
'''

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_doc)
