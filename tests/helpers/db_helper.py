def get_audit_log(
    db_connection,
    after_id,
    event_type,
    username,
    endpoint
):
    with db_connection.cursor() as cursor:

        if username is None:
            cursor.execute(
                """
                SELECT event_type, username, endpoint
                FROM audit_logs
                WHERE id > %s
                  AND event_type = %s
                  AND username IS NULL
                  AND endpoint = %s
                ORDER BY id DESC
                LIMIT 1;
                """,
                (
                    after_id,
                    event_type,
                    endpoint,
                )
            )

        else:
            cursor.execute(
                """
                SELECT event_type, username, endpoint
                FROM audit_logs
                WHERE id > %s
                  AND event_type = %s
                  AND username = %s
                  AND endpoint = %s
                ORDER BY id DESC
                LIMIT 1;
                """,
                (
                    after_id,
                    event_type,
                    username,
                    endpoint,
                )
            )

        return cursor.fetchone()

def get_last_audit_id(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COALESCE(MAX(id), 0)
            FROM audit_logs;
            """
        )

        return cursor.fetchone()[0]

def get_user_status(db_connection, username):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT status
            FROM users
            WHERE username = %s;
            """,
            (username,)
        )

        row = cursor.fetchone()

    return row[0] if row else None


def update_user_status(db_connection, username, status):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE users
            SET status = %s
            WHERE username = %s;
            """,
            (
                status,
                username,
            )
        )

    db_connection.commit()

def get_user_by_username(db_connection, username):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, username, password_hash, role, status
            FROM users
            WHERE username = %s;
            """,
            (username,)
        )

        return cursor.fetchone()


def delete_user_by_username(db_connection, username):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM users
            WHERE username = %s
              AND role = 'USER';
            """,
            (username,)
        )

    db_connection.commit()

def count_users_by_username(db_connection, username):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM users
            WHERE username = %s;
            """,
            (username,)
        )

        return cursor.fetchone()[0]

