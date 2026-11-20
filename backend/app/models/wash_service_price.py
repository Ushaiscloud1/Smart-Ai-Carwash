
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WashServicePrice(Base):
    __tablename__ = "wash_service_prices"

    __table_args__ = (
        UniqueConstraint(
            "wash_service_id",
            "vehicle_type",
            name="uq_service_vehicle_type",
        ),
        CheckConstraint(
            "price >= 0",
            name="ck_wash_service_price_nonnegative",
        ),
        CheckConstraint(
            "vehicle_type IN ('sedan', 'suv', 'van')",
            name="ck_wash_service_vehicle_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    wash_service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wash_services.id"),
        nullable=False,
        index=True,
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    wash_service = relationship("WashService")
