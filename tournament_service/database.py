import os
import pyodbc
from dotenv import dotenv_values
from pathlib import Path

_env_file = dotenv_values(Path(__file__).parent.parent / "env")


def _cfg(key: str) -> str:
    return os.environ.get(key) or _env_file.get(key, "")


def get_connection():
    server = _cfg("DB_SERVER").replace("tcp:", "")
    database = _cfg("DB_DATABASE")
    username = _cfg("DB_USERNAME")
    password = _cfg("DB_PASSWORD")
    conn_str = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"Uid={username};"
        f"Pwd={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)
