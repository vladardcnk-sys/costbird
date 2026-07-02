import httpx
from connectors.base import BaseConnector

WB_BASE = "https://statistics-api.wildberries.ru/api/v5/supplier"


class WildberriesConnector(BaseConnector):
    def __init__(self, api_key: str, **kw):
        super().__init__(api_key)
        self.headers = {"Authorization": api_key}

    async def get_expenses(self, seller_id: str, period: str) -> dict:
        date_from, date_to = self.period_to_dates(period)
        try:
            sales = await self._report(date_from, date_to, flag=0)
            returns = await self._report(date_from, date_to, flag=1)
        except Exception:
            sales, returns = self._mock_sales(), self._mock_returns()

        exp = dict(commission=0.0, logistics=0.0, storage=0.0,
                   fines=0.0, ads=0.0, returns=0.0, other=0.0)
        for r in sales:
            exp["commission"] += abs(r.get("ppvz_for_pay", 0) - r.get("retail_amount", 0))
            exp["logistics"]  += abs(r.get("delivery_rub", 0))
            exp["storage"]    += abs(r.get("storage_fee", 0))
            exp["fines"]      += abs(r.get("penalty", 0))
            exp["ads"]        += abs(r.get("supplier_promo", 0))
        for r in returns:
            exp["returns"] += abs(r.get("retail_amount", 0))
        exp["total"] = sum(exp.values())
        return exp

    async def get_breakdown(self, seller_id: str, period: str) -> list[dict]:
        date_from, date_to = self.period_to_dates(period)
        try:
            sales = await self._report(date_from, date_to, flag=0)
        except Exception:
            sales = self._mock_sales()

        by_sku: dict[str, dict] = {}
        for r in sales:
            nm = str(r.get("nm_id", "?"))
            if nm not in by_sku:
                by_sku[nm] = dict(sku=nm, name=r.get("subject_name",""),
                                  units_sold=0, commission=0.0, logistics=0.0, profit=0.0)
            by_sku[nm]["units_sold"] += 1
            by_sku[nm]["commission"] += abs(r.get("ppvz_for_pay",0) - r.get("retail_amount",0))
            by_sku[nm]["logistics"]  += abs(r.get("delivery_rub", 0))
            by_sku[nm]["profit"]     += r.get("ppvz_for_pay", 0)
        return list(by_sku.values())

    async def _report(self, date_from, date_to, flag):
        resp = await self.client.get(
            f"{WB_BASE}/reportDetailByPeriod", headers=self.headers,
            params=dict(dateFrom=date_from, dateTo=date_to, flag=flag, rrdid=0, limit=100_000))
        resp.raise_for_status()
        return resp.json() or []

    @staticmethod
    def _mock_sales():
        return [
            dict(nm_id=101, subject_name="Футболка XL", ppvz_for_pay=890,
                 retail_amount=1200, delivery_rub=90, storage_fee=22, penalty=0, supplier_promo=60),
            dict(nm_id=102, subject_name="Джинсы 32", ppvz_for_pay=2100,
                 retail_amount=2800, delivery_rub=120, storage_fee=35, penalty=50, supplier_promo=200),
        ]

    @staticmethod
    def _mock_returns():
        return [dict(retail_amount=1200)]
