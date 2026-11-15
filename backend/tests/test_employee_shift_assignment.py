
import uuid
from datetime import date, datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.employee_shift_assignment import EmployeeShiftAssignment


client = TestClient(app)


def test_create_shift_assignment_success():
    employee_id = uuid.uuid4()
    shift_id = uuid.uuid4()
    assignment_id = uuid.uuid4()

    mock_assignment = EmployeeShiftAssignment(
        id=assignment_id,
        employee_id=employee_id,
        shift_id=shift_id,
        shift_date=date(2026, 11, 17),
        created_at=datetime.now(timezone.utc),
    )

    with patch(
        "app.api.employee_shift_assignment.create_shift_assignment",
        return_value=mock_assignment,
    ):
        response = client.post(
            "/api/shift-assignments/",
            json={
                "employee_id": str(employee_id),
                "shift_id": str(shift_id),
                "shift_date": "2026-11-17",
            },
        )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["employee_id"] == str(employee_id)
    assert response_data["shift_id"] == str(shift_id)
    assert response_data["shift_date"] == "2026-11-17"

from fastapi import HTTPException


def test_duplicate_shift_assignment():
    employee_id = uuid.uuid4()
    shift_id = uuid.uuid4()

    with patch(
        "app.api.employee_shift_assignment.create_shift_assignment",
        side_effect=HTTPException(
            status_code=409,
            detail="Employee already has a shift assignment on this date",
        ),
    ):
        response = client.post(
            "/api/shift-assignments/",
            json={
                "employee_id": str(employee_id),
                "shift_id": str(shift_id),
                "shift_date": "2026-11-17",
            },
        )

    assert response.status_code == 409

    assert response.json() == {
        "detail": "Employee already has a shift assignment on this date"
    }
    

def test_employee_not_found():
    employee_id = uuid.uuid4()
    shift_id = uuid.uuid4()

    with patch(
        "app.api.employee_shift_assignment.create_shift_assignment",
        side_effect=HTTPException(
            status_code=404,
            detail="Employee not found",
        ),
    ):
        response = client.post(
            "/api/shift-assignments/",
            json={
                "employee_id": str(employee_id),
                "shift_id": str(shift_id),
                "shift_date": "2026-11-17",
            },
        )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Employee not found"
    }



def get_shift_assignments(
    db: Session,
    branch_id: uuid.UUID,
    limit: int = 100,
) -> list[EmployeeShiftAssignment]:
    """
    Retrieve shift assignments for a specific branch.
    """

    statement = (
        select(EmployeeShiftAssignment)
        .join(
            Employee,
            EmployeeShiftAssignment.employee_id == Employee.id,
        )
        .where(Employee.branch_id == branch_id)
        .order_by(
            EmployeeShiftAssignment.shift_date,
            EmployeeShiftAssignment.created_at,
        )
        .limit(limit)
    )

    assignments = db.scalars(statement).all()

    return list(assignments)
