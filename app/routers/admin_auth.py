import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv

from app.database import get_connection


load_dotenv()


router = APIRouter(
    prefix="/admin/auth",
    tags=["Admin - Auth"],
    include_in_schema=False
)


class AdminLoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def admin_login(request: AdminLoginRequest):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, password_hash, role, status
                FROM users
                WHERE username = %s
                  AND role = 'ADMIN';
                """,
                (request.username,)
            )

            admin = cursor.fetchone()

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    password_match = bcrypt.checkpw(
        request.password.encode("utf-8"),
        admin[2].encode("utf-8")
    )

    if not password_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if admin[4] != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    token = jwt.encode(
        {
            "sub": str(admin[0]),
            "role": "ADMIN",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm="HS256"
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }