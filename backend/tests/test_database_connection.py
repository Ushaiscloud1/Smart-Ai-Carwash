
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.organization import Organization


def test_create_and_read_organization():
    db = SessionLocal()
    slug = "smartwash-ai-test"

    try:
        organization = db.scalar(
            select(Organization).where(Organization.slug == slug)
        )

        if organization is None:
            organization = Organization(
                name="SmartWash AI",
                slug=slug,
            )
            db.add(organization)
            db.commit()

        saved_organization = db.scalar(
            select(Organization).where(Organization.slug == slug)
        )

        assert saved_organization is not None
        assert saved_organization.name == "SmartWash AI"

        print("Organization created and retrieved successfully!")

    finally:
        db.close()
