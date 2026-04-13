from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router
from attendance.router import router as attendance_router
from leave.router import router as leave_router
from payroll.router import router as payroll_router
from reports.router import router as reports_router
from db import setup_database

app = FastAPI(title="HRMS API")

# Allow the frontend (Azure Static Web Apps) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://delightful-river-071a00600.7.azurestaticapps.net"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(attendance_router)
app.include_router(leave_router)
app.include_router(payroll_router)
app.include_router(reports_router)

setup_database()

@app.get("/")
def root():
    return {"message": "HRMS API running"}
