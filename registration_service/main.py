import json
from pathlib import Path
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from database import get_connection

_env = dotenv_values(Path(__file__).parent.parent / "env")
SB_SEND_CONN_STR = _env.get("SB_SEND_CONN_STR", "")
SB_QUEUE_NAME = _env.get("SB_QUEUE_NAME", "")
if not SB_SEND_CONN_STR or not SB_QUEUE_NAME:
    missing = [k for k, v in {"SB_SEND_CONN_STR": SB_SEND_CONN_STR, "SB_QUEUE_NAME": SB_QUEUE_NAME}.items() if not v]
    raise RuntimeError("Missing required env configuration: " + ", ".join(missing))

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


class RegistrationCreate(BaseModel):
    userID: int
    tornamentId: int


@app.post("/registrations", status_code=201)
def create_registration(data: RegistrationCreate):
    """Create a new registration and publish UserRegistered event to the queue."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO UladzislauBarsukou_registration.registrations (userID, tornamentId, status) "
            "OUTPUT INSERTED.registerID VALUES (?, ?, 'pending')",
            data.userID, data.tornamentId,
        )
        row = cursor.fetchone()
        register_id = row[0]

        # Publish to Service Bus BEFORE committing — if send fails, rollback
        payload = json.dumps({
            "event": "UserRegistered",
            "registerID": register_id,
            "userID": data.userID,
            "tornamentId": data.tornamentId,
            "status": "pending",
        })
        try:
            with ServiceBusClient.from_connection_string(SB_SEND_CONN_STR) as client:
                with client.get_queue_sender(queue_name=SB_QUEUE_NAME) as sender:
                    sender.send_messages(ServiceBusMessage(payload))
        except Exception as exc:
            conn.rollback()
            raise HTTPException(status_code=503, detail="Unable to publish registration event. Please retry.") from exc

        conn.commit()
        print(f"[RegistrationService] Sent UserRegistered event for registerID={register_id}")
        return {"registerID": register_id, "userID": data.userID, "tornamentId": data.tornamentId, "status": "pending"}
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
