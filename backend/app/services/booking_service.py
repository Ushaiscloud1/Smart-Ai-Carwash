
from datetime import datetime, timedelta

import uuid
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.branch import Branch
from app.models.branch_hours import BranchHours

import uuid

from app.core.database import SessionLocal


from sqlalchemy import func

from app.models.booking import Booking
from app.models.wash_bay import WashBay




BOOKING_WINDOW_DAYS = 14
MINIMUM_NOTICE_MINUTES = 30
BOOKING_INTERVAL_MINUTES = 30


def validate_booking_time(
    scheduled_start: datetime,
    current_time: datetime,
) -> None:
    """
    Validate the requested appointment start time.

    Raises ValueError when a booking violates
    the scheduling policies.
    """

    if (
        scheduled_start.tzinfo is None
        or scheduled_start.utcoffset() is None
        or current_time.tzinfo is None
        or current_time.utcoffset() is None
    ):
        raise ValueError(
            "Booking timestamps must include timezone information."
        )

    minimum_start = current_time + timedelta(
        minutes=MINIMUM_NOTICE_MINUTES
    )

    maximum_start = current_time + timedelta(
        days=BOOKING_WINDOW_DAYS
    )

    if scheduled_start < minimum_start:
        raise ValueError(
            "Bookings require at least 30 minutes notice."
        )

    if scheduled_start > maximum_start:
        raise ValueError(
            "Bookings cannot be made more than 14 days in advance."
        )

    if (
        scheduled_start.minute % BOOKING_INTERVAL_MINUTES != 0
        or scheduled_start.second != 0
        or scheduled_start.microsecond != 0
    ):
        raise ValueError(
            "Bookings must start on a 30-minute interval."
        )

def validate_branch_operating_hours(
    db: Session,
    branch_id: uuid.UUID,
    scheduled_start: datetime,
    scheduled_end: datetime,
) -> None:
    """
    Ensure an appointment fits within branch operating hours.
    """

    if (
        scheduled_start.tzinfo is None
        or scheduled_start.utcoffset() is None
        or scheduled_end.tzinfo is None
        or scheduled_end.utcoffset() is None
    ):
        raise ValueError("Booking timestamps must include timezone information.")

    if scheduled_end <= scheduled_start:
        raise ValueError("Booking end time must be after start time.")

    branch = db.get(Branch, branch_id)

    if branch is None:
        raise ValueError("Branch not found.")

    branch_timezone = ZoneInfo(branch.timezone)

    local_start = scheduled_start.astimezone(branch_timezone)
    local_end = scheduled_end.astimezone(branch_timezone)

    if local_start.date() != local_end.date():
        raise ValueError("Bookings must start and finish on the same day.")

    day_of_week = local_start.weekday()

    hours = (
        db.query(BranchHours)
        .filter(
            BranchHours.branch_id == branch_id,
            BranchHours.day_of_week == day_of_week,
        )
        .one_or_none()
    )

    if hours is None or hours.is_closed:
        raise ValueError("Branch is closed on the selected day.")

    if (
        local_start.time().replace(tzinfo=None) < hours.opening_time
        or local_end.time().replace(tzinfo=None) > hours.closing_time
    ):
        raise ValueError("Booking is outside branch operating hours.")

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


def check_bay_availability(
    db: Session,
    branch_id: uuid.UUID,
    scheduled_start: datetime,
    scheduled_end: datetime,
) -> bool:
    """
    Check bay availability across the requested appointment.
    Includes a 10-minute turnaround buffer.
    """

    if (
        scheduled_start.tzinfo is None
        or scheduled_start.utcoffset() is None
        or scheduled_end.tzinfo is None
        or scheduled_end.utcoffset() is None
    ):
        raise ValueError("Booking timestamps must include timezone information.")

    if scheduled_end <= scheduled_start:
        raise ValueError("Booking end time must be after start time.")

    total_bays = (
        db.query(func.count(WashBay.id))
        .filter(
            WashBay.branch_id == branch_id,
            WashBay.is_active.is_(True),
        )
        .scalar()
    )

    if total_bays == 0:
        return False

    turnaround = timedelta(minutes=10)
    requested_end = scheduled_end + turnaround

    existing_bookings = (
        db.query(Booking)
        .filter(
            Booking.branch_id == branch_id,
            Booking.status.in_([
                "confirmed",
                "checked_in",
                "in_progress",
            ]),
            Booking.scheduled_start < requested_end,
            Booking.scheduled_end + turnaround > scheduled_start,
        )
        .all()
    )

    events = []

    for booking in existing_bookings:
        occupied_start = max(
            booking.scheduled_start,
            scheduled_start,
        )
        occupied_end = min(
            booking.scheduled_end + turnaround,
            requested_end,
        )

        events.append((occupied_start, 1))
        events.append((occupied_end, -1))

    # Process departures before arrivals at identical timestamps.
    events.sort(key=lambda event: (event[0], event[1]))

    occupied_bays = 0

    for _, change in events:
        occupied_bays += change

        if occupied_bays >= total_bays:
            return False

    return True
