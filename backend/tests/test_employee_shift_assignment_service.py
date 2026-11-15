
import uuid
from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.employee_shift_assignment import get_shift_assignments

from app.models.employee import Employee
from app.schemas.employee_shift_assignment import (
    EmployeeShiftAssignmentCreate,
)
from app.services.employee_shift_assignment import (
    create_shift_assignment,
)


def test_inactive_employee_cannot_be_assigned():
    employee_id = uuid.uuid4()
    shift_id = uuid.uuid4()
    branch_id = uuid.uuid4()

    employee = Employee(
        id=employee_id,
        branch_id=branch_id,
        full_name="Test Inactive Employee",
        role="attendant",
        is_active=False,
    )

    mock_db = MagicMock()
    mock_db.get.return_value = employee

    assignment_data = EmployeeShiftAssignmentCreate(
        employee_id=employee_id,
        shift_id=shift_id,
        shift_date=date(2026, 11, 18),
    )

    with pytest.raises(HTTPException) as error:
        create_shift_assignment(
            db=mock_db,
            assignment_data=assignment_data,
        )

    assert error.value.status_code == 400
    assert error.value.detail == "Employee is inactive"

    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()

from app.models.shift import Shift


def test_employee_and_shift_must_share_branch():
    employee_id = uuid.uuid4()
    shift_id = uuid.uuid4()

    employee_branch_id = uuid.uuid4()
    shift_branch_id = uuid.uuid4()

    employee = Employee(
        id=employee_id,
        branch_id=employee_branch_id,
        full_name="Test Attendant",
        role="attendant",
        is_active=True,
    )

    shift = Shift(
        id=shift_id,
        branch_id=shift_branch_id,
        name="Morning Shift",
        is_active=True,
    )

    mock_db = MagicMock()

    def mock_get(model, record_id):
        if model is Employee:
            return employee
        if model is Shift:
            return shift
        return None

    mock_db.get.side_effect = mock_get

    assignment_data = EmployeeShiftAssignmentCreate(
        employee_id=employee_id,
        shift_id=shift_id,
        shift_date=date(2026, 11, 18),
    )

    with pytest.raises(HTTPException) as error:
        create_shift_assignment(
            db=mock_db,
            assignment_data=assignment_data,
        )

    assert error.value.status_code == 400
    assert error.value.detail == (
        "Employee and shift must belong to the same branch"
    )

    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


def test_inactive_shift_cannot_be_assigned():
    employee_id = uuid.uuid4()
    shift_id = uuid.uuid4()
    branch_id = uuid.uuid4()

    employee = Employee(
        id=employee_id,
        branch_id=branch_id,
        full_name="Test Attendant",
        role="attendant",
        is_active=True,
    )

    shift = Shift(
        id=shift_id,
        branch_id=branch_id,
        name="Inactive Evening Shift",
        is_active=False,
    )

    mock_db = MagicMock()

    def mock_get(model, record_id):
        if model is Employee:
            return employee
        if model is Shift:
            return shift
        return None

    mock_db.get.side_effect = mock_get

    assignment_data = EmployeeShiftAssignmentCreate(
        employee_id=employee_id,
        shift_id=shift_id,
        shift_date=date(2026, 11, 18),
    )

    with pytest.raises(HTTPException) as error:
        create_shift_assignment(
            db=mock_db,
            assignment_data=assignment_data,
        )

    assert error.value.status_code == 400
    assert error.value.detail == "Shift is inactive"

    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()

from app.models.employee_shift_assignment import EmployeeShiftAssignment


def test_duplicate_assignment_rejected_by_service():
    employee_id = uuid.uuid4()
    shift_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    assignment_date = date(2026, 11, 18)

    employee = Employee(
        id=employee_id,
        branch_id=branch_id,
        full_name="Test Attendant",
        role="attendant",
        is_active=True,
    )

    shift = Shift(
        id=shift_id,
        branch_id=branch_id,
        name="Morning Shift",
        is_active=True,
    )

    existing_assignment = EmployeeShiftAssignment(
        id=uuid.uuid4(),
        employee_id=employee_id,
        shift_id=shift_id,
        shift_date=assignment_date,
    )

    mock_db = MagicMock()

    def mock_get(model, record_id):
        if model is Employee:
            return employee
        if model is Shift:
            return shift
        return None

    mock_db.get.side_effect = mock_get
    mock_db.scalar.return_value = existing_assignment

    assignment_data = EmployeeShiftAssignmentCreate(
        employee_id=employee_id,
        shift_id=shift_id,
        shift_date=assignment_date,
    )

    with pytest.raises(HTTPException) as error:
        create_shift_assignment(
            db=mock_db,
            assignment_data=assignment_data,
        )

    assert error.value.status_code == 409
    assert error.value.detail == (
        "Employee already has a shift assignment on this date"
    )

    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


def test_get_shift_assignments_filters_by_branch():
    branch_id = uuid.uuid4()
    mock_db = MagicMock()

    mock_db.scalars.return_value.all.return_value = []

    assignments = get_shift_assignments(
        db=mock_db,
        branch_id=branch_id,
        limit=100,
    )

    assert assignments == []

    mock_db.scalars.assert_called_once()

    statement = mock_db.scalars.call_args.args[0]

    compiled_sql = str(statement.compile())

    assert "employees.branch_id" in compiled_sql
    assert "employee_shift_assignments" in compiled_sql

    assert branch_id in statement.compile().params.values()
