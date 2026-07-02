from abc import ABC, abstractmethod
from calendar import monthrange
import httpx


class BaseConnector(ABC):
    def __init__(self, api_key: str, **kw):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        await self.client.aclose()

    @abstractmethod
    async def get_expenses(self, seller_id: str, period: str) -> dict: ...

    @abstractmethod
    async def get_breakdown(self, seller_id: str, period: str) -> list[dict]: ...

    def period_to_dates(self, period: str) -> tuple[str, str]:
        y, m = map(int, period.split("-"))
        last = monthrange(y, m)[1]
        return f"{period}-01", f"{period}-{last:02d}"
