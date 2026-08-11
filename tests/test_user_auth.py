import requests
from tests.data.test_data import USERS

from tests.helpers.db_helper import (
    get_last_audit_id,
    get_audit_log,
)

def test_user_login_success(base_url, db_connection):

    # 1. 테스트 시작 전 Audit Log 기준점 저장
    before_audit_id = get_last_audit_id(db_connection)

    # 2. USER 정상 로그인
    response = requests.post(
        f"{base_url}/auth/login",
        json={
            "username": USERS["default"]["username"],
            "password": USERS["default"]["password"],
        }
    )

    # 3. API Response 검증
    assert response.status_code == 200

    body = response.json()

    assert body["message"] == "Login successful"
    assert body["username"] == USERS["default"]["username"]
    assert body["role"] == "USER"

    # 4. 이번 요청으로 생성된 Audit Log 조회
    audit_log = get_audit_log(
        db_connection,
        after_id=before_audit_id,
        event_type="LOGIN_SUCCESS",
        username=USERS["default"]["username"],
        endpoint="/auth/login",
    )

    # 5. Audit Log 검증
    assert audit_log is not None
    assert audit_log[0] == "LOGIN_SUCCESS"
    assert audit_log[1] == USERS["default"]["username"]
    assert audit_log[2] == "/auth/login"


def test_user_login_wrong_password(base_url, db_connection):

    # 1. 테스트 시작 전 Audit Log 기준점 저장
    before_audit_id = get_last_audit_id(db_connection)

    # 2. USER 정상 로그인
    response = requests.post(
        f"{base_url}/auth/login",
        json={
            "username": USERS["invalid"]["username"],
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
        username=USERS["invalid"]["username"],
        endpoint="/auth/login",
    )

    # 5. Audit Log 검증
    assert audit_log is not None
    assert audit_log[0] == "LOGIN_FAILED"
    assert audit_log[1] == USERS["invalid"]["username"]
    assert audit_log[2] == "/auth/login"


def test_user_login_inactive(
    base_url,
    db_connection,
    inactive_user
):
    # 1. 테스트 시작 전 Audit Log 기준점 저장
    before_audit_id = get_last_audit_id(db_connection)

    # 2. INACTIVE USER 로그인
    response = requests.post(
        f"{base_url}/auth/login",
        json={
            "username": inactive_user["username"],
            "password": inactive_user["password"],
        }
    )

    # 3. API Response 검증
    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Account is inactive"

    # 4. 이번 요청으로 생성된 Audit Log 조회
    audit_log = get_audit_log(
        db_connection,
        after_id=before_audit_id,
        event_type="LOGIN_FAILED",
        username=inactive_user["username"],
        endpoint="/auth/login",
    )

    # 5. Audit Log 검증
    assert audit_log is not None
    assert audit_log[0] == "LOGIN_FAILED"
    assert audit_log[1] == inactive_user["username"]
    assert audit_log[2] == "/auth/login"


def test_admin_blocked_from_user_login(
    base_url,
    db_connection,
    admin_user
):
    # 1. 테스트 시작 전 Audit Log 기준점 저장
    before_audit_id = get_last_audit_id(db_connection)

    # 2. 정상 ADMIN 계정으로 USER 로그인 API 호출
    response = requests.post(
        f"{base_url}/auth/login",
        json={
            "username": admin_user["username"],
            "password": admin_user["password"],
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
        endpoint="/auth/login",
    )

    # 5. Audit Log 검증
    assert audit_log is not None
    assert audit_log[0] == "LOGIN_FAILED"
    assert audit_log[1] == admin_user["username"]
    assert audit_log[2] == "/auth/login"