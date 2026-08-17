import uuid

from tests.data.test_data import USERS, STATUSES

from tests.helpers.user_helper import (
    run_step,
    create_user,
    check_duplicate_username,
    check_invalid_user_status,
    change_user_status,
    check_user_list,
    cleanup_user,
)


def test_user_lifecycle(
    base_url,
    db_connection,
    admin_token,
):
    username = (
        USERS["create"]["username_prefix"]
        + uuid.uuid4().hex[:8]
    )

    password = USERS["create"]["password"]

    try:
        # 1. USER 생성
        user = run_step(
            "CREATE USER",
            create_user,
            base_url,
            db_connection,
            admin_token,
            username,
            password,
            "ACTIVE",
        )

        user_id = user["id"]

        # 2. 중복 username - BUG-001 Regression
        run_step(
            "DUPLICATE USERNAME",
            check_duplicate_username,
            base_url,
            admin_token,
            db_connection,
            username,
            password,
            "ACTIVE",
        )

        # 3. Invalid Status
        run_step(
            "INVALID USER STATUS",
            check_invalid_user_status,
            base_url,
            admin_token,
            db_connection,
            user_id,
            username,
            STATUSES["invalid"],
            "ACTIVE",
        )

        # 4. ACTIVE → INACTIVE
        run_step(
            "UPDATE ACTIVE -> INACTIVE",
            change_user_status,
            base_url,
            db_connection,
            admin_token,
            user_id,
            username,
            "INACTIVE",
        )

        # 5. INACTIVE → ACTIVE
        run_step(
            "UPDATE INACTIVE -> ACTIVE",
            change_user_status,
            base_url,
            db_connection,
            admin_token,
            user_id,
            username,
            "ACTIVE",
        )

        # 6. USER LIST
        run_step(
            "GET USER LIST",
            check_user_list,
            base_url,
            admin_token,
            user_id,
            username,
            "ACTIVE",
        )

    finally:
        cleanup_user(
            db_connection,
            username,
        )