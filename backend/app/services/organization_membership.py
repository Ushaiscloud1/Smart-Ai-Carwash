
import uuid

from sqlalchemy.orm import Session

from app.core.roles import OrganizationRole
from app.models.organization_membership import OrganizationMembership



def get_organization_membership(
    db: Session,
    user_id: uuid.UUID,
    organization_id: uuid.UUID,
) -> OrganizationMembership | None:
    return (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.organization_id == organization_id,
        )
        .first()
    )

def create_organization_membership(
    db: Session,
    user_id: uuid.UUID,
    organization_id: uuid.UUID,
    role: OrganizationRole,
) -> OrganizationMembership:
    if not isinstance(role, OrganizationRole):
        raise ValueError("Invalid organization role")

    existing_membership = get_organization_membership(
        db=db,
        user_id=user_id,
        organization_id=organization_id,
    )

    if existing_membership is not None:
        raise ValueError("User already belongs to this organization")

    membership = OrganizationMembership(
        user_id=user_id,
        organization_id=organization_id,
        role=role.value,
    )

    db.add(membership)
    db.flush()

    return membership
