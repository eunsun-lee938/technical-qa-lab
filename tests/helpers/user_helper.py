import requests

from tests.helpers.db_helper import (
    get_user_by_username,
    get_user_status,
    count_users_by_username,
    delete_user_by_username,
)


def run_step(step_name, func, *args, **kwargs):
    """
    Lifecycle의 각 기능 모듈을 실행한다.

    PASS:
        [PASS] 출력 후 함수 결과 반환

    FAIL:
        [FAIL] 출력 후 예외를 다시 발생시켜
        Lifecycle을 즉시 중단한다.
    """
    try:
        result = func(*args, **kwargs)

    except Exception as error:
        print(
            f"[FAIL] {step_name} "
            f"- {type(error).__name__}: {error}"
        )
        raise

    print(f"[PASS] {step_name}")

    return result


def create_user(
    base_url,
    db_connection,
    admin_token,
    username,
    password,
    status="ACTIVE",
):
    """
    USER 생성
    - API Response 검증
    - DB 저장 결과 검증
    """

    response = requests.post(
        f"{base_url}/admin/users",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "username": username,
            "password": password,
            "status": status,
        }
    )

    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}: "
        f"{response.text}"
    )

    user = response.json()

    assert user["username"] == username
    assert user["role"] == "USER"
    assert user["status"] == status

    # DB 검증
    db_user = get_user_by_username(
        db_connection,
        username
    )

    assert db_user is not None, (
        f"Created user not found in DB: {username}"
    )

    assert db_user[1] == username

    # password_hash 저장 여부
    assert db_user[2] is not None

    # 평문 비밀번호 저장 방지
    assert db_user[2] != password

    assert db_user[3] == "USER"
    assert db_user[4] == status

    return user


def change_user_status(
    base_url,
    db_connection,
    admin_token,
    user_id,
    username,
    status,
):
    """
    USER 상태 변경
    - PATCH Response 검증
    - DB 상태 변경 검증
    """

    response = requests.patch(
        f"{base_url}/admin/users/{user_id}/status",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "status": status
        }
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: "
        f"{response.text}"
    )

    user = response.json()

    assert user["id"] == user_id
    assert user["username"] == username
    assert user["role"] == "USER"
    assert user["status"] == status

    # DB 검증
    db_status = get_user_status(
        db_connection,
        username
    )

    assert db_status == status, (
        f"Expected DB status {status}, "
        f"got {db_status}"
    )

    return user


def check_user_list(
    base_url,
    admin_token,
    user_id,
    username,
    expected_status,
):
    """
    USER 목록 조회
    - Lifecycle에서 생성한 계정 존재 확인
    - USER 역할만 노출되는지 확인
    - 민감정보 미노출 확인
    """

    response = requests.get(
        f"{base_url}/admin/users",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: "
        f"{response.text}"
    )

    users = response.json()

    assert isinstance(users, list), (
        "GET /admin/users response must be a list"
    )

    target_user = next(
        (
            user
            for user in users
            if user["username"] == username
        ),
        None
    )

    assert target_user is not None, (
        f"User not found in list: {username}"
    )

    assert target_user["id"] == user_id
    assert target_user["username"] == username
    assert target_user["role"] == "USER"
    assert target_user["status"] == expected_status

    # ADMIN이 USER 목록에 노출되지 않는지
    assert all(
        user["role"] == "USER"
        for user in users
    ), "Non-USER account exposed in USER list"

    # 비밀번호 해시가 API 응답에 노출되지 않는지
    assert all(
        "password_hash" not in user
        for user in users
    ), "password_hash exposed in USER list"

    return users


def cleanup_user(
    db_connection,
    username,
):
    """
    Lifecycle 중간 FAIL 발생 시 테스트 데이터 cleanup.

    제품의 DELETE 기능 검증과는 별개이며,
    테스트 데이터가 DB에 남지 않도록 하는 안전장치.
    """

    user = get_user_by_username(
        db_connection,
        username
    )

    if user is None:
        return False

    delete_user_by_username(
        db_connection,
        username
    )

    remaining_user = get_user_by_username(
        db_connection,
        username
    )

    if remaining_user is not None:
        raise RuntimeError(
            f"Cleanup failed: {username}"
        )

    print(f"[CLEANUP] Deleted test user: {username}")

    return True

def check_duplicate_username(
    base_url,
    admin_token,
    db_connection,
    username,
    password,
    status="ACTIVE",
):
    """
    BUG-001 Regression
    - 동일 username 재생성 시 409
    - 추가 row가 생성되지 않는지 확인
    """

    response = requests.post(
        f"{base_url}/admin/users",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "username": username,
            "password": password,
            "status": status,
        }
    )

    assert response.status_code == 409, (
        f"Expected 409, got {response.status_code}: "
        f"{response.text}"
    )

    body = response.json()

    assert body["detail"] == "Username already exists"

    user_count = count_users_by_username(
        db_connection,
        username
    )

    assert user_count == 1, (
        f"Expected 1 row for {username}, "
        f"got {user_count}"
    )


def check_invalid_user_status(
    base_url,
    admin_token,
    db_connection,
    user_id,
    username,
    invalid_status,
    expected_status,
):
    """
    잘못된 status Validation
    - 422 반환
    - 기존 DB status가 변경되지 않는지 확인
    """

    before_status = get_user_status(
        db_connection,
        username
    )

    assert before_status == expected_status

    response = requests.patch(
        f"{base_url}/admin/users/{user_id}/status",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "status": invalid_status
        }
    )

    assert response.status_code == 422, (
        f"Expected 422, got {response.status_code}: "
        f"{response.text}"
    )

    body = response.json()

    assert "detail" in body

    after_status = get_user_status(
        db_connection,
        username
    )

    assert after_status == expected_status, (
        f"DB status changed unexpectedly: "
        f"{before_status} -> {after_status}"
    )