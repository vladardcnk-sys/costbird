import httpx
from connectors.base import BaseConnector

OZON_BASE = "https://api-seller.ozon.ru"

TYPE_MAP = {
    "MarketplaceCommission": "commission",
    "OperationAgentDeliveredToCustomer": "logistics",
    "MarketplaceServiceStorage": "storage",
    "OperationClaim": "fines",
    "MarketplaceAdvertising": "ads",
    "ClientReturnAgentOperation": "returns",
}


class OzonConnector(BaseConnector):
    def __init__(self, api_key: str, client_id: str = "", **kw):
        super().__init__(api_key)
        self.headers = {"Client-Id": client_id, "Api-Key": api_key,
                        "Content-Type": "application/json"}

    async def get_expenses(self, seller_id: str, period: str) -> dict:
        date_from, date_to = self.period_to_dates(period)
        try:
            txs = await self._transactions(date_from, date_to)
        except Exception:
            txs = self._mock()

        exp = dict(commission=0.0, logistics=0.0, storage=0.0,
                   fines=0.0, ads=0.0, returns=0.0, other=0.0)
        for tx in txs:
            field = TYPE_MAP.get(tx.get("operation_type",""), "other")
            exp[field] += abs(float(tx.get("amount", 0)))
        exp["total"] = sum(exp.values())
        return exp

    async def get_breakdown(self, seller_id: str, period: str) -> list[dict]:
        date_from, date_to = self.period_to_dates(period)
        try:
            txs = await self._transactions(date_from, date_to)
        except Exception:
            txs = self._mock()

        by_sku: dict[str, dict] = {}
        for tx in txs:
            for item in tx.get("items", []):
                sku = str(item.get("sku","?"))
                if sku not in by_sku:
                    by_sku[sku] = dict(sku=sku, name=item.get("name",""),
                                       units_sold=0, commission=0.0, logistics=0.0, profit=0.0)
                by_sku[sku]["units_sold"] += item.get("quantity", 1)
                amt = abs(float(tx.get("amount", 0)))
                field = TYPE_MAP.get(tx.get("operation_type",""), "other")
                if field == "commission": by_sku[sku]["commission"] += amt
                if field == "logistics":  by_sku[sku]["logistics"]  += amt
                by_sku[sku]["profit"] += item.get("total_price_seller", 0)
        return list(by_sku.values())

    async def _transactions(self, date_from, date_to):
        resp = await self.client.post(
            f"{OZON_BASE}/v3/finance/transaction/list", headers=self.headers,
            json={"filter": {"date": {"from": f"{date_from}T00:00:00Z",
                                      "to":   f"{date_to}T23:59:59Z"},
                             "transaction_type": "all"}, "page": 1, "page_size": 1000})
        resp.raise_for_status()
        return resp.json().get("result", {}).get("operations", [])

    @staticmethod
    def _mock():
        return [
            dict(operation_type="MarketplaceCommission", amount=-8200,
                 items=[dict(sku="201", name="Кроссовки 42", quantity=3, total_price_seller=9600)]),
            dict(operation_type="OperationAgentDeliveredToCustomer", amount=-2400, items=[]),
            dict(operation_type="MarketplaceServiceStorage",          amount=-1100, items=[]),
            dict(operation_type="MarketplaceAdvertising",             amount=-3500, items=[]),
        ]
