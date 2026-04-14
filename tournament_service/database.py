import pyodbc
from dotenv import dotenv_values
from pathlib import Path

env_path = Path(__file__).parent.parent / "env"
config = dotenv_values(env_path)


def get_connection():
    server = config.get("DB_SERVER", "").replace("tcp:", "")
    database = config.get("DB_DATABASE", "")
    username = config.get("DB_USERNAME", "")
    password = config.get("DB_PASSWORD", "")
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
