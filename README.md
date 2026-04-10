# Employee Tracking - HRMS Backend

A FastAPI-based Human Resource Management System (HRMS) backend with JWT authentication, attendance tracking, leave management, and payroll calculation.

---

## Project Structure

```
Employee_Tracking/
├── .env                   # Environment variables (not committed)
├── .gitignore
├── .python-version        # Python 3.12
├── pyproject.toml         # Project dependencies
├── README.md
└── Backend/
    ├── main.py            # FastAPI app entry point
    ├── db.py              # MySQL connection helper
    ├── auth/
    │   ├── router.py      # Signup & login endpoints
    │   ├── schemas.py     # Pydantic models for auth
    │   └── utils.py       # JWT & bcrypt helpers
    ├── attendance/
    │   ├── router.py      # Attendance mark endpoint
    │   └── schemas.py
    ├── leave/
    │   ├── router.py      # Leave apply, view, approve/reject
    │   └── schemas.py
    └── payroll/
        ├── router.py      # Payroll calculate & view
        └── schemas.py
```

---

## Prerequisites

- Python 3.12
- MySQL server running locally (or accessible remotely)
- [`uv`](https://github.com/astral-sh/uv) package manager (recommended) **or** `pip`

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd Employee_Tracking
```

### 2. Create the MySQL database and tables

Connect to your MySQL server and run the following SQL:

```sql
CREATE DATABASE hrms;
USE hrms;

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('employee', 'manager', 'hr', 'admin') DEFAULT 'employee',
    department VARCHAR(100),
    salary DECIMAL(10, 2) DEFAULT 0.00
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    date DATE NOT NULL,
    check_in DATETIME,
    status VARCHAR(20) DEFAULT 'present',
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE leaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    leave_type VARCHAR(50),
    start_date DATE,
    end_date DATE,
    reason TEXT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE payroll (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    basic_salary DECIMAL(10, 2),
    deductions DECIMAL(10, 2),
    net_salary DECIMAL(10, 2),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
```

### 3. Configure environment variables

Copy the example below and save it as `.env` in the project root (`Employee_Tracking/.env`):

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=hrms
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> **Note:** Never commit your `.env` file. It is already in `.gitignore`.

### 4. Install dependencies

Using `uv` (recommended):

```bash
uv sync
```

Using `pip`:

```bash
pip install -r requirements.txt
# or install manually:
pip install fastapi uvicorn mysql-connector-python pyjwt bcrypt python-dotenv
```

### 5. Run the server

```bash
cd Backend
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive docs (Swagger UI): `http://127.0.0.1:8000/docs`

---

## Authentication

The API uses **JWT Bearer tokens**. After login, include the token in all protected requests:

```
Authorization: Bearer <your_token>
```

---

## API Endpoints

### Auth

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/signup` | Public | Register a new employee |
| POST | `/auth/login` | Public | Login and get JWT token |

**Signup request body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secret123",
  "role": "employee",
  "department": "Engineering"
}
```
> `role` defaults to `"employee"`. Valid values: `employee`, `manager`, `hr`, `admin`.

**Login request body:**
```json
{
  "email": "john@example.com",
  "password": "secret123"
}
```

**Login response:**
```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer",
  "role": "employee",
  "name": "John Doe"
}
```

---

### Attendance

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/attendance/mark` | Any logged-in user | Mark today's attendance (once per day) |

Returns `400` if attendance is already marked for the day.

---

### Leave

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/leave/apply` | Any logged-in user | Apply for a leave |
| GET | `/leave/my-leaves` | Any logged-in user | View own leave history |
| GET | `/leave/all-leaves` | manager / hr / admin | View all employees' leaves |
| PUT | `/leave/{leave_id}/status` | manager / hr / admin | Approve or reject a leave |

**Apply leave request body:**
```json
{
  "leave_type": "sick",
  "start_date": "2026-04-15",
  "end_date": "2026-04-17",
  "reason": "Fever"
}
```

**Update leave status request body:**
```json
{
  "status": "approved"
}
```
> Valid values: `approved`, `rejected`.

---

### Payroll

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/payroll/calculate` | hr / admin | Calculate payroll for an employee for a given month |
| GET | `/payroll/my-payroll` | Any logged-in user | View own payroll records |

**Calculate payroll request body:**
```json
{
  "employee_id": 1,
  "month": 4,
  "year": 2026
}
```

Payroll is calculated as:
```
deduction = (base_salary / total_days_in_month) * days_absent
net_salary = base_salary - deduction
```

> The employee's `salary` field must be set in the `employees` table before calculating payroll.

---

## Role Summary

| Role | Capabilities |
|------|-------------|
| `employee` | Mark attendance, apply leave, view own leaves & payroll |
| `manager` | All of employee + view all leaves, approve/reject leaves |
| `hr` | All of manager + calculate payroll |
| `admin` | Full access |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| Database | MySQL |
| Auth | JWT (PyJWT) + bcrypt |
| Python | 3.12 |
| Package Manager | uv |
