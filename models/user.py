from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from core.database import Base
import bcrypt


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True)
    email      = Column(String(255), unique=True, nullable=False)
    name       = Column(String(255), nullable=False)
    password   = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active  = Column(Boolean, default=True)

    def set_password(self, raw: str):
        self.password = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()

    def check_password(self, raw: str) -> bool:
        return bcrypt.checkpw(raw.encode(), self.password.encode())


class MarketplaceCredential(Base):
    """Хранит API-ключи продавца по каждому маркетплейсу."""
    __tablename__ = "marketplace_credentials"

    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, nullable=False)
    marketplace = Column(String(50), nullable=False)   # wildberries | ozon | yandex_market
    api_key     = Column(Text, nullable=False)
    client_id   = Column(String(255), nullable=True)
    campaign_id = Column(String(255), nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    is_active   = Column(Boolean, default=True)
