
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EmployeeShiftAssignmentCreate(BaseModel):
    employee_id: uuid.UUID
    shift_id: uuid.UUID
    shift_date: date


class EmployeeShiftAssignmentResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    shift_id: uuid.UUID
    shift_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
