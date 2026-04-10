from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from auth.utils import get_current_user
from db import get_connection

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/mark", status_code=201)
def mark_attendance(current_user: dict = Depends(get_current_user)):
    employee_id = int(current_user["sub"])
    now = datetime.now()
    today = now.date()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM attendance WHERE employee_id = %s AND date = %s",
        (employee_id, today)
    )
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Attendance already marked for today")

    cursor.execute(
        "INSERT INTO attendance (employee_id, date, check_in, status) VALUES (%s, %s, %s, %s)",
        (employee_id, today, now, "present")
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "Attendance marked successfully",
        "employee_id": employee_id,
        "check_in": now,
        "date": today
    }