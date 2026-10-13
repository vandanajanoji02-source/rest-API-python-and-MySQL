import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


def get_connection():
    env_file = Path(__file__).with_name(".env")
    load_dotenv(env_file)

    required_variables = ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
    missing_variables = [
        name for name in required_variables if os.getenv(name) is None
    ]
    if missing_variables:
        missing = ", ".join(missing_variables)
        raise RuntimeError(f"Missing required environment variables: {missing}")

    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "3307")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )


def test_database_connection():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT DATABASE()")
            result = cursor.fetchone()
            return result[0]
        finally:
            cursor.close()
    finally:
        connection.close()
