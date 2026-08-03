import bcrypt
from app.security import verify_admin_token
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_connection
from typing import Literal
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - Users"],
    include_in_schema=False,
    dependencies=[Depends(verify_admin_token)]
)

class UserStatusUpdate(BaseModel):
    status: Literal["ACTIVE", "INACTIVE"]


@router.get("")
def get_users():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, role, status, created_at
                FROM users
                where role = 'USER'
                ORDER BY id;
            """)

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "username": row[1],
            "role": row[2],
            "status": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]

@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    password_hash = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    username,
                    password_hash,
                    role,
                    status
                )
                (
                    user.username,
                    password_hash,
                    "USER",
                    user.status,
                )
                RETURNING id, username, role, status, created_at;
                """,
                (
                    user.username,
                    password_hash,
                    user.role,
                    user.status,
                )
            )

            row = cursor.fetchone()

    return {
        "id": row[0],
        "username": row[1],
        "role": row[2],
        "status": row[3],
        "created_at": row[4],
    }

@router.patch("/{user_id}/status")
def update_user_status(user_id: int, update: UserStatusUpdate):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET status = %s
                WHERE id = %s
                RETURNING id, username, role, status;
                """,
                (
                    update.status,
                    user_id,
                )
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": row[0],
        "username": row[1],
        "role": row[2],
        "status": row[3],
    }
