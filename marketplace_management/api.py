import frappe
from werkzeug import Response
import json


@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_app_info(marketplace):
    data = frappe.get_single("Marketplace Management")
    if marketplace == "lazada":
        return Response(
            json.dumps(
                {
                    "client_id": int(data.client_id),
                    "client_secret": data.client_secret,
                }
            ),
            status=200,
            mimetype="application/json",
        )
    if marketplace == "shopee":
        return Response(
            json.dumps(
                {"partner_id": int(data.partner_id), "partner_key": data.partner_key}
            ),
            status=200,
        )

    return Response(json.dumps({"error": "Marketplace not supported"}), status=400)
