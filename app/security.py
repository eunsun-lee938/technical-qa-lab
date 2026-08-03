import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_connection
from app.audit import write_audit_log


load_dotenv()

bearer_scheme = HTTPBearer(auto_error=False)


def verify_admin_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    # 토큰 자체가 없는 경우
    if credentials is None:
        write_audit_log(
            "ACCESS_DENIED",
            None,
            request.url.path
        )

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

        # 토큰은 정상이나 ADMIN 권한이 아닌 경우
        if admin_id is None or role != "ADMIN":
            write_audit_log(
                "ACCESS_DENIED",
                None,
                request.url.path
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    # 만료된 토큰
    except jwt.ExpiredSignatureError:
        write_audit_log(
            "ACCESS_DENIED",
            None,
            request.url.path
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    # 위조/형식 오류 등 잘못된 토큰
    except jwt.InvalidTokenError:
        write_audit_log(
            "ACCESS_DENIED",
            None,
            request.url.path
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # 토큰에 있는 ADMIN이 현재 DB에서도 유효한지 확인
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

    # 삭제됐거나 비활성화된 ADMIN
    if admin is None:
        write_audit_log(
            "ACCESS_DENIED",
            None,
            request.url.path
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return admin_id