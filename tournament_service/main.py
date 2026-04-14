from fastapi import FastAPI, HTTPException
from database import get_connection

app = FastAPI(title="Tournament Service", version="1.0.0")


@app.get("/")
def root():
    return {"service": "Tournament Service", "status": "running"}


# ---------- Tournaments ----------

@app.get("/tournaments")
def get_tournaments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT tornamentsID, name, Date, location FROM UladzislauBarsukou_tournament.tournaments"
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"tornamentsID": r[0], "name": r[1], "Date": str(r[2]), "location": r[3]}
        for r in rows
    ]


@app.get("/tournaments/{tournament_id}")
def get_tournament(tournament_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT tornamentsID, name, Date, location "
        "FROM UladzislauBarsukou_tournament.tournaments WHERE tornamentsID = ?",
        tournament_id,
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return {"tornamentsID": row[0], "name": row[1], "Date": str(row[2]), "location": row[3]}


# ---------- Schedule ----------

@app.get("/tournaments/{tournament_id}/schedule")
def get_tournament_schedule(tournament_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT scheduleID, round, scheduled_date, description "
        "FROM UladzislauBarsukou_tournament.schedules WHERE tournamentID = ?",
        tournament_id,
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "scheduleID": r[0],
            "round": r[1],
            "scheduled_date": str(r[2]),
            "description": r[3],
        }
        for r in rows
    ]


# ---------- Matches ----------

@app.get("/tournaments/{tournament_id}/matches")
def get_tournament_matches(tournament_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT matchID, participant1, participant2, match_date, result "
        "FROM UladzislauBarsukou_tournament.matches WHERE tournamentID = ?",
        tournament_id,
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "matchID": r[0],
            "participant1": r[1],
            "participant2": r[2],
            "match_date": str(r[3]),
            "result": r[4],
        }
        for r in rows
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
