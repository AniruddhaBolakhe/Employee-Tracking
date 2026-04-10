from fastapi import APIRouter, HTTPException
from .schemas import LoginRequest, TokenResponse, SignupRequest
from .utils import verify_password, create_token, hash_password
from db import get_connection

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", status_code=201)
def signup(data: SignupRequest):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM employees WHERE email = %s", (data.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(data.password)
    cursor.execute(
        "INSERT INTO employees (name, email, password_hash, role, department) VALUES (%s, %s, %s, %s, %s)",
        (data.name, data.email, hashed, data.role, data.department)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Employee registered successfully"}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees WHERE email = %s", (data.email,))
    employee = cursor.fetchone()
    cursor.close()
    conn.close()

    if not employee or not verify_password(data.password, employee["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"sub": str(employee["id"]), "role": employee["role"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": employee["role"],
        "name": employee["name"]
    }