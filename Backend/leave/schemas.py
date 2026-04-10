from pydantic import BaseModel
from datetime import date

class LeaveRequest(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str

class LeaveStatusUpdate(BaseModel):
    status: str  # "approved" or "rejected"