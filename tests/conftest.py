import os
import pytest
import jwt
import requests
from datetime import datetime, timezone, timedelta
from app.database import get_connection
from tests.data.test_data import USERS
from tests.helpers.db_helper import (
    get_user_status,
    update_user_status,
)

@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000"


@pytest.fixture
def db_connection() :
    conn = get_connection()

    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def inactive_user(db_connection):
    username = USERS["default"]["username"]

    # 1. 테스트 실행 전 현재 상태 확인
    original_status = get_user_status(
        db_connection,
        username
    )

    assert original_status is not None

    # 2. ACTIVE인 경우에만 INACTIVE로 변경
    if original_status == "ACTIVE":
        update_user_status(
            db_connection,
            username,
            "INACTIVE"
        )

    # 3. 실제 INACTIVE 상태인지 확인
    current_status = get_user_status(
        db_connection,
        username
    )

    assert current_status == "INACTIVE"

    try:
        # 4. 테스트에 정상 계정 정보 전달
        yield USERS["default"]

    finally:
        # 5. fixture가 ACTIVE → INACTIVE로 바꿨을 때만 원복
        if original_status == "ACTIVE":
            update_user_status(
                db_connection,
                username,
                "ACTIVE"
            )

            # 6. 원복 확인
            restored_status = get_user_status(
                db_connection,
                username
            )

            assert restored_status == "ACTIVE"

@pytest.fixture
def admin_user():
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")

    assert username is not None
    assert password is not None

    return {
        "username": username,
        "password": password,
    }

@pytest.fixture
def expired_admin_token(db_connection, admin_user):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE username = %s
              AND role = 'ADMIN';
            """,
            (admin_user["username"],)
        )

        admin = cursor.fetchone()

    assert admin is not None

    token = jwt.encode(
        {
            "sub": str(admin[0]),
            "role": "ADMIN",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm="HS256"
    )

    return token

@pytest.fixture
def admin_token(base_url, admin_user):
    response = requests.post(
        f"{base_url}/admin/auth/login",
        json={
            "username": admin_user["username"],
            "password": admin_user["password"],
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["access_token"]

    return body["access_token"]