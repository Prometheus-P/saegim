from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from src.core.database import Base


class ShortLink(Base):
    """Short link mapping for SMS/Alimtalk.

    We intentionally store only:
      - code (public)
      - target_token (existing QR token, already random & non-PII)

    Final destination is computed as: {WEB_BASE_URL}{target_path}/{target_token}
    (v1 uses target_path='/p')
    """

    __tablename__ = "short_links"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(String(12), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False, index=True)

    target_token = Column(String(32), nullable=False)
    target_path = Column(String(255), nullable=False, default="/p")

    click_count = Column(Integer, nullable=False, default=0)
    last_clicked_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order")
