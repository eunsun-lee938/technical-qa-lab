from app.database import get_connection


def write_audit_log(event_type, username, endpoint):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO audit_logs (
                    event_type,
                    username,
                    endpoint
                )
                VALUES (%s, %s, %s);
                """,
                (
                    event_type,
                    username,
                    endpoint
                )
            )