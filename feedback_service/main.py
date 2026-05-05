import json
import logging
import os
import threading
import time
from pathlib import Path
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException
from azure.servicebus import ServiceBusClient
from database import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("feedback_service")

_env = dotenv_values(Path(__file__).parent.parent / "env")
SB_LISTEN_CONN_STR = os.environ.get("SB_LISTEN_CONN_STR") or _env.get("SB_LISTEN_CONN_STR", "")
SB_QUEUE_NAME = os.environ.get("SB_QUEUE_NAME") or _env.get("SB_QUEUE_NAME", "")
if not SB_LISTEN_CONN_STR or not SB_QUEUE_NAME:
    missing = [
        k for k, v in {
            "SB_LISTEN_CONN_STR": SB_LISTEN_CONN_STR,
            "SB_QUEUE_NAME": SB_QUEUE_NAME,
        }.items()
        if not v
    ]
    raise RuntimeError("Missing required env configuration: " + ", ".join(missing))

POLL_INTERVAL_SECONDS = 10

app = FastAPI(title="Feedback Service", version="1.0.0")


def _poll_queue():
    """Background thread: reads messages from Service Bus every POLL_INTERVAL_SECONDS."""
    logger.info("Queue listener started (interval=%ds)", POLL_INTERVAL_SECONDS)
    while True:
        try:
            with ServiceBusClient.from_connection_string(SB_LISTEN_CONN_STR) as client:
                with client.get_queue_receiver(
                    queue_name=SB_QUEUE_NAME, max_wait_time=5
                ) as receiver:
                    messages = receiver.receive_messages(
                        max_message_count=20, max_wait_time=5
                    )
                    for msg in messages:
                        if hasattr(msg.body, "__iter__") and not isinstance(
                            msg.body, (bytes, str)
                        ):
                            raw = b"".join(msg.body)
                        else:
                            raw = msg.body
                        body = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
                        logger.info("Received message: %s", body)
                        try:
                            data = json.loads(body)
                            event = data.get("event", "unknown")
                            logger.info(
                                "Processed event=%s registerID=%s",
                                event,
                                data.get("registerID"),
                            )
                        except json.JSONDecodeError:
                            logger.warning("Non-JSON message received: %s", body)
                        receiver.complete_message(msg)
        except Exception as exc:
            logger.error("Queue polling error: %s", exc)
        time.sleep(POLL_INTERVAL_SECONDS)


@app.on_event("startup")
def startup_event():
    t = threading.Thread(target=_poll_queue, daemon=True)
    t.start()
    logger.info("Feedback Service started")


@app.get("/")
def root():
    return {"service": "Feedback Service", "status": "running"}


@app.get("/feedback")
def get_all_feedback():
    logger.info("GET /feedback")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT feedbackID, userID, tornamentId, comments"
        " FROM UladzislauBarsukou_feedback.feedback"
    )
    rows = cursor.fetchall()
    conn.close()
    logger.info("Returning %d feedback entries", len(rows))
    return [
        {"feedbackID": r[0], "userID": r[1], "tornamentId": r[2], "comments": r[3]}
        for r in rows
    ]


@app.get("/feedback/my")
def get_my_feedback(user_id: int):
    logger.info("GET /feedback/my?user_id=%d", user_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT feedbackID, userID, tornamentId, comments"
        " FROM UladzislauBarsukou_feedback.feedback WHERE userID = ?",
        user_id,
    )
    rows = cursor.fetchall()
    conn.close()
    logger.info("Returning %d feedback entries for user %d", len(rows), user_id)
    return [
        {"feedbackID": r[0], "userID": r[1], "tornamentId": r[2], "comments": r[3]}
        for r in rows
    ]


@app.get("/feedback/tournament/{tournament_id}")
def get_feedback_by_tournament(tournament_id: int):
    logger.info("GET /feedback/tournament/%d", tournament_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT feedbackID, userID, tornamentId, comments"
        " FROM UladzislauBarsukou_feedback.feedback WHERE tornamentId = ?",
        tournament_id,
    )
    rows = cursor.fetchall()
    conn.close()
    logger.info("Returning %d feedback entries for tournament %d", len(rows), tournament_id)
    return [
        {"feedbackID": r[0], "userID": r[1], "tornamentId": r[2], "comments": r[3]}
        for r in rows
    ]


@app.get("/feedback/{feedback_id}")
def get_feedback(feedback_id: int):
    logger.info("GET /feedback/%d", feedback_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT feedbackID, userID, tornamentId, comments"
        " FROM UladzislauBarsukou_feedback.feedback WHERE feedbackID = ?",
        feedback_id,
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        logger.warning("Feedback %d not found", feedback_id)
        raise HTTPException(status_code=404, detail="Feedback not found")
    return {"feedbackID": row[0], "userID": row[1], "tornamentId": row[2], "comments": row[3]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
