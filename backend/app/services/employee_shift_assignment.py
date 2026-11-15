
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.shift import Shift
from app.models.employee_shift_assignment import EmployeeShiftAssignment
from app.schemas.employee_shift_assignment import EmployeeShiftAssignmentCreate


def create_shift_assignment(
    db: Session,
    assignment_data: EmployeeShiftAssignmentCreate,
) -> EmployeeShiftAssignment:

    # Step 1: Find the employee
    employee = db.get(Employee, assignment_data.employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee is inactive",
        )

    # Step 2: Find the shift
    shift = db.get(Shift, assignment_data.shift_id)

    if shift is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found",
        )

    if not shift.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shift is inactive",
        )

    # Step 3: Check that employee and shift belong
    # to the same branch
    if employee.branch_id != shift.branch_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee and shift must belong to the same branch",
        )

    # Step 4: Prevent duplicate daily assignments
    existing_assignment = db.scalar(
        select(EmployeeShiftAssignment).where(
            EmployeeShiftAssignment.employee_id == employee.id,
            EmployeeShiftAssignment.shift_date == assignment_data.shift_date,
        )
    )

    if existing_assignment is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee already has a shift assignment on this date",
        )

    # Step 5: Create the assignment
    new_assignment = EmployeeShiftAssignment(
        id=uuid.uuid4(),
        employee_id=employee.id,
        shift_id=shift.id,
        shift_date=assignment_data.shift_date,
    )

    db.add(new_assignment)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shift assignment conflicts with an existing record",
        )

    db.refresh(new_assignment)

    return new_assignment
