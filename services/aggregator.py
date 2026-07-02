from connectors.wildberries import WildberriesConnector
from connectors.ozon import OzonConnector
from core.cache import cache_get, cache_set


def _connector(marketplace: str, api_key: str, **kw):
    match marketplace:
        case "wildberries":   return WildberriesConnector(api_key)
        case "ozon":          return OzonConnector(api_key, **kw)
        case _: raise ValueError(f"Unknown marketplace: {marketplace}")


async def get_expenses(seller_id: str, marketplace: str,
                       period: str, api_key: str, **kw) -> dict:
    key = f"exp:{seller_id}:{marketplace}:{period}"
    if cached := await cache_get(key):
        return cached

    conn = _connector(marketplace, api_key, **kw)
    try:
        data = await conn.get_expenses(seller_id, period)
    finally:
        await conn.close()

    result = dict(seller_id=seller_id, marketplace=marketplace,
                  period=period, currency="RUB", expenses=data)
    await cache_set(key, result)
    return result


async def get_summary(seller_id: str, period: str,
                      credentials: list[dict]) -> dict:
    key = f"summary:{seller_id}:{period}"
    if cached := await cache_get(key):
        return cached

    totals: dict[str, float] = {}
    combined = dict(commission=0.0, logistics=0.0, storage=0.0,
                    fines=0.0, ads=0.0, returns=0.0, other=0.0, total=0.0)

    for creds in credentials:
        mp  = creds["marketplace"]
        conn = _connector(mp, creds["api_key"], **creds)
        try:
            exp = await conn.get_expenses(seller_id, period)
        finally:
            await conn.close()
        totals[mp] = exp.get("total", 0)
        for field in combined:
            combined[field] += exp.get(field, 0)

    result = dict(period=period, marketplaces=list(totals),
                  total_expenses=combined["total"],
                  by_marketplace=totals, by_type=combined)
    await cache_set(key, result)
    return result


async def get_breakdown(seller_id: str, marketplace: str,
                        period: str, api_key: str, **kw) -> dict:
    key = f"bkd:{seller_id}:{marketplace}:{period}"
    if cached := await cache_get(key):
        return cached

    conn = _connector(marketplace, api_key, **kw)
    try:
        items = await conn.get_breakdown(seller_id, period)
    finally:
        await conn.close()

    result = dict(period=period, marketplace=marketplace,
                  items=items, total_skus=len(items))
    await cache_set(key, result)
    return result
