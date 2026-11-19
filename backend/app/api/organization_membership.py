
import uuid

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_organization_membership
from app.models.organization_membership import OrganizationMembership


router = APIRouter(
    prefix="/api/organizations",
    tags=["Organization Memberships"],
)


@router.get("/{organization_id}/my-membership")
def get_my_organization_membership(
    organization_id: uuid.UUID,
    membership: OrganizationMembership = Depends(
        get_current_organization_membership
    ),
):
    return {
        "organization_id": str(membership.organization_id),
        "user_id": str(membership.user_id),
        "role": membership.role,
    }
