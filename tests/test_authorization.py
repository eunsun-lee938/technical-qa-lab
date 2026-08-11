import requests
from tests.data.test_data import TOKENS

from tests.helpers.db_helper import (
    get_last_audit_id,
    get_audit_log,
)

def test_admin_api_without_token(
    base_url,
    db_connection
):
    # 1. 테스트 시작 전 Audit Log 기준점 저장
    before_audit_id = get_last_audit_id(db_connection)

    # 2. Authorization Header 없이 ADMIN API 호출
    response = requests.get(
        f"{base_url}/admin/users"
    )

    # 3. API Response 검증
    assert response.status_code == 401

    # 4. 이번 요청으로 생성된 ACCESS_DENIED Audit 조회
    audit_log = get_audit_log(
        db_connection,
        after_id=before_audit_id,
        event_type="ACCESS_DENIED",
        username=None,
        endpoint="/admin/users",
    )

    # 5. Audit Log 검증
    assert audit_log is not None
    assert audit_log[0] == "ACCESS_DENIED"
    assert audit_log[1] is None
    assert audit_log[2] == "/admin/users"

def test_admin_api_invalid_token(
    base_url,
    db_connection
):
    # 1. 테스트 시작 전 Audit Log 기준점 저장
    before_audit_id = get_last_audit_id(db_connection)

    # 2. 잘못된 토큰으로 ADMIN API 호출
    response = requests.get(
        f"{base_url}/admin/users",
        headers={
            "Authorization": f"Bearer {TOKENS['invalid']['token']}"
        }
    )

    # 3. API Response 검증
    assert response.status_code == 401

    # 4. ACCESS_DENIED Audit Log 조회
    audit_log = get_audit_log(
        db_connection,
        after_id=before_audit_id,
        event_type="ACCESS_DENIED",
        username=None,
        endpoint="/admin/users",
    )

    # 5. Audit Log 검증
    assert audit_log is not None
    assert audit_log[0] == "ACCESS_DENIED"
    assert audit_log[1] is None
    assert audit_log[2] == "/admin/users"


def test_admin_api_expired_token(
    base_url,
    db_connection,
    expired_admin_token
):
    # 1. 테스트 시작 전 Audit Log 기준점 저장
    before_audit_id = get_last_audit_id(db_connection)

    # 2. 만료된 ADMIN 토큰으로 ADMIN API 호출
    response = requests.get(
        f"{base_url}/admin/users",
        headers={
            "Authorization": f"Bearer {expired_admin_token}"
        }
    )

    # 3. API Response 검증
    assert response.status_code == 401

    # 4. ACCESS_DENIED Audit Log 조회
    audit_log = get_audit_log(
        db_connection,
        after_id=before_audit_id,
        event_type="ACCESS_DENIED",
        username=None,
        endpoint="/admin/users",
    )

    # 5. Audit Log 검증
    assert audit_log is not None
    assert audit_log[0] == "ACCESS_DENIED"
    assert audit_log[1] is None
    assert audit_log[2] == "/admin/users"