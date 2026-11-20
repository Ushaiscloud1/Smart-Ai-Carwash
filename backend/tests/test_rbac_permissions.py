
import pytest
from fastapi import HTTPException
import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_current_organization_membership

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
def test_staff_cannot_access_owner_endpoint():
    organization_id = uuid.uuid4()

    def override_membership():
        return OrganizationMembership(
            user_id=uuid.uuid4(),
            organization_id=organization_id,
            role="staff",
        )

    app.dependency_overrides[get_current_organization_membership] = (
        override_membership
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/organizations/{organization_id}/owner-access"
            )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "You do not have permission to perform this action"
        }

    finally:
        app.dependency_overrides.pop(
            get_current_organization_membership,
            None,
        )

def test_owner_can_access_owner_endpoint():
    organization_id = uuid.uuid4()

    def override_membership():
        return OrganizationMembership(
            user_id=uuid.uuid4(),
            organization_id=organization_id,
            role="owner",
        )

    app.dependency_overrides[get_current_organization_membership] = (
        override_membership
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/organizations/{organization_id}/owner-access"
            )

        assert response.status_code == 200
        assert response.json() == {
            "organization_id": str(organization_id),
            "role": "owner",
            "message": "Owner access granted",
        }

    finally:
        app.dependency_overrides.pop(
            get_current_organization_membership,
            None,
        )

def test_unauthenticated_user_cannot_access_owner_endpoint():
    organization_id = uuid.uuid4()

    with TestClient(app) as client:
        response = client.get(
            f"/api/organizations/{organization_id}/owner-access"
        )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication required"
    }

def test_owner_can_access_manager_endpoint():
    organization_id = uuid.uuid4()

    def override_membership():
        return OrganizationMembership(
            user_id=uuid.uuid4(),
            organization_id=organization_id,
            role="owner",
        )

    app.dependency_overrides[get_current_organization_membership] = (
        override_membership
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/organizations/{organization_id}/manager-access"
            )

        assert response.status_code == 200
        assert response.json() == {
            "organization_id": str(organization_id),
            "role": "owner",
            "message": "Manager-level access granted",
        }

    finally:
        app.dependency_overrides.pop(
            get_current_organization_membership,
            None,
        )

def test_manager_can_access_manager_endpoint():
    organization_id = uuid.uuid4()

    def override_membership():
        return OrganizationMembership(
            user_id=uuid.uuid4(),
            organization_id=organization_id,
            role="manager",
        )

    app.dependency_overrides[get_current_organization_membership] = (
        override_membership
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/organizations/{organization_id}/manager-access"
            )

        assert response.status_code == 200
        assert response.json() == {
            "organization_id": str(organization_id),
            "role": "manager",
            "message": "Manager-level access granted",
        }

    finally:
        app.dependency_overrides.pop(
            get_current_organization_membership,
            None,
        )

def test_staff_cannot_access_manager_endpoint():
    organization_id = uuid.uuid4()

    def override_membership():
        return OrganizationMembership(
            user_id=uuid.uuid4(),
            organization_id=organization_id,
            role="staff",
        )

    app.dependency_overrides[get_current_organization_membership] = (
        override_membership
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/organizations/{organization_id}/manager-access"
            )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "You do not have permission to perform this action"
        }

    finally:
        app.dependency_overrides.pop(
            get_current_organization_membership,
            None,
        )

def test_manager_cannot_access_owner_endpoint():
    organization_id = uuid.uuid4()

    def override_membership():
        return OrganizationMembership(
            user_id=uuid.uuid4(),
            organization_id=organization_id,
            role="manager",
        )

    app.dependency_overrides[get_current_organization_membership] = (
        override_membership
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/organizations/{organization_id}/owner-access"
            )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "You do not have permission to perform this action"
        }

    finally:
        app.dependency_overrides.pop(
            get_current_organization_membership,
            None,
        )

def test_staff_can_access_staff_endpoint():
    organization_id = uuid.uuid4()

    def override_membership():
        return OrganizationMembership(
            user_id=uuid.uuid4(),
            organization_id=organization_id,
            role="staff",
        )

    app.dependency_overrides[get_current_organization_membership] = (
        override_membership
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/organizations/{organization_id}/staff-access"
            )

        assert response.status_code == 200
        assert response.json() == {
            "organization_id": str(organization_id),
            "role": "staff",
            "message": "Staff-level access granted",
        }

    finally:
        app.dependency_overrides.pop(
            get_current_organization_membership,
            None,
        )

def test_manager_can_access_staff_endpoint():
    organization_id = uuid.uuid4()

    def override_membership():
        return OrganizationMembership(
            user_id=uuid.uuid4(),
            organization_id=organization_id,
            role="manager",
        )

    app.dependency_overrides[get_current_organization_membership] = (
        override_membership
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/organizations/{organization_id}/staff-access"
            )

        assert response.status_code == 200
        assert response.json() == {
            "organization_id": str(organization_id),
            "role": "manager",
            "message": "Staff-level access granted",
        }

    finally:
        app.dependency_overrides.pop(
            get_current_organization_membership,
            None,
        )

def test_owner_can_access_staff_endpoint():
    organization_id = uuid.uuid4()

    def override_membership():
        return OrganizationMembership(
            user_id=uuid.uuid4(),
            organization_id=organization_id,
            role="owner",
        )

    app.dependency_overrides[get_current_organization_membership] = (
        override_membership
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/organizations/{organization_id}/staff-access"
            )

        assert response.status_code == 200
        assert response.json() == {
            "organization_id": str(organization_id),
            "role": "owner",
            "message": "Staff-level access granted",
        }

    finally:
        app.dependency_overrides.pop(
            get_current_organization_membership,
            None,
        )

def test_unauthenticated_user_cannot_access_manager_endpoint():
    organization_id = uuid.uuid4()

    with TestClient(app) as client:
        response = client.get(
            f"/api/organizations/{organization_id}/manager-access"
        )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication required"
    }

def test_unauthenticated_user_cannot_access_staff_endpoint():
    organization_id = uuid.uuid4()

    with TestClient(app) as client:
        response = client.get(
            f"/api/organizations/{organization_id}/staff-access"
        )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication required"
    }
