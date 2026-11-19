
import pytest
from fastapi import HTTPException

from app.core.dependencies import require_organization_role
from app.core.roles import OrganizationRole
from app.models.organization_membership import OrganizationMembership


def test_staff_cannot_access_owner_operations():
    membership = OrganizationMembership(role="staff")

    with pytest.raises(HTTPException) as error:
        require_organization_role(
            membership,
            {OrganizationRole.OWNER},
        )

    assert error.value.status_code == 403
    assert error.value.detail == (
        "You do not have permission to perform this action"
    )
