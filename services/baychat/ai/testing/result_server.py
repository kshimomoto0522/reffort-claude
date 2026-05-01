"""
比較HTML向けローカル再生成APIサーバー
====================================================================
比較HTMLから「補足情報を入れて生成ボタン」を押すと、ここのAPIが
GPT-4.1-Mini / GPT-4o-Mini / GPT-5-Mini の3モデルで本番ペイロード再現の
admin_prompt を実行し、結果をJSONで返す。

起動:
    python result_server.py
    → http://127.0.0.1:8765 で待ち受け

エンドポイント:
    POST /api/regenerate
        body: {
            "case_id": "cat02_03_brand_new_or_used",
            "supplemental": "新品で未使用、箱・papers・タグ全部あり",
            "tone": "polite" | "friendly" | "apologetic",
            "prompt_version": "2.3_baseline_natural2",
            "test_case_path": "test_cases/category_02_natural5_subset.json"
        }
        response: {
            "case_id": "...",
            "tone": "polite",
            "results": [
                {"model_id":"gpt","model_name":"GPT-4.1-Mini",
                 "buyer_reply":"...","jpn_reply":"...","elapsed":3.2,
                 "cost_jpy":0.4,"input_tokens":...,"output_tokens":...},
                ...
            ]
        }
"""

import os
import sys
import json

# Windows でも UTF-8 出力可能に
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from flask import Flask, request, jsonify
from flask_cors import CORS

from batch_test import (
    AVAILABLE_MODELS, JPY_RATE,
    load_prompt_from_md, call_model,
    OPENAI_API_KEY,
)
from payload_builder import (
    build_production_payload,
    get_production_response_format,
    PRODUCTION_TEMPERATURE,
)


app = Flask(__name__)
CORS(app)  # ローカルファイルからのfetchに対応


# 画面側「TO」値（buyer_ebay）として使う既定値マップ — テストケース内の値を優先
DEFAULT_SELLER_NAME = "rioxxrinaxjapan"


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "BayChat AI Reply 再生成API",
        "endpoints": ["/api/regenerate (POST)"],
        "models": list(AVAILABLE_MODELS.keys()),
    })


@app.route("/api/regenerate", methods=["POST"])
def regenerate():
    data = request.get_json(force=True, silent=True) or {}

    case_id = data.get("case_id")
    supplemental = (data.get("supplemental") or "").strip()
    tone = data.get("tone", "polite")
    prompt_version = data.get("prompt_version", "2.3_baseline_natural2")
    test_case_path_rel = data.get(
        "test_case_path",
        "test_cases/category_02_natural5_subset.json",
    )
    seller_name = data.get("seller_name", DEFAULT_SELLER_NAME)
    model_ids = data.get("models", ["gpt", "gpt4omini", "gpt5mini"])

    if not case_id:
        return jsonify({"error": "case_id is required"}), 400
    if tone not in ("polite", "friendly", "apologetic"):
        return jsonify({"error": f"invalid tone: {tone}"}), 400

    test_case_path = os.path.join(SCRIPT_DIR, test_case_path_rel)
    if not os.path.exists(test_case_path):
        return jsonify({"error": f"test case file not found: {test_case_path_rel}"}), 404

    # ケース読み込み
    try:
        with open(test_case_path, "r", encoding="utf-8") as f:
            cases = json.load(f)
    except Exception as e:
        return jsonify({"error": f"failed to load cases: {e}"}), 500

    case = next((c for c in cases if c.get("id") == case_id), None)
    if case is None:
        return jsonify({"error": f"case not found: {case_id}"}), 404

    # admin プロンプト読み込み
    try:
        admin_prompt = load_prompt_from_md(prompt_version)
    except Exception as e:
        return jsonify({"error": f"failed to load prompt v{prompt_version}: {e}"}), 500

    buyer_name = case.get("buyer_ebay") or ""

    results = []
    for mid in model_ids:
        if mid not in AVAILABLE_MODELS:
            results.append({"model_id": mid, "error": f"unknown model id: {mid}"})
            continue
        label, provider, model_id, in_p, out_p = AVAILABLE_MODELS[mid]

        if provider == "openai" and not OPENAI_API_KEY:
            results.append({"model_id": mid, "model_name": label,
                            "error": "OPENAI_API_KEY not set"})
            continue

        # 本番ペイロード組み立て (description = 補足情報)
        try:
            messages = build_production_payload(
                test_case=case,
                admin_prompt_text=admin_prompt,
                tone=tone,
                buyer_name=buyer_name,
                seller_name=seller_name,
                description=supplemental,
                include_forced_template=False,  # 2.3_baseline* は自動False
                prompt_version=prompt_version,
            )
        except Exception as e:
            results.append({"model_id": mid, "model_name": label,
                            "error": f"payload build failed: {e}"})
            continue

        # 推論実行 (本番再現: temperature=0.2 + json_schema strict)
        try:
            if provider == "openai":
                text, in_tok, out_tok, elapsed = call_model(
                    provider, model_id, messages,
                    response_format=get_production_response_format(),
                    temperature_override=PRODUCTION_TEMPERATURE,
                )
            else:
                text, in_tok, out_tok, elapsed = call_model(
                    provider, model_id, messages,
                )
        except Exception as e:
            results.append({"model_id": mid, "model_name": label,
                            "error": f"API call failed: {e}"})
            continue

        # JSON 解析
        try:
            rj = json.loads(text)
            buyer_reply = rj.get("buyerLanguage", text)
            jpn_reply = rj.get("jpnLanguage", "")
        except json.JSONDecodeError:
            buyer_reply = text
            jpn_reply = "(JSON parse failed)"

        cost_usd = (in_tok / 1_000_000 * in_p) + (out_tok / 1_000_000 * out_p)
        cost_jpy = cost_usd * JPY_RATE

        results.append({
            "model_id": mid,
            "model_name": label,
            "buyer_reply": buyer_reply,
            "jpn_reply": jpn_reply,
            "elapsed": round(elapsed, 2),
            "cost_jpy": round(cost_jpy, 3),
            "input_tokens": in_tok,
            "output_tokens": out_tok,
        })

    return jsonify({
        "case_id": case_id,
        "tone": tone,
        "supplemental": supplemental,
        "prompt_version": prompt_version,
        "results": results,
    })


if __name__ == "__main__":
    print("=" * 70)
    print("  BayChat AI Reply 再生成APIサーバー")
    print("  起動URL: http://127.0.0.1:8765")
    print("  比較HTMLの「補足情報を入れて生成」ボタンから呼び出されます")
    print("  停止: Ctrl+C")
    print("=" * 70)
    app.run(host="127.0.0.1", port=8765, debug=False, use_reloader=False)
