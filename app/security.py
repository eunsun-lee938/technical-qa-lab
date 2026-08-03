import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_connection


load_dotenv()

bearer_scheme = HTTPBearer(auto_error=False)


def verify_admin_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=["HS256"]
        )

        admin_id = payload.get("sub")
        role = payload.get("role")

        if admin_id is None or role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE id = %s
                  AND role = 'ADMIN'
                  AND status = 'ACTIVE';
                """,
                (admin_id,)
            )

            admin = cursor.fetchone()

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return admin_id