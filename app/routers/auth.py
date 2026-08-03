import bcrypt

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.database import get_connection


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(request: LoginRequest):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, password_hash, role, status
                FROM users
                WHERE username = %s
                AND role = 'USER';
                """,
                (request.username,)
            )

            user = cursor.fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    password_match = bcrypt.checkpw(
        request.password.encode("utf-8"),
        user[2].encode("utf-8")
    )

    if not password_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if user[4] != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    return {
        "message": "Login successful",
        "user_id": user[0],
        "username": user[1],
        "role": user[3],
    }