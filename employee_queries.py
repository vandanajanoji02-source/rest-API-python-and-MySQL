import mysql.connector

from database import get_connection


def get_all_employees():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, name, email, department, salary FROM employees"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_employee_by_id(employee_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, name, email, department, salary "
            "FROM employees WHERE id = %s",
            (employee_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def add_employee(employee_data):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO employees (name, email, department, salary) "
            "VALUES (%s, %s, %s, %s)",
            (
                employee_data["name"],
                employee_data["email"],
                employee_data["department"],
                employee_data["salary"],
            ),
        )
        employee_id = cursor.lastrowid
        connection.commit()

        cursor.execute(
            "SELECT id, name, email, department, salary "
            "FROM employees WHERE id = %s",
            (employee_id,),
        )
        return cursor.fetchone()
    except mysql.connector.Error:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def update_employee(employee_id, employee_data):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "UPDATE employees "
            "SET name = %s, email = %s, department = %s, salary = %s "
            "WHERE id = %s",
            (
                employee_data["name"],
                employee_data["email"],
                employee_data["department"],
                employee_data["salary"],
                employee_id,
            ),
        )
        connection.commit()

        cursor.execute(
            "SELECT id, name, email, department, salary "
            "FROM employees WHERE id = %s",
            (employee_id,),
        )
        return cursor.fetchone()
    except mysql.connector.Error:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def delete_employee(employee_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
        connection.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def search_employees(name=None, department=None):
    query = (
        "SELECT id, name, email, department, salary "
        "FROM employees WHERE 1 = 1"
    )
    parameters = []

    if name:
        query += " AND name LIKE %s"
        parameters.append(f"%{name}%")
    if department:
        query += " AND department LIKE %s"
        parameters.append(f"%{department}%")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, tuple(parameters))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
