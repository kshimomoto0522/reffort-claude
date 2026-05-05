# -*- coding: utf-8 -*-
"""
cat03 テストケースに shipment block を注入する（本番ペイロード再現）。

shipped event があるケースに対して、developer role で shipment 情報を input[1] 位置に注入。
"""
import json
import os

CAT03_PATH = "test_cases/category_03_post_purchase_shipping_qa.json"

# 各ケースの shipment block 定義（shipped event があるケースのみ）
SHIPMENT_BLOCKS = {
    "cat03_02_tracking_not_updating": {
        "shippingCarrier": "DHL Express",
        "trackingNumber": "1234567890",
        "estimatedDeliveryTimeMin": "2026-05-05T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-08T08:00:00.000Z",
        "shipByDate": "2026-05-02T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
    "cat03_03_delivery_overdue_anxious": {
        "shippingCarrier": "EMS International",
        "trackingNumber": "EE123456789JP",
        "estimatedDeliveryTimeMin": "2026-05-01T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-03T08:00:00.000Z",
        "shipByDate": "2026-04-26T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
    "cat03_04_customs_held": {
        "shippingCarrier": "FedEx International Priority",
        "trackingNumber": "770012345678",
        "estimatedDeliveryTimeMin": "2026-05-03T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-06T08:00:00.000Z",
        "shipByDate": "2026-04-30T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
    "cat03_05_missing_accessory_minor_apology": {
        "shippingCarrier": "DHL Express",
        "trackingNumber": "9876543210",
        "estimatedDeliveryTimeMin": "2026-04-30T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-02T08:00:00.000Z",
        "shipByDate": "2026-04-27T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
    "cat03_06_shipped_then_customs_question": {
        "shippingCarrier": "EMS International",
        "trackingNumber": "EJ987654321JP",
        "estimatedDeliveryTimeMin": "2026-05-08T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-12T08:00:00.000Z",
        "shipByDate": "2026-05-03T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
    "cat03_07_tracking_stuck_anxious_multi": {
        "shippingCarrier": "FedEx International Economy",
        "trackingNumber": "770098765432",
        "estimatedDeliveryTimeMin": "2026-05-01T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-05T08:00:00.000Z",
        "shipByDate": "2026-04-26T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
    "cat03_08_carrier_redirect_question": {
        "shippingCarrier": "FedEx International Priority",
        "trackingNumber": "770011223344",
        "estimatedDeliveryTimeMin": "2026-05-06T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-09T08:00:00.000Z",
        "shipByDate": "2026-05-04T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
    "cat03_09_box_damaged_minor_apology_multi": {
        "shippingCarrier": "EMS International",
        "trackingNumber": "EJ112233445JP",
        "estimatedDeliveryTimeMin": "2026-04-29T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-02T08:00:00.000Z",
        "shipByDate": "2026-04-24T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
    "cat03_11_customs_refund_demand_assertive": {
        "shippingCarrier": "FedEx International Priority",
        "trackingNumber": "770099887766",
        "estimatedDeliveryTimeMin": "2026-05-02T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-05T08:00:00.000Z",
        "shipByDate": "2026-04-27T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
    "cat03_12_counterfeit_accusation_assertive": {
        "shippingCarrier": "DHL Express",
        "trackingNumber": "DHL5566778899",
        "estimatedDeliveryTimeMin": "2026-05-02T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-05T08:00:00.000Z",
        "shipByDate": "2026-04-27T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
    "cat03_13_address_blame_buyer_fault_assertive": {
        "shippingCarrier": "FedEx International Priority",
        "trackingNumber": "770044556677",
        "estimatedDeliveryTimeMin": "2026-05-02T08:00:00.000Z",
        "estimatedDeliveryTimeMax": "2026-05-05T08:00:00.000Z",
        "shipByDate": "2026-04-27T14:59:59.000Z",
        "whoPaysShipping": "Buyer",
        "detailProduct": None,
    },
}


def inject():
    with open(CAT03_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    updated = 0
    for case in cases:
        cid = case["id"]
        if cid not in SHIPMENT_BLOCKS:
            continue
        block = SHIPMENT_BLOCKS[cid]
        # 既に shipment block が注入済みかチェック（input[1]に shippingCarrier が含まれていれば既存）
        inputs = case["input"]
        if len(inputs) >= 2 and inputs[1].get("role") == "developer":
            content = inputs[1].get("content", "")
            if "shippingCarrier" in content:
                # 既に注入済みなら更新
                inputs[1] = {"role": "developer", "content": json.dumps(block, ensure_ascii=False)}
                updated += 1
                continue
        # 新規注入：input[0] (商品情報) の直後に挿入
        new_block = {"role": "developer", "content": json.dumps(block, ensure_ascii=False)}
        inputs.insert(1, new_block)
        updated += 1

    with open(CAT03_PATH, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

    print(f"Updated {updated} cases with shipment block.")
    print(f"Total cases in cat03: {len(cases)}")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    inject()
