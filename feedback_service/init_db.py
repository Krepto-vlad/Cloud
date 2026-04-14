from database import get_connection


def init():
    conn = get_connection()
    cursor = conn.cursor()

    # Create schema
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'UladzislauBarsukou_feedback')
        EXEC('CREATE SCHEMA UladzislauBarsukou_feedback')
    """)
    conn.commit()

    # Create feedback table
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = 'UladzislauBarsukou_feedback' AND t.name = 'feedback'
        )
        CREATE TABLE UladzislauBarsukou_feedback.feedback (
            feedbackID  INT IDENTITY(1,1) PRIMARY KEY,
            userID      INT            NOT NULL,
            tornamentId INT            NOT NULL,
            comments    NVARCHAR(1000) NOT NULL
        )
    """)

    # Create feedback_responses table
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = 'UladzislauBarsukou_feedback' AND t.name = 'feedback_responses'
        )
        CREATE TABLE UladzislauBarsukou_feedback.feedback_responses (
            responseID INT IDENTITY(1,1) PRIMARY KEY,
            feedbackID INT            NOT NULL REFERENCES UladzislauBarsukou_feedback.feedback(feedbackID),
            response   NVARCHAR(1000) NOT NULL,
            created_at DATETIME       NOT NULL DEFAULT GETDATE()
        )
    """)
    conn.commit()

    # Stub data: feedback
    cursor.execute("SELECT COUNT(*) FROM UladzislauBarsukou_feedback.feedback")
    row = cursor.fetchone()
    if row is not None and row[0] == 0:
        cursor.execute("""
            INSERT INTO UladzislauBarsukou_feedback.feedback (userID, tornamentId, comments) VALUES
            (1, 1, 'Great tournament, well organised!'),
            (2, 1, 'Loved the venue, would participate again.'),
            (3, 2, 'Schedule was a bit tight but overall good.'),
            (4, 2, 'Need better facilities next time.'),
            (5, 3, 'Amazing experience, highly recommend!')
        """)
        conn.commit()

        cursor.execute("""
            INSERT INTO UladzislauBarsukou_feedback.feedback_responses (feedbackID, response) VALUES
            (1, 'Thank you for your positive feedback!'),
            (3, 'We will improve the schedule in future events.'),
            (4, 'Thank you for the suggestion, we will look into it.')
        """)
        conn.commit()

    cursor.close()
    conn.close()
    print("UladzislauBarsukou_feedback schema initialised successfully.")


if __name__ == "__main__":
    init()
