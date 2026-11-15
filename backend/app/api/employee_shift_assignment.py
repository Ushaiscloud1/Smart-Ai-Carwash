
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.employee_shift_assignment import (
    EmployeeShiftAssignmentCreate,
    EmployeeShiftAssignmentResponse,
)
from app.services.employee_shift_assignment import create_shift_assignment


router = APIRouter(
    prefix="/api/shift-assignments",
    tags=["Employee Shift Assignments"],
)


@router.post(
    "/",
    response_model=EmployeeShiftAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_employee_to_shift(
    assignment_data: EmployeeShiftAssignmentCreate,
    db: Session = Depends(get_db),
):
    return create_shift_assignment(
        db=db,
        assignment_data=assignment_data,
    )
