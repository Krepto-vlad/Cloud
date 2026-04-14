from database import get_connection


def init():
    conn = get_connection()
    cursor = conn.cursor()

    # Create schema
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'UladzislauBarsukou_registration')
        EXEC('CREATE SCHEMA UladzislauBarsukou_registration')
    """)
    conn.commit()

    # Create users table
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = 'UladzislauBarsukou_registration' AND t.name = 'users'
        )
        CREATE TABLE UladzislauBarsukou_registration.users (
            UserID       INT IDENTITY(1,1) PRIMARY KEY,
            name         NVARCHAR(100)  NOT NULL,
            email        NVARCHAR(150)  NOT NULL UNIQUE,
            password_hash NVARCHAR(256) NOT NULL
        )
    """)

    # Create registrations table
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE s.name = 'UladzislauBarsukou_registration' AND t.name = 'registrations'
        )
        CREATE TABLE UladzislauBarsukou_registration.registrations (
            registerID   INT IDENTITY(1,1) PRIMARY KEY,
            userID       INT          NOT NULL REFERENCES UladzislauBarsukou_registration.users(UserID),
            tornamentId  INT          NOT NULL,
            status       NVARCHAR(50) NOT NULL DEFAULT 'pending'
        )
    """)
    conn.commit()

    # Stub data: users
    cursor.execute("SELECT COUNT(*) FROM UladzislauBarsukou_registration.users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO UladzislauBarsukou_registration.users (name, email, password_hash) VALUES
            ('Alice Johnson', 'alice@example.com', 'hashed_pw_1'),
            ('Bob Smith',     'bob@example.com',   'hashed_pw_2'),
            ('Carol White',   'carol@example.com', 'hashed_pw_3'),
            ('David Brown',   'david@example.com', 'hashed_pw_4'),
            ('Eve Davis',     'eve@example.com',   'hashed_pw_5')
        """)
        conn.commit()

    # Stub data: registrations
    cursor.execute("SELECT COUNT(*) FROM UladzislauBarsukou_registration.registrations")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO UladzislauBarsukou_registration.registrations (userID, tornamentId, status) VALUES
            (1, 1, 'confirmed'),
            (2, 1, 'confirmed'),
            (3, 2, 'pending'),
            (4, 2, 'confirmed'),
            (5, 3, 'cancelled'),
            (1, 3, 'confirmed')
        """)
        conn.commit()

    cursor.close()
    conn.close()
    print("UladzislauBarsukou_registration schema initialised successfully.")


if __name__ == "__main__":
    init()
