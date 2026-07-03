from flask import Blueprint, jsonify, request
from core.auth import login_required, current_user_id
from core.database import SessionLocal
from models.user import MarketplaceCredential
import httpx
from datetime import datetime, timedelta

wb_api = Blueprint("wb_api", __name__, url_prefix="/cabinet/api")

def get_wb_token(user_id):
    db = SessionLocal()
    try:
        cred = db.query(MarketplaceCredential).filter_by(
            user_id=user_id, marketplace="wildberries", is_active=True).first()
        return cred.api_key if cred else None
    finally:
        db.close()

@wb_api.get("/wb-expenses")
@login_required
def wb_expenses():
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    if not date_from or not date_to:
        today = datetime.today()
        date_from = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        date_to = today.strftime("%Y-%m-%d")

    token = get_wb_token(current_user_id())
    if not token:
        return jsonify({"error": "Wildberries не подключён"}), 400

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.get(
                "https://statistics-api.wildberries.ru/api/v5/supplier/reportDetailByPeriod",
                headers={"Authorization": token},
                params={"dateFrom": date_from, "dateTo": date_to, "flag": 0, "rrdid": 0, "limit": 100000},
            )
            if resp.status_code == 401:
                return jsonify({"error": "Неверный API-ключ WB"}), 400
            sales = resp.json() or []

            resp2 = client.get(
                "https://statistics-api.wildberries.ru/api/v5/supplier/reportDetailByPeriod",
                headers={"Authorization": token},
                params={"dateFrom": date_from, "dateTo": date_to, "flag": 1, "rrdid": 0, "limit": 100000},
            )
            returns = resp2.json() or []
    except Exception as e:
        return jsonify({"error": f"Ошибка соединения: {str(e)}"}), 500

    totals = dict(revenue=0.0, payout=0.0, commission=0.0, logistics=0.0,
                  storage=0.0, fines=0.0, ads=0.0, returns_sum=0.0, orders=0, return_count=0)
    by_day = {}

    for r in sales:
        retail = abs(float(r.get("retail_amount") or 0))
        ppvz = float(r.get("ppvz_for_pay") or 0)
        totals["revenue"] += retail
        totals["payout"] += ppvz
        totals["commission"] += max(retail - ppvz, 0)
        totals["logistics"] += abs(float(r.get("delivery_rub") or 0))
        totals["storage"] += abs(float(r.get("storage_fee") or 0))
        totals["fines"] += abs(float(r.get("penalty") or 0))
        totals["ads"] += abs(float(r.get("supplier_promo") or 0))
        totals["orders"] += 1
        day = (r.get("sale_dt") or r.get("order_dt") or "")[:10]
        if day:
            if day not in by_day:
                by_day[day] = {"revenue": 0.0, "expenses": 0.0}
            by_day[day]["revenue"] += retail
            by_day[day]["expenses"] += abs(float(r.get("delivery_rub") or 0))

    for r in returns:
        totals["returns_sum"] += abs(float(r.get("retail_amount") or 0))
        totals["return_count"] += 1

    totals["total_expenses"] = sum([totals["commission"], totals["logistics"],
                                    totals["storage"], totals["fines"], totals["ads"], totals["returns_sum"]])
    for k in totals:
        if isinstance(totals[k], float):
            totals[k] = round(totals[k], 2)

    sorted_days = sorted(by_day.keys())
    return jsonify({
        "period": {"from": date_from, "to": date_to},
        "totals": totals,
        "by_day": {
            "labels": sorted_days,
            "revenue": [round(by_day[d]["revenue"], 2) for d in sorted_days],
            "expenses": [round(by_day[d]["expenses"], 2) for d in sorted_days],
        }
    })
