import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.database import get_connection
from app.audit import write_audit_log


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

    # ADMIN 계정이 존재하지 않는 경우
    if admin is None:
        write_audit_log(
            "LOGIN_FAILED",
            request.username,
            "/admin/auth/login"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    password_match = bcrypt.checkpw(
        request.password.encode("utf-8"),
        admin[2].encode("utf-8")
    )

    # 비밀번호 오류
    if not password_match:
        write_audit_log(
            "LOGIN_FAILED",
            request.username,
            "/admin/auth/login"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # 비활성 ADMIN
    if admin[4] != "ACTIVE":
        write_audit_log(
            "LOGIN_FAILED",
            request.username,
            "/admin/auth/login"
        )

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

    write_audit_log(
        "LOGIN_SUCCESS",
        request.username,
        "/admin/auth/login"
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }