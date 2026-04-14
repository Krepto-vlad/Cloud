from fastapi import FastAPI, HTTPException
from database import get_connection

app = FastAPI(title="Feedback Service", version="1.0.0")


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
