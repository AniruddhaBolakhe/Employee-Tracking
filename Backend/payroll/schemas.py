from pydantic import BaseModel

class PayrollRequest(BaseModel):
    employee_id: int
    month: int
    year: int