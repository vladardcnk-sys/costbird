from flask import Blueprint, request, jsonify
from services import aggregator as svc

api = Blueprint("api", __name__, url_prefix="/v1")

MARKETPLACES = {"wildberries", "ozon", "yandex_market"}

# --- mock credentials (в проде — тянуть из БД по seller_id) ---
def _creds(marketplace: str) -> dict:
    return dict(marketplace=marketplace, api_key="mock_key",
                client_id="mock_client", campaign_id="mock_campaign")


def _validate_period(period: str) -> bool:
    try:
        y, m = period.split("-")
        return len(y) == 4 and 1 <= int(m) <= 12
    except Exception:
        return False


@api.get("/expenses/<seller_id>")
async def expenses(seller_id: str):
    mp     = request.args.get("marketplace", "")
    period = request.args.get("period", "")

    if mp not in MARKETPLACES:
        return jsonify(error=f"marketplace должен быть одним из: {MARKETPLACES}"), 400
    if not _validate_period(period):
        return jsonify(error="period должен быть в формате YYYY-MM"), 400

    try:
        data = await svc.get_expenses(seller_id, mp, period, **_creds(mp))
        return jsonify(data)
    except Exception as e:
        return jsonify(error=str(e)), 502


@api.get("/expenses/<seller_id>/summary")
async def summary(seller_id: str):
    period = request.args.get("period", "")
    mps    = request.args.getlist("marketplaces") or ["wildberries", "ozon"]

    if not _validate_period(period):
        return jsonify(error="period должен быть в формате YYYY-MM"), 400

    try:
        credentials = [_creds(mp) for mp in mps if mp in MARKETPLACES]
        data = await svc.get_summary(seller_id, period, credentials)
        return jsonify(data)
    except Exception as e:
        return jsonify(error=str(e)), 502


@api.get("/expenses/<seller_id>/breakdown")
async def breakdown(seller_id: str):
    mp     = request.args.get("marketplace", "")
    period = request.args.get("period", "")

    if mp not in MARKETPLACES:
        return jsonify(error=f"marketplace должен быть одним из: {MARKETPLACES}"), 400
    if not _validate_period(period):
        return jsonify(error="period должен быть в формате YYYY-MM"), 400

    try:
        data = await svc.get_breakdown(seller_id, mp, period, **_creds(mp))
        return jsonify(data)
    except Exception as e:
        return jsonify(error=str(e)), 502
