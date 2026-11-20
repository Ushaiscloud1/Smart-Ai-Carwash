
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.branch import Branch
from app.models.wash_service import WashService
from app.models.wash_service_price import WashServicePrice


BRANCH_ID = uuid.UUID("1b598316-4cfa-42e1-9d76-13c8744b32d7")

SERVICES = [
    {
        "name": "Basic Exterior",
        "duration_minutes": 30,
        "required_attendants": 1,
        "prices": {
            "sedan": 3000,
            "suv": 4000,
            "van": 5000,
        },
    },
    {
        "name": "Standard Wash",
        "duration_minutes": 60,
        "required_attendants": 2,
        "prices": {
            "sedan": 5000,
            "suv": 6500,
            "van": 8000,
        },
    },
    {
        "name": "Premium Wash",
        "duration_minutes": 90,
        "required_attendants": 2,
        "prices": {
            "sedan": 8000,
            "suv": 10000,
            "van": 13000,
        },
    },
    {
        "name": "Deep Cleaning",
        "duration_minutes": 180,
        "required_attendants": 2,
        "prices": {
            "sedan": 20000,
            "suv": 28000,
            "van": 35000,
        },
    },
]


def seed_service_catalogue():
    with SessionLocal() as db:
        with db.begin():
            branch = db.get(Branch, BRANCH_ID)

            if branch is None:
                raise ValueError("SmartWash AI Main Branch not found")

            for item in SERVICES:
                service = db.scalar(
                    select(WashService).where(
                        WashService.branch_id == BRANCH_ID,
                        WashService.name == item["name"],
                    )
                )

                if service is None:
                    service = WashService(
                        branch_id=BRANCH_ID,
                        name=item["name"],
                        duration_minutes=item["duration_minutes"],
                        required_attendants=item["required_attendants"],
                    )
                    db.add(service)
                    db.flush()
                else:
                    service.duration_minutes = item["duration_minutes"]
                    service.required_attendants = item["required_attendants"]

                for vehicle_type, amount in item["prices"].items():
                    price = db.scalar(
                        select(WashServicePrice).where(
                            WashServicePrice.wash_service_id == service.id,
                            WashServicePrice.vehicle_type == vehicle_type,
                        )
                    )

                    if price is None:
                        price = WashServicePrice(
                            wash_service_id=service.id,
                            vehicle_type=vehicle_type,
                            price=Decimal(amount),
                        )
                        db.add(price)
                    else:
                        price.price = Decimal(amount)

            print("Service catalogue seeded successfully!")


if __name__ == "__main__":
    seed_service_catalogue()
