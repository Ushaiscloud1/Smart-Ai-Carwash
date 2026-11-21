
from datetime import datetime, timedelta, timezone

import pytest

import uuid

from app.core.database import SessionLocal
from app.services.booking_service import validate_branch_operating_hours

from app.services.booking_service import check_bay_availability

from decimal import Decimal

from app.models.booking import Booking

from app.services.booking_service import validate_booking_time

# Fixed reference time: 20 November 2026, 10:00 AM Nigeria time
NIGERIA_TZ = timezone(timedelta(hours=1))
CURRENT_TIME = datetime(2026, 11, 20, 10, 0, tzinfo=NIGERIA_TZ)


def test_reject_booking_with_less_than_30_minutes_notice():
    scheduled_start = CURRENT_TIME + timedelta(minutes=15)

    with pytest.raises(ValueError, match="at least 30 minutes"):
        validate_booking_time(scheduled_start, CURRENT_TIME)


def test_accept_booking_with_exactly_30_minutes_notice():
    scheduled_start = CURRENT_TIME + timedelta(minutes=30)

    validate_booking_time(scheduled_start, CURRENT_TIME)


def test_reject_booking_more_than_14_days_ahead():
    scheduled_start = CURRENT_TIME + timedelta(days=20)

    with pytest.raises(ValueError, match="more than 14 days"):
        validate_booking_time(scheduled_start, CURRENT_TIME)


def test_reject_booking_outside_30_minute_interval():
    scheduled_start = CURRENT_TIME + timedelta(minutes=80)

    with pytest.raises(ValueError, match="30-minute interval"):
        validate_booking_time(scheduled_start, CURRENT_TIME)


def test_accept_booking_on_valid_interval():
    scheduled_start = CURRENT_TIME + timedelta(minutes=90)

    validate_booking_time(scheduled_start, CURRENT_TIME)


def test_reject_booking_without_timezone():
    scheduled_start = datetime(2026, 11, 20, 11, 0)

    with pytest.raises(ValueError, match="timezone information"):
        validate_booking_time(scheduled_start, CURRENT_TIME)

def test_reject_sunday_booking():
    branch_id = uuid.UUID(
        "1b598316-4cfa-42e1-9d76-13c8744b32d7"
    )

    # Sunday, 22 November 2026
    scheduled_start = datetime(
        2026, 11, 22, 10, 0, tzinfo=NIGERIA_TZ
    )

    scheduled_end = scheduled_start + timedelta(minutes=60)

    with SessionLocal() as db:
        with pytest.raises(
            ValueError,
            match="Branch is closed",
        ):
            validate_branch_operating_hours(
                db,
                branch_id,
                scheduled_start,
                scheduled_end,
            )

def test_accept_weekday_booking():
    branch_id = uuid.UUID(
        "1b598316-4cfa-42e1-9d76-13c8744b32d7"
    )

    scheduled_start = datetime(
        2026, 11, 23, 10, 0, tzinfo=NIGERIA_TZ
    )

    scheduled_end = scheduled_start + timedelta(minutes=60)

    with SessionLocal() as db:
        validate_branch_operating_hours(
            db,
            branch_id,
            scheduled_start,
            scheduled_end,
        )

def test_reject_booking_after_closing_time():
    branch_id = uuid.UUID(
        "1b598316-4cfa-42e1-9d76-13c8744b32d7"
    )

    # Monday, 23 November 2026
    scheduled_start = datetime(
        2026, 11, 23, 22, 30, tzinfo=NIGERIA_TZ
    )

    scheduled_end = scheduled_start + timedelta(minutes=60)

    with SessionLocal() as db:
        with pytest.raises(
            ValueError,
            match="outside branch operating hours",
        ):
            validate_branch_operating_hours(
                db,
                branch_id,
                scheduled_start,
                scheduled_end,
            )

def test_bay_available_when_no_bookings_exist():
    branch_id = uuid.UUID(
        "1b598316-4cfa-42e1-9d76-13c8744b32d7"
    )

    scheduled_start = datetime(
        2026, 11, 23, 10, 0, tzinfo=NIGERIA_TZ
    )

    scheduled_end = scheduled_start + timedelta(minutes=60)

    with SessionLocal() as db:
        is_available = check_bay_availability(
            db,
            branch_id,
            scheduled_start,
            scheduled_end,
        )

    assert is_available is True

def test_reject_booking_when_all_bays_occupied():
    branch_id = uuid.UUID(
        "1b598316-4cfa-42e1-9d76-13c8744b32d7"
    )

    service_id = uuid.UUID(
        "9417f7e2-3beb-4cff-9379-1300402aab36"
    )

    scheduled_start = datetime(
        2026, 11, 23, 10, 0, tzinfo=NIGERIA_TZ
    )
    scheduled_end = scheduled_start + timedelta(minutes=60)

    with SessionLocal() as db:
        try:
            for number in range(5):
                booking = Booking(
                    branch_id=branch_id,
                    wash_service_id=service_id,
                    customer_name=f"Test Customer {number + 1}",
                    customer_phone=f"0800000000{number}",
                    vehicle_type="sedan",
                    scheduled_start=scheduled_start,
                    scheduled_end=scheduled_end,
                    total_price=Decimal("5000.00"),
                    status="confirmed",
                )
                db.add(booking)

            db.flush()

            is_available = check_bay_availability(
                db,
                branch_id,
                scheduled_start,
                scheduled_end,
            )

            assert is_available is False

        finally:
            db.rollback()

def test_bay_available_with_staggered_bookings():
    branch_id = uuid.UUID(
        "1b598316-4cfa-42e1-9d76-13c8744b32d7"
    )

    service_id = uuid.UUID(
        "9417f7e2-3beb-4cff-9379-1300402aab36"
    )

    base_time = datetime(
        2026, 11, 23, 10, 0, tzinfo=NIGERIA_TZ
    )

    with SessionLocal() as db:
        try:
            appointment_times = [
                (base_time, base_time + timedelta(hours=1)),
                (
                    base_time + timedelta(minutes=90),
                    base_time + timedelta(minutes=150),
                ),
            ]

            for number, (start, end) in enumerate(appointment_times):
                db.add(
                    Booking(
                        branch_id=branch_id,
                        wash_service_id=service_id,
                        customer_name=f"Staggered Customer {number + 1}",
                        customer_phone=f"0800000010{number}",
                        vehicle_type="sedan",
                        scheduled_start=start,
                        scheduled_end=end,
                        total_price=Decimal("5000.00"),
                        status="confirmed",
                    )
                )

            db.flush()

            is_available = check_bay_availability(
                db,
                branch_id,
                base_time,
                base_time + timedelta(hours=2),
            )

            assert is_available is True

        finally:
            db.rollback()
