from fastapi import FastAPI, HTTPException
from database import get_connection

app = FastAPI(title="Registration Service", version="1.0.0")


@app.get("/")
def root():
    return {"service": "Registration Service", "status": "running"}


# ---------- Users ----------

@app.get("/users")
def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, name, email FROM UladzislauBarsukou_registration.users")
    rows = cursor.fetchall()
    conn.close()
    return [{"UserID": r[0], "name": r[1], "email": r[2]} for r in rows]


@app.get("/users/{user_id}")
def get_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT UserID, name, email FROM UladzislauBarsukou_registration.users WHERE UserID = ?",
        user_id,
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return {"UserID": row[0], "name": row[1], "email": row[2]}


# ---------- Registrations ----------

@app.get("/registrations")
def get_registrations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT registerID, userID, tornamentId, status FROM UladzislauBarsukou_registration.registrations"
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"registerID": r[0], "userID": r[1], "tornamentId": r[2], "status": r[3]}
        for r in rows
    ]


@app.get("/registrations/{register_id}")
def get_registration(register_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT registerID, userID, tornamentId, status "
        "FROM UladzislauBarsukou_registration.registrations WHERE registerID = ?",
        register_id,
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found")
    return {"registerID": row[0], "userID": row[1], "tornamentId": row[2], "status": row[3]}


@app.get("/me/registrations")
def get_my_registrations(user_id: int):
    """Pass ?user_id=<id> to filter registrations for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT registerID, userID, tornamentId, status "
        "FROM UladzislauBarsukou_registration.registrations WHERE userID = ?",
        user_id,
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"registerID": r[0], "userID": r[1], "tornamentId": r[2], "status": r[3]}
        for r in rows
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
