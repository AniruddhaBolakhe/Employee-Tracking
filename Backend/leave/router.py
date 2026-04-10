from fastapi import APIRouter, HTTPException, Depends
from auth.utils import get_current_user
from db import get_connection
from .schemas import LeaveRequest, LeaveStatusUpdate

router = APIRouter(prefix="/leave", tags=["Leave"])

@router.post("/apply", status_code=201)
def apply_leave(data: LeaveRequest, current_user: dict = Depends(get_current_user)):
    employee_id = int(current_user["sub"])

    if data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """INSERT INTO leaves (employee_id, leave_type, start_date, end_date, reason)
           VALUES (%s, %s, %s, %s, %s)""",
        (employee_id, data.leave_type, data.start_date, data.end_date, data.reason)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "Leave applied successfully",
        "employee_id": employee_id,
        "leave_type": data.leave_type,
        "start_date": data.start_date,
        "end_date": data.end_date,
        "status": "pending"
    }

@router.get("/my-leaves")
def my_leaves(current_user: dict = Depends(get_current_user)):
    employee_id = int(current_user["sub"])

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM leaves WHERE employee_id = %s ORDER BY applied_at DESC",
        (employee_id,)
    )
    leaves = cursor.fetchall()
    cursor.close()
    conn.close()

    return leaves

@router.get("/all-leaves")
def all_leaves(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("manager", "hr", "admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """SELECT l.*, e.name, e.department 
           FROM leaves l 
           JOIN employees e ON l.employee_id = e.id 
           ORDER BY l.applied_at DESC"""
    )
    leaves = cursor.fetchall()
    cursor.close()
    conn.close()

    return leaves

@router.put("/{leave_id}/status")
def update_leave_status(leave_id: int, data: LeaveStatusUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("manager", "hr", "admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    if data.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM leaves WHERE id = %s", (leave_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Leave request not found")

    cursor.execute(
        "UPDATE leaves SET status = %s WHERE id = %s",
        (data.status, leave_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": f"Leave {data.status} successfully",
        "leave_id": leave_id,
        "status": data.status
    }