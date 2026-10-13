import math
import re
from typing import Optional

import mysql.connector
from fastapi import Body, FastAPI, HTTPException, Query
from mysql.connector.errors import IntegrityError

import employee_queries


app = FastAPI(title="Employee Management API")


def validate_employee_data(employee_data):
    required_fields = ("name", "email", "department", "salary")
    missing_fields = [
        field for field in required_fields if field not in employee_data
    ]
    if missing_fields:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required fields: {', '.join(missing_fields)}",
        )

    for field in ("name", "email", "department"):
        value = employee_data[field]
        if not isinstance(value, str) or not value.strip():
            raise HTTPException(
                status_code=422,
                detail=f"{field} must be a non-empty string",
            )

    if len(employee_data["name"]) > 100:
        raise HTTPException(status_code=422, detail="name is too long")
    if len(employee_data["email"]) > 255:
        raise HTTPException(status_code=422, detail="email is too long")
    if len(employee_data["department"]) > 100:
        raise HTTPException(status_code=422, detail="department is too long")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", employee_data["email"]):
        raise HTTPException(
            status_code=422,
            detail="email must have a valid basic format",
        )

    salary = employee_data["salary"]
    if isinstance(salary, bool) or not isinstance(salary, (int, float)):
        raise HTTPException(status_code=422, detail="salary must be a number")
    if not math.isfinite(salary) or salary <= 0 or salary > 99999999.99:
        raise HTTPException(
            status_code=422,
            detail="salary must be greater than 0 and at most 99999999.99",
        )

    return {
        "name": employee_data["name"].strip(),
        "email": employee_data["email"].strip(),
        "department": employee_data["department"].strip(),
        "salary": salary,
    }


def raise_database_http_error(error):
    if isinstance(error, IntegrityError):
        raise HTTPException(
            status_code=409,
            detail="That email address is already used by an employee",
        ) from error
    if isinstance(error, (mysql.connector.Error, RuntimeError)):
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Check the MySQL service and settings.",
        ) from error
    raise error


@app.post("/employees", status_code=201)
def create_employee(employee_data: dict = Body(...)):
    employee_data = validate_employee_data(employee_data)
    try:
        return employee_queries.add_employee(employee_data)
    except (mysql.connector.Error, RuntimeError) as error:
        raise_database_http_error(error)


@app.get("/employees")
def read_employees():
    try:
        return employee_queries.get_all_employees()
    except (mysql.connector.Error, RuntimeError) as error:
        raise_database_http_error(error)


@app.get("/employees/search")
def find_employees(
    name: Optional[str] = Query(default=None, min_length=1),
    department: Optional[str] = Query(default=None, min_length=1),
):
    if name is None and department is None:
        raise HTTPException(
            status_code=422,
            detail="Provide a name, a department, or both to search",
        )
    try:
        return employee_queries.search_employees(name, department)
    except (mysql.connector.Error, RuntimeError) as error:
        raise_database_http_error(error)


@app.get("/employees/{employee_id}")
def read_employee(employee_id: int):
    try:
        employee = employee_queries.get_employee_by_id(employee_id)
    except (mysql.connector.Error, RuntimeError) as error:
        raise_database_http_error(error)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.put("/employees/{employee_id}")
def replace_employee(employee_id: int, employee_data: dict = Body(...)):
    employee_data = validate_employee_data(employee_data)
    try:
        employee = employee_queries.update_employee(employee_id, employee_data)
    except (mysql.connector.Error, RuntimeError) as error:
        raise_database_http_error(error)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.delete("/employees/{employee_id}")
def remove_employee(employee_id: int):
    try:
        deleted = employee_queries.delete_employee(employee_id)
    except (mysql.connector.Error, RuntimeError) as error:
        raise_database_http_error(error)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}
