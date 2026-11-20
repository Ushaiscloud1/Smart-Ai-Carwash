
import uuid

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_organization_membership
from app.models.organization_membership import OrganizationMembership
from app.core.dependencies import require_organization_role
from app.core.roles import OrganizationRole


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
    
@router.get("/{organization_id}/owner-access")
def verify_owner_access(
    organization_id: uuid.UUID,
    membership: OrganizationMembership = Depends(
        get_current_organization_membership
    ),
):
    require_organization_role(
        membership=membership,
        allowed_roles={OrganizationRole.OWNER},
    )

    return {
        "organization_id": str(organization_id),
        "role": membership.role,
        "message": "Owner access granted",
    }


@router.get("/{organization_id}/manager-access")
def verify_manager_access(
    organization_id: uuid.UUID,
    membership: OrganizationMembership = Depends(
        get_current_organization_membership
    ),
):
    require_organization_role(
        membership=membership,
        allowed_roles={
            OrganizationRole.OWNER,
            OrganizationRole.MANAGER,
        },
    )

    return {
        "organization_id": str(organization_id),
        "role": membership.role,
        "message": "Manager-level access granted",
    }

@router.get("/{organization_id}/staff-access")
def verify_staff_access(
    organization_id: uuid.UUID,
    membership: OrganizationMembership = Depends(
        get_current_organization_membership
    ),
):
    require_organization_role(
        membership=membership,
        allowed_roles={
            OrganizationRole.OWNER,
            OrganizationRole.MANAGER,
            OrganizationRole.STAFF,
        },
    )

    return {
        "organization_id": str(organization_id),
        "role": membership.role,
        "message": "Staff-level access granted",
    }
