"""
HTML レポート生成（Ver.1.5）

【Ver.1 → Ver.1.5 改善】
- 「売れる根拠」セクションをカードに追加（evidence score + 市場概要 + 価格ポジション）
- ゲート通過候補のみを出力（赤字・低根拠は CSV/JSON に残るが HTML から除外）
- カテゴリ・サマリ統計を上部に追加
"""

import html
from typing import Optional


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
    if usd >= 50:
        return '#4ade80'
    if usd >= 20:
        return '#86efac'
    if usd >= 0:
        return '#fbbf24'
    return '#f87171'


def _evidence_color(score: float) -> str:
    if score >= 75:
        return '#22c55e'
    if score >= 60:
        return '#a78bfa'
    if score >= 45:
        return '#eab308'
    return '#f87171'


def _verdict_label(verdict: str) -> str:
    return {
        'strong': '強い',
        'moderate': '中',
        'weak': '弱い',
        'insufficient': '不足',
    }.get(verdict, verdict)


def _signal_color(label: str) -> str:
    return {
        'high': '#4ade80',
        'medium': '#a78bfa',
        'low': '#f87171',
        'healthy': '#4ade80',
        'sparse': '#a78bfa',
        'saturated': '#f87171',
        'wins': '#4ade80',
        'parity': '#a78bfa',
        'loses': '#f87171',
    }.get(label, '#94a3b8')


