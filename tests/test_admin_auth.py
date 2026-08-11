import requests
from tests.data.test_data import USERS

from tests.helpers.db_helper import (
    get_last_audit_id,
    get_audit_log,
)

def test_admin_login_success(
    base_url,
    db_connection,
    admin_user
):
    # 1. 테스트 시작 전 Audit Log 기준점 저장
    before_audit_id = get_last_audit_id(db_connection)

    # 2. ADMIN 정상 로그인
    response = requests.post(
        f"{base_url}/admin/auth/login",
        json={
            "username": admin_user["username"],
            "password": admin_user["password"],
        }
    )

    # 3. API Response 검증
    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["access_token"]

    # 4. 이번 요청으로 생성된 Audit Log 조회
    audit_log = get_audit_log(
        db_connection,
        after_id=before_audit_id,
        event_type="LOGIN_SUCCESS",
        username=admin_user["username"],
        endpoint="/admin/auth/login",
    )

    # 5. Audit Log 검증
    assert audit_log is not None
    assert audit_log[0] == "LOGIN_SUCCESS"
    assert audit_log[1] == admin_user["username"]
    assert audit_log[2] == "/admin/auth/login"

def test_admin_login_failure(
    base_url,
    db_connection,
    admin_user
):
    # 1. 테스트 시작 전 Audit Log 기준점 저장
    before_audit_id = get_last_audit_id(db_connection)

    # 2. ADMIN 잘못된 비밀번호로 로그인
    response = requests.post(
        f"{base_url}/admin/auth/login",
        json={
            "username": admin_user["username"],
            "password": USERS["invalid"]["password"],
        }
    )

    # 3. API Response 검증
    assert response.status_code == 401

    body = response.json()

    assert body["detail"] == "Invalid credentials"

    # 4. 이번 요청으로 생성된 Audit Log 조회
    audit_log = get_audit_log(
        db_connection,
        after_id=before_audit_id,
        event_type="LOGIN_FAILED",
        username=admin_user["username"],
        endpoint="/admin/auth/login",
    )

    # 5. Audit Log 검증
    assert audit_log is not None
    assert audit_log[0] == "LOGIN_FAILED"
    assert audit_log[1] == admin_user["username"]
    assert audit_log[2] == "/admin/auth/login"