import os

import bcrypt
from dotenv import load_dotenv

from app.database import get_connection


load_dotenv()


def init_admin():
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT id, username
                FROM users
                WHERE role = 'ADMIN'
                LIMIT 1;
                """
            )

            existing_admin = cursor.fetchone()

            if existing_admin:
                print(
                    f"ADMIN already exists: {existing_admin[1]}"
                )
                return

            password_hash = bcrypt.hashpw(
                admin_password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            cursor.execute(
                """
                INSERT INTO users (
                    username,
                    password_hash,
                    role,
                    status
                )
                VALUES (%s, %s, 'ADMIN', 'ACTIVE')
                RETURNING id, username, role, status;
                """,
                (
                    admin_username,
                    password_hash,
                )
            )

            admin = cursor.fetchone()

    print(f"ADMIN created: {admin}")


if __name__ == "__main__":
    init_admin()