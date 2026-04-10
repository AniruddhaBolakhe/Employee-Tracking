from pydantic import BaseModel

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "employee"
    department: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str