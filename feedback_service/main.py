import json
import threading
import time
from pathlib import Path
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException
from azure.servicebus import ServiceBusClient
from database import get_connection

_env = dotenv_values(Path(__file__).parent.parent / "env")
SB_LISTEN_CONN_STR = _env.get("SB_LISTEN_CONN_STR", "")
SB_QUEUE_NAME = _env.get("SB_QUEUE_NAME", "")
if not SB_LISTEN_CONN_STR or not SB_QUEUE_NAME:
    missing = [k for k, v in {"SB_LISTEN_CONN_STR": SB_LISTEN_CONN_STR, "SB_QUEUE_NAME": SB_QUEUE_NAME}.items() if not v]
    raise RuntimeError("Missing required env configuration: " + ", ".join(missing))

POLL_INTERVAL_SECONDS = 10

app = FastAPI(title="Feedback Service", version="1.0.0")


def _poll_queue():
    """Background thread: reads messages from Service Bus every POLL_INTERVAL_SECONDS."""
    print(f"[FeedbackService] Queue listener started (interval={POLL_INTERVAL_SECONDS}s)")
    while True:
        try:
            with ServiceBusClient.from_connection_string(SB_LISTEN_CONN_STR) as client:
                with client.get_queue_receiver(queue_name=SB_QUEUE_NAME, max_wait_time=5) as receiver:
                    messages = receiver.receive_messages(max_message_count=20, max_wait_time=5)
                    for msg in messages:
                        raw = b"".join(msg.body) if hasattr(msg.body, "__iter__") and not isinstance(msg.body, (bytes, str)) else msg.body
                        body = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
                        print(f"[FeedbackService] Received message: {body}")
                        try:
                            data = json.loads(body)
                            event = data.get("event", "unknown")
                            print(f"[FeedbackService] Event={event}, data={data}")
                        except json.JSONDecodeError:
                            print(f"[FeedbackService] Non-JSON message: {body}")
                        receiver.complete_message(msg)
        except Exception as exc:
            print(f"[FeedbackService] Queue error: {exc}")
        time.sleep(POLL_INTERVAL_SECONDS)


@app.on_event("startup")
def startup_event():
    t = threading.Thread(target=_poll_queue, daemon=True)
    t.start()


@app.get("/")
def root():
    return {"service": "Feedback Service", "status": "running"}


# ---------- Feedback ----------

@app.get("/feedback")
def get_all_feedback():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT feedbackID, userID, tornamentId, comments FROM UladzislauBarsukou_feedback.feedback"
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"feedbackID": r[0], "userID": r[1], "tornamentId": r[2], "comments": r[3]}
        for r in rows
    ]


@app.get("/feedback/my")
def get_my_feedback(user_id: int):
    """Pass ?user_id=<id> to get feedback submitted by a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT feedbackID, userID, tornamentId, comments "
        "FROM UladzislauBarsukou_feedback.feedback WHERE userID = ?",
        user_id,
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"feedbackID": r[0], "userID": r[1], "tornamentId": r[2], "comments": r[3]}
        for r in rows
    ]


@app.get("/feedback/tournament/{tournament_id}")
def get_feedback_by_tournament(tournament_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT feedbackID, userID, tornamentId, comments "
        "FROM UladzislauBarsukou_feedback.feedback WHERE tornamentId = ?",
        tournament_id,
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"feedbackID": r[0], "userID": r[1], "tornamentId": r[2], "comments": r[3]}
        for r in rows
    ]


@app.get("/feedback/{feedback_id}")
def get_feedback(feedback_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT feedbackID, userID, tornamentId, comments "
        "FROM UladzislauBarsukou_feedback.feedback WHERE feedbackID = ?",
        feedback_id,
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return {"feedbackID": row[0], "userID": row[1], "tornamentId": row[2], "comments": row[3]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
