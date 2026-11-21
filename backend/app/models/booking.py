
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.booking_status import BookingStatus


class Booking(Base):
    __tablename__ = "bookings"

    __table_args__ = (
        CheckConstraint(
            "scheduled_end > scheduled_start",
            name="ck_booking_valid_schedule",
        ),
        
        
        CheckConstraint(
            "total_price >= 0",
            name="ck_booking_price_nonnegative",
        ),
        CheckConstraint(
            "vehicle_type IN ('sedan', 'suv', 'van')",
            name="ck_booking_vehicle_type",
        ),
        
CheckConstraint(
    "status IN ('confirmed', 'checked_in', 'in_progress', "
    "'completed', 'cancelled', 'no_show')",
    name="ck_booking_valid_status",
),

    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id"),
        nullable=False,
        index=True,
    )

    wash_service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wash_services.id"),
        nullable=False,
        index=True,
    )

    customer_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    customer_phone: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    scheduled_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    scheduled_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default=BookingStatus.CONFIRMED.value,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    branch = relationship("Branch")
    wash_service = relationship("WashService")
