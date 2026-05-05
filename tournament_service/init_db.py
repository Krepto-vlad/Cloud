from database import get_connection


def init():
    conn = get_connection()
    cursor = conn.cursor()

    # Create schema
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'UladzislauBarsukou_tournament')
        EXEC('CREATE SCHEMA UladzislauBarsukou_tournament')
    """)
    conn.commit()

    # Create tournaments table
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = 'UladzislauBarsukou_tournament' AND t.name = 'tournaments'
        )
        CREATE TABLE UladzislauBarsukou_tournament.tournaments (
            tornamentsID INT IDENTITY(1,1) PRIMARY KEY,
            name         NVARCHAR(200) NOT NULL,
            Date         DATE          NOT NULL,
            location     NVARCHAR(200) NOT NULL
        )
    """)

    # Create matches table
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = 'UladzislauBarsukou_tournament' AND t.name = 'matches'
        )
        CREATE TABLE UladzislauBarsukou_tournament.matches (
            matchID      INT IDENTITY(1,1) PRIMARY KEY,
            tournamentID INT          NOT NULL REFERENCES UladzislauBarsukou_tournament.tournaments(tornamentsID),
            participant1 NVARCHAR(100) NOT NULL,
            participant2 NVARCHAR(100) NOT NULL,
            match_date   DATETIME      NOT NULL,
            result       NVARCHAR(100) NULL
        )
    """)

    # Create schedules table
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = 'UladzislauBarsukou_tournament' AND t.name = 'schedules'
        )
        CREATE TABLE UladzislauBarsukou_tournament.schedules (
            scheduleID     INT IDENTITY(1,1) PRIMARY KEY,
            tournamentID   INT           NOT NULL REFERENCES UladzislauBarsukou_tournament.tournaments(tornamentsID),
            round          INT           NOT NULL,
            scheduled_date DATETIME      NOT NULL,
            description    NVARCHAR(500) NULL
        )
    """)
    conn.commit()

    # Stub data: tournaments
    cursor.execute("SELECT COUNT(*) FROM UladzislauBarsukou_tournament.tournaments")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO UladzislauBarsukou_tournament.tournaments (name, Date, location) VALUES
            ('Spring Tennis Open 2026',       '2026-04-20', 'Central Park Court, NYC'),
            ('Summer Basketball League 2026', '2026-06-15', 'LA Sports Arena'),
            ('Autumn Football Championship',  '2026-09-10', 'National Stadium')
        """)
        conn.commit()

        cursor.execute("""
            INSERT INTO UladzislauBarsukou_tournament.matches
            (tournamentID, participant1, participant2, match_date, result) VALUES
            (1, 'Alice Johnson', 'Bob Smith', '2026-04-21 10:00', 'Alice Johnson'),
            (1, 'Carol White',  'David Brown',  '2026-04-21 12:00', NULL),
            (2, 'Team Alpha',   'Team Beta',    '2026-06-16 15:00', NULL),
            (3, 'FC North',     'FC South',     '2026-09-11 18:00', NULL)
        """)

        cursor.execute("""
            INSERT INTO UladzislauBarsukou_tournament.schedules
            (tournamentID, round, scheduled_date, description) VALUES
            (1, 1, '2026-04-21 09:00', 'Quarter-finals'),
            (1, 2, '2026-04-23 09:00', 'Semi-finals'),
            (1, 3, '2026-04-25 14:00', 'Final'),
            (2, 1, '2026-06-16 14:00', 'Group Stage Round 1'),
            (3, 1, '2026-09-11 17:00', 'Opening Round')
        """)
        conn.commit()

    cursor.close()
    conn.close()
    print("UladzislauBarsukou_tournament schema initialised successfully.")


if __name__ == "__main__":
    init()
