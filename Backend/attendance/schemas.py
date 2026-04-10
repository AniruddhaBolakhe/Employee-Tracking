from pydantic import BaseModel
from datetime import datetime, date

class AttendanceResponse(BaseModel):
    message: str
    employee_id: int
    check_in: datetime
    date: date