def render_html(records: list[dict], out_path: str, *, generated_at: str = '',
                all_evaluated_count: Optional[int] = None) -> None:
    rows_html: list[str] = []

    if records:
        fx_rate = records[0].get('fx_rate_usd_jpy', '-')
    else:
        fx_rate = '-'

    # サマリ集計
    total_passed = len(records)
    avg_evidence = (sum(r['evidence_score'] for r in records) / total_passed) if total_passed else 0
    avg_margin = (sum(r['profit_margin_pct'] for r in records) / total_passed) if total_passed else 0
    total_profit_usd = sum(r['net_profit_usd'] for r in records)
    keyword_count = len({r['keyword'] for r in records})

    for i, r in enumerate(records, 1):
        profit_color = _profit_color(r['net_profit_usd'])
        evid_color = _evidence_color(r['evidence_score'])
        match_color = '#22c55e' if r['match_score'] >= 80 else ('#eab308' if r['match_score'] >= 60 else '#f59e0b')
        ebay_img = r.get('ebay_image', '')
        img_html = f'<img src="{html.escape(ebay_img)}" loading="lazy">' if ebay_img else ''

        # 競合シグナル文言
        comp_text = {
            'healthy': '健全な競争',
            'sparse': '競合少（ニッチ）',
            'saturated': '飽和警戒',
        }.get(r.get('competition_signal', ''), r.get('competition_signal', ''))

        demand_text = {
            'high': '需要 強',
            'medium': '需要 中',
            'low': '需要 弱',
        }.get(r.get('demand_signal', ''), r.get('demand_signal', ''))

        price_text = {
            'wins': '価格優位',
            'parity': '価格同等',
            'loses': '価格劣位',
        }.get(r.get('price_competitiveness', ''), r.get('price_competitiveness', ''))

        rows_html.append(f'''
        <div class="card">
          <div class="rank">#{i}</div>
          <div class="thumb">{img_html}</div>
          <div class="body">
            <div class="title-row">
              <a class="title" href="{html.escape(r["ebay_url"])}" target="_blank" rel="noopener">{html.escape(r["ebay_title"])}</a>
              <div class="evidence-pill" style="background:{evid_color}">
                根拠 {r["evidence_score"]:.0f} 点 / {_verdict_label(r["evidence_verdict"])}
              </div>
            </div>
            <div class="meta">
              {_badge(html.escape(r["keyword"]), '#475569')}
              出品者 <a href="https://www.ebay.com/usr/{html.escape(r["ebay_seller"])}" target="_blank">{html.escape(r["ebay_seller"])}</a>
              <span class="muted">({r["ebay_seller_feedback"]}% / {r["ebay_seller_score"]} 評価)</span>
              {_badge(f'FVF: {r["fvf_category"]}', '#7c3aed')}
              {_badge(f'関税: {r["duty_category"]} ({r["us_import_duty_rate"]*100:.0f}%)', '#0ea5e9')}
              {_badge(f'重量推定 {r["weight_kg"]}kg', '#475569')}
            </div>

            <div class="grid">
              <div class="col">
                <h4>① eBay 売価（収入）</h4>
                <p class="big">{_format_usd(r["ebay_price_usd"])} <small>+ 送料 {_format_usd(r["ebay_buyer_shipping_usd"])}</small></p>
                <p>合計 <b>{_format_usd(r["gross_revenue_usd"])}</b></p>
              </div>
              <div class="col">
                <h4>② 日本仕入候補</h4>
                <p class="big">{_format_jpy(r["supplier_price_jpy"])} <small>({_format_usd(r["purchase_price_usd"])})</small></p>
                <p>
                  <a href="{html.escape(r["supplier_url"])}" target="_blank" rel="noopener">{html.escape(r["supplier_source"])}</a>
                  ／ {html.escape(r["supplier_shop"] or "-")}
                  ／ {_badge(f'一致 {r["match_score"]}点', match_color)}
                  ／ {_badge(r.get("supplier_condition", "n/a"), '#475569')}
                </p>
                <p class="muted">{html.escape(r["supplier_name"][:80])}</p>
              </div>
              <div class="col">
                <h4>③ コスト内訳</h4>
                <table>
                  <tr><td>eBay 手数料合計</td><td>{_format_usd(r["total_ebay_fees_usd"])}</td></tr>
                  <tr><td>国際送料 ({_format_jpy(r["shipping_cost_jpy"])})</td><td>{_format_usd(r["shipping_cost_usd"])}</td></tr>
                  <tr><td>仕入価格（税抜）</td><td>{_format_usd(r["purchase_price_usd"])}</td></tr>
                  <tr><td>為替差損（Wise）</td><td>{_format_usd(r["fx_loss_usd"])}</td></tr>
                  <tr class="muted"><td>関税（買い手払い参考）</td><td>{_format_usd(r["us_import_duty_usd_buyer_pays"])}</td></tr>
                </table>
              </div>
              <div class="col profit" style="border-color:{profit_color}">
                <h4>④ 純利益</h4>
                <p class="huge" style="color:{profit_color}">{_format_usd(r["net_profit_usd"])}</p>
                <p class="big">{_format_jpy(r["net_profit_jpy"])}</p>
                <p>マージン <b>{r["profit_margin_pct"]:.1f}%</b></p>
                <p class="muted">損益分岐仕入 {_format_jpy(r["breakeven_purchase_jpy"])}</p>
              </div>
            </div>

            <div class="evidence-block">
              <h4>⑤ 売れる根拠（市場シグナル）</h4>
              <div class="signals">
                <div class="signal-pill" style="background:{_signal_color(r.get("demand_signal", ""))}">{html.escape(demand_text)}</div>
                <div class="signal-pill" style="background:{_signal_color(r.get("competition_signal", ""))}">{html.escape(comp_text)}</div>
                <div class="signal-pill" style="background:{_signal_color(r.get("price_competitiveness", ""))}">{html.escape(price_text)}</div>
              </div>
              <table class="market-table">
                <tr>
                  <td>eBay 全体 出品総数</td><td><b>{r["market_total_listed"]:,} 件</b></td>
                  <td>ユニークセラー</td><td><b>{r["market_unique_sellers"]} 名</b></td>
                </tr>
                <tr>
                  <td>日本セラー / 米国セラー</td><td>{r["market_jp_sellers"]} / {r["market_us_sellers"]} 名</td>
                  <td>価格レンジ（USD）</td><td>${r["market_price_min_usd"]:.0f} - ${r["market_price_max_usd"]:.0f}</td>
                </tr>
                <tr>
                  <td>市場中央値</td><td><b>${r["market_price_median_usd"]:.0f}</b> (P75 ${r["market_price_p75_usd"]:.0f})</td>
                  <td>自分の想定売価</td><td><b>${r["ebay_price_usd"]:.0f}</b></td>
                </tr>
              </table>
              <p class="rationale-text">{html.escape(r.get("evidence_rationale", ""))}</p>
            </div>
          </div>
        </div>
        ''')

    extra_evaluated = ''
    if all_evaluated_count is not None and all_evaluated_count > total_passed:
        extra_evaluated = f' / 全評価 {all_evaluated_count} 件中ゲート通過'

    html_doc = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>eBay 無在庫リサーチツール Ver.1.5 — 結果レポート</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", "Hiragino Sans", "Yu Gothic", system-ui, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:0; }}
  .container {{ max-width: 1500px; margin: 0 auto; padding: 24px; }}
  h1 {{ color: #a78bfa; border-bottom: 3px solid #a78bfa; padding-bottom: 8px; }}
  .summary {{ background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 24px; display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; }}
  .summary .item {{ text-align: center; }}
  .summary .item .label {{ font-size: 12px; color:#94a3b8; }}
  .summary .item .val {{ font-size: 24px; font-weight: bold; color: #a78bfa; }}
  .gate-info {{ background: #1e293b; border-left: 4px solid #a78bfa; padding: 12px 20px; margin-bottom: 24px; border-radius: 6px; font-size: 13px; color: #cbd5e1; }}
  .card {{ background: #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 16px; display: grid; grid-template-columns: 50px 130px 1fr; gap: 16px; }}
  .rank {{ font-size: 28px; font-weight: bold; color: #a78bfa; }}
  .thumb img {{ width: 130px; max-height: 130px; object-fit: contain; border-radius: 8px; background: #0f172a; }}
  .title-row {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 6px; }}
  .title {{ color: #f1f5f9; text-decoration: none; font-size: 15px; font-weight: 600; flex: 1; }}
  .title:hover {{ color: #a78bfa; }}
  .evidence-pill {{ padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: 600; color: white; white-space: nowrap; }}
  .meta {{ font-size: 12px; color: #94a3b8; margin: 6px 0 12px; }}
  .meta a {{ color: #c4b5fd; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; color: white; margin-right: 4px; }}
  .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 12px; }}
  .col {{ background: #0f172a; border-radius: 8px; padding: 12px; border: 2px solid transparent; }}
  .col.profit {{ background: #0c1426; }}
  .col h4 {{ margin: 0 0 6px; font-size: 11px; color: #94a3b8; text-transform: uppercase; }}
  .col p {{ margin: 3px 0; }}
  .col .big {{ font-size: 17px; font-weight: 600; color: #f1f5f9; }}
  .col .huge {{ font-size: 26px; font-weight: bold; }}
  .col small {{ font-size: 11px; color: #94a3b8; }}
  .col table {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
  .col table td {{ padding: 2px 0; }}
  .col table td:last-child {{ text-align: right; font-weight: 500; }}
  .evidence-block {{ background: #0f172a; border-radius: 8px; padding: 12px; border-left: 3px solid #a78bfa; }}
  .evidence-block h4 {{ margin: 0 0 8px; font-size: 11px; color: #a78bfa; text-transform: uppercase; }}
  .signals {{ display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }}
  .signal-pill {{ padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 500; color: white; }}
  .market-table {{ width: 100%; font-size: 11px; border-collapse: collapse; }}
  .market-table td {{ padding: 2px 6px; color: #cbd5e1; }}
  .market-table td:nth-child(2), .market-table td:nth-child(4) {{ color: #f1f5f9; font-weight: 500; }}
  .rationale-text {{ font-size: 11px; color: #94a3b8; margin: 8px 0 0; line-height: 1.5; }}
  .muted {{ color: #64748b; font-size: 11px; }}
  code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; }}
  .footer {{ margin-top: 32px; padding: 16px; color: #64748b; font-size: 11px; line-height: 1.6; }}
  .footer h4 {{ color: #94a3b8; }}
</style>
</head>
<body>
<div class="container">
  <h1>🔎 eBay 無在庫リサーチツール Ver.1.5 — 結果レポート</h1>
  <div class="gate-info">
    <b>ゲート:</b> 純利益 ≥ $15 ／ マージン ≥ 15% ／ 売れる根拠スコア ≥ 45 点 ／ 仕入候補が新品判定
    {html.escape(extra_evaluated)}
  </div>
  <div class="summary">
    <div class="item"><div class="label">候補総数</div><div class="val">{total_passed}</div></div>
    <div class="item"><div class="label">対象キーワード</div><div class="val">{keyword_count}</div></div>
    <div class="item"><div class="label">平均根拠スコア</div><div class="val" style="color:#4ade80">{avg_evidence:.0f}</div></div>
    <div class="item"><div class="label">平均マージン</div><div class="val">{avg_margin:.0f}%</div></div>
    <div class="item"><div class="label">合計利益</div><div class="val">{_format_usd(total_profit_usd)}</div></div>
  </div>

  {''.join(rows_html)}

  <div class="footer">
    <h4>本ツール Ver.1.5 について</h4>
    <p>
      <b>手段</b>:<br>
      ① eBay Browse API（Application Token）で米国マーケット全体スナップショット（出品総数・価格分布・ユニークセラー数・JP/US 比率）取得<br>
      ② 同 API で日本セラー（itemLocationCountry=JP）の出品を抽出<br>
      ③ 各商品のタイトルから型番・ブランド抽出 → 楽天市場・Yahoo!ショッピング・Amazon.co.jp・Yahoo!フリマ・駿河屋を並列検索<br>
      ④ 中古マーカーを除外（タイトルに【中古】等を含むものは新品リサーチでは弾く）<br>
      ⑤ 一致スコア 45 点以上の最安候補を採用<br>
      ⑥ 全コスト（FVF・送料・関税・為替・国内コスト）の純利益試算<br>
      ⑦ 「売れる根拠スコア」を 7 シグナルから 0-100 で計算（需要総数・競合数・同型番セラー数・価格優位性・出品の長寿性・上位セラー実績）<br>
      ⑧ ゲート通過のみを出力
    </p>
    <p>
      <b>2026 年版の重要前提</b>:<br>
      ・米国 De Minimis $800 免税は <b>2025/8/29 廃止・継続中</b>。$1 でも関税申告対象<br>
      ・Section 122 全国 10% 追加関税は <b>2026/2/24 施行・2026/7/24 失効予定</b><br>
      ・スニーカー $150 以上は <b>FVF 8% / per-order 免除</b>（2024 StockX 対抗）<br>
      ・eBay User Agreement 改訂（2026/2/20）で AI/LLM bot 検索ページスクレイピング全面禁止 → Browse API のみ使用
    </p>
    <p>
      <b>Ver.1.5 の限界（5/31 までに改善予定）</b>:<br>
      ・SOLD（実販売実績）データは未取得：Marketplace Insights API 申請後に追加（現状は「現在出品中の競合厚み」を需要シグナルの代理指標）<br>
      ・watchCount は申請承認制：App Check 申請通過後に追加<br>
      ・楽天/Yahoo!ショッピング/Yahoo!フリマは公式 API キー登録後に切替予定<br>
      ・Amazon.co.jp はスクレイピング暫定動作（curl_cffi + chrome131 偽装で 2026/5 時点動作確認）<br>
      ・Reffort 自社販売実績起点モード（過去 90 日に売れた商品からの逆引き）は未実装<br>
      ・メルカリ・ヨドバシ・サウンドハウスは Sprint 2 で追加予定
    </p>
    <p>
      <b>Ver.1（2026/4/30 版）の問題点と Ver.1.5 の対処</b>:<br>
      ・[Ver.1] 中古商品が新品リサーチに混入 → [Ver.1.5] 中古マーカー除外・Amazon の condition 推定追加<br>
      ・[Ver.1] スニーカー偏重（14 中 6 件）→ [Ver.1.5] 12 カテゴリ全網羅・スニーカー 2 銘柄に縮小<br>
      ・[Ver.1] 赤字 16 件混入 → [Ver.1.5] 利益 $15 + マージン 15% + 根拠 45 点 のゲートで除外<br>
      ・[Ver.1] 仕入先 2 サイト → [Ver.1.5] 5 サイト並列<br>
      ・[Ver.1] 売れる根拠ゼロ → [Ver.1.5] 7 シグナル合成 0-100 スコア
    </p>
  </div>
</div>
</body>
</html>
'''

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_doc)
