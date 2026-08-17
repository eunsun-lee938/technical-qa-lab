# 04. Automation Strategy

## 1. 목적

Technical QA Lab의 자동화는 수동 테스트 전체를 코드로 복제하는 것이 목적이 아니다.

반복 수행 가치가 높은 핵심 인증 / 인가 / 계정 관리 / 데이터 / Audit Log 시나리오를  
pytest로 자동화하여 다음 영역을 반복 검증한다.

- API 자동 Regression Test
- JWT 인증 / 인가 검증
- API Response와 PostgreSQL 데이터 교차검증
- Audit Log 자동 검증
- 테스트 데이터 Setup / Cleanup
- 기존 Database 데이터에 대한 의존성 최소화
- 실제 결함의 Regression 자동화
- 기능 단위 검증 로직을 조합한 Lifecycle 테스트
- 전체 자동화 수행 결과의 HTML Test Report 생성

---

## 2. Automation Tool

자동화 도구는 **pytest**를 사용한다.

Postman Collection은 관리자 API 호출, JWT Negative Scenario,  
수동 재현 및 요청 보관 용도로 유지한다.

전체 자동화 수행 결과는 **pytest-html**을 사용하여  
PASS / FAIL 결과를 HTML Report로 생성한다.

### pytest를 선택한 이유

1. HTTP Response와 PostgreSQL 데이터를 하나의 테스트 흐름에서 검증할 수 있다.
2. Audit Log 조회를 API 요청과 연결하여 자동 검증할 수 있다.
3. 테스트 데이터 생성 / 상태 변경 / 정리를 코드로 제어할 수 있다.
4. 인증 테스트에 필요한 USER를 동적으로 생성하여 기존 DB 데이터 의존성을 줄일 수 있다.
5. BUG-001과 같은 결함 Regression을 반복 실행할 수 있다.
6. 반복되는 검증 로직을 Helper로 분리하여 재사용할 수 있다.
7. USER 관리 기능을 Lifecycle 형태로 연결하여 검증할 수 있다.
8. 전체 실행 결과를 HTML Test Report로 남길 수 있다.

### 도구 역할 분리

| 도구 | 역할 |
| --- | --- |
| Swagger | Public API 명세 및 Smoke 확인 |
| Postman | ADMIN API / JWT / Negative 수동 시나리오 및 재현 |
| PostgreSQL | 데이터 / Constraint / Audit Log 직접 검증 |
| pytest | 핵심 기능 및 결함 Regression 자동화 |
| pytest-html | 전체 자동화 수행 결과 HTML Report 생성 |

---

## 3. Automation Selection Criteria

다음 조건을 기준으로 자동화 대상을 선정하였다.

### 자동화 우선

- 인증 / 인가 등 실패 영향도가 높은 기능
- 반복 수행 가치가 높은 기능
- 입력과 기대 결과가 명확하여 자동 판정 가능한 기능
- API 결과와 DB / Audit Log를 함께 검증할 가치가 있는 기능
- 실제 결함 발생 이력이 있어 Regression 가치가 높은 기능
- 하나의 사용자 흐름에서 연속적으로 검증할 가치가 높은 기능

### 수동 유지

- UI / 문서 노출 여부처럼 직접 확인 가치가 높은 항목
- 동일 인증 조건을 엔드포인트별로 반복 확인하는 상세 영향 범위 테스트
- DB Constraint를 직접 깨뜨리는 일회성 정책 검증
- 최초 Docker 환경 구축 및 재현 확인

자동화 비율 자체를 높이는 것보다  
**반복성과 위험도가 높은 시나리오를 안정적으로 재검증하는 것**을 우선한다.

---

## 4. Automation Scope

수동 테스트에서 선정한 **15개의 핵심 검증 의도**를 자동화하였다.

인증 / 인가 기능은 독립 pytest Test Function으로 구성하고,  
USER 관리 기능은 하나의 `test_user_lifecycle` 내부에서 기능별 Step을 순차 실행하도록 구성하였다.

### 최종 구성

- 독립 pytest Test Function: **9개**
- USER Lifecycle Test Function: **1개**
- USER Lifecycle 내부 검증 Step: **6개**
- 전체 pytest Test Function: **10개**
- 전체 핵심 자동화 검증 의도: **15개**

### Manual TC Mapping

| Pytest Test / Step | Manual TC | 검증 포인트 |
| --- | --- | --- |
| `test_user_login_success` | TC01, TC33 | 200 / USER 정보 / LOGIN_SUCCESS |
| `test_user_login_wrong_password` | TC02, TC35 | 401 / Invalid credentials / LOGIN_FAILED |
| `test_user_login_inactive` | TC04 | 403 / Account is inactive |
| `test_admin_blocked_from_user_login` | TC05 | USER 로그인 경로에서 ADMIN 차단 |
| `test_admin_login_success` | TC11, TC36 | ADMIN 로그인 / JWT / LOGIN_SUCCESS |
| `test_admin_login_failure` | TC07, TC37 | ADMIN 로그인 실패 / LOGIN_FAILED |
| `test_admin_api_without_token` | TC09, TC40 | 401 / ACCESS_DENIED / endpoint |
| `test_admin_api_invalid_token` | TC14, TC41 | Invalid JWT / ACCESS_DENIED |
| `test_admin_api_expired_token` | TC26, TC42 | Expired JWT / ACCESS_DENIED |
| `test_user_lifecycle - CREATE` | TC15, TC32 | USER 생성 / DB / password hash |
| `test_user_lifecycle - DUPLICATE` | TC16, TC27 | 중복 차단 / BUG-001 Regression |
| `test_user_lifecycle - INVALID STATUS` | TC23 | 422 / DB 값 미변경 |
| `test_user_lifecycle - INACTIVE` | TC19 | ACTIVE → INACTIVE / DB 반영 |
| `test_user_lifecycle - ACTIVE` | TC20 | INACTIVE → ACTIVE / DB 반영 |
| `test_user_lifecycle - GET USERS` | TC24 | USER 목록 / ADMIN 및 password_hash 미노출 |

Automation Coverage에 대한 상세 계산은  
[`03_test_coverage.md`](03_test_coverage.md)에서 관리한다.

---

## 5. USER Lifecycle Design

USER 관리 정상 / 예외 검증은 동일한 테스트 USER를 재사용하는  
Lifecycle 형태로 구성하였다.

```text
CREATE USER
        ↓
DUPLICATE USERNAME
        ↓
INVALID USER STATUS
        ↓
ACTIVE → INACTIVE
        ↓
INACTIVE → ACTIVE
        ↓
GET USER LIST
        ↓
Lifecycle 종료
        ↓
Test Data Cleanup
```

기능별로 USER를 새로 생성하고 삭제하는 대신,  
Lifecycle 시작 시 하나의 USER를 생성한 뒤 동일 계정을 후속 검증에 사용한다.

이를 통해 다음을 확인한다.

- 생성된 USER의 API Response 및 DB 저장 결과
- password hash 저장 여부
- 동일 username 재요청 시 BUG-001 Regression
- 잘못된 status 입력 시 Validation
- ACTIVE / INACTIVE 상태 전환
- 상태 변경 결과의 DB 반영
- USER 목록 조회 결과
- ADMIN 및 password_hash 미노출

제품 요구사항에는 USER DELETE 기능이 존재하지 않으므로,  
Lifecycle 마지막의 DB 삭제는 제품 기능 테스트가 아닌  
**테스트 데이터 Cleanup 목적**으로 수행한다.

---

## 6. Modular Test Design

USER 관리 기능의 반복되는 검증 로직은  
`user_helper.py`의 함수로 분리하였다.

```text
user_helper.py
├─ run_step()
├─ create_user()
├─ check_duplicate_username()
├─ check_invalid_user_status()
├─ change_user_status()
├─ check_user_list()
└─ cleanup_user()
```

`test_users.py`는 API 검증 코드를 반복 작성하지 않고  
각 검증 함수를 Lifecycle 순서에 따라 호출한다.

```text
test_user_lifecycle()
        │
        ├─ create_user()
        ├─ check_duplicate_username()
        ├─ check_invalid_user_status()
        ├─ change_user_status(INACTIVE)
        ├─ change_user_status(ACTIVE)
        └─ check_user_list()
```

각 기능 함수에서는 필요한 범위에 따라 다음 항목을 확인한다.

```text
API Request
    ↓
HTTP Status
    ↓
Response Body
    ↓
Database State
```

공통 실행 함수 `run_step()`은 각 기능 Step의 실행 결과를  
`[PASS]` 또는 `[FAIL]`로 출력한다.

중간 단계에서 Assertion이 실패하면 예외를 다시 발생시켜  
Lifecycle을 중단한다.

이후 `finally`에서 Cleanup을 수행하여  
실패 시에도 생성한 테스트 USER가 DB에 남지 않도록 구성하였다.

---

## 7. Test Data Strategy

테스트 데이터는 **기존 Database에 특정 USER가 존재한다는 전제를 최소화하는 방향**으로 구성하였다.

### 기존 구조의 문제

초기 USER 인증 테스트에서는 Database에 이미 존재하는 특정 일반 USER를 사용하였다.

이 방식은 기존 개발 환경에서는 정상적으로 동작할 수 있지만,  
새 PostgreSQL Volume을 생성한 환경에서는 해당 USER가 존재하지 않아  
동일한 Test Suite가 실패할 수 있다.

따라서 인증 테스트에 필요한 일반 USER도 pytest 실행 과정에서 생성하도록 변경하였다.

---

### 7-1. Dynamic USER Naming

테스트 USER의 username은 실행 시 동적으로 생성한다.

예:

```text
qa_test_a81f47c2
qa_test_f31982ab
```

이를 통해 다음 문제를 줄인다.

- 기존 username 충돌
- 이전 테스트 데이터 의존성
- 반복 실행 간 데이터 충돌

---

### 7-2. `default_user` Fixture

USER 인증 테스트에 필요한 기본 계정은 `default_user` fixture에서 생성한다.

```text
default_user
     ↓
Dynamic username 생성
     ↓
USER 생성
     ↓
테스트에 username/password 전달
     ↓
테스트 종료
     ↓
Cleanup
```

`default_user`는 다음 테스트에서 사용한다.

- USER 정상 로그인
- 잘못된 비밀번호 로그인
- INACTIVE USER 테스트의 기본 계정

테스트 종료 후 생성한 계정은 Cleanup한다.

---

### 7-3. `inactive_user` Fixture

INACTIVE USER 로그인 테스트를 위해 별도의 고정 INACTIVE 계정을 유지하지 않는다.

`default_user`로 생성된 ACTIVE USER를 테스트 전에 일시적으로 INACTIVE 상태로 변경한다.

```text
default_user 생성
       ↓
현재 Status 확인
       ↓
ACTIVE → INACTIVE
       ↓
403 로그인 검증
       ↓
INACTIVE → ACTIVE 복원
       ↓
default_user Cleanup
```

상태 변경 이전 값을 확인하고,  
fixture가 변경한 경우에만 테스트 종료 후 원래 상태로 복원한다.

이를 통해 테스트가 끝난 뒤 DB 상태를 가능한 한 원상태로 돌린다.

---

### 7-4. USER Lifecycle Test Data

`test_user_lifecycle` 역시 고정된 USER ID나 기존 일반 USER에 의존하지 않는다.

- username을 실행마다 동적으로 생성
- Lifecycle 시작 시 USER 1회 생성
- 생성된 USER의 ID를 API Response에서 확보
- 동일 USER를 중복 / Validation / 상태 변경 / 목록 조회에 재사용
- 중간 FAIL 발생 시에도 `finally` Cleanup
- Cleanup은 제품 기능이 아닌 테스트 Teardown 목적으로 사용

---

### 7-5. Static Test Data

동적으로 생성할 필요가 없는 값만 `test_data.py`에 관리한다.

예:

- 테스트 USER username prefix
- 테스트용 password
- Wrong Password
- Invalid Token
- Invalid Status

ADMIN Credential과 JWT Secret은 정적 테스트 데이터에 저장하지 않고  
환경변수에서 읽는다.

---

## 8. Authentication / Token Strategy

### USER Authentication

USER 로그인 테스트는 `default_user` fixture를 통해  
테스트 시작 시 필요한 USER를 생성한다.

따라서 기존 Database에 특정 일반 계정을 미리 생성할 필요가 없다.

정상 로그인에서는:

- `200 OK`
- username
- `role = USER`
- `LOGIN_SUCCESS` Audit Log

를 확인한다.

잘못된 비밀번호에서는 동일하게 실제 존재하는 USER를 사용하면서  
password만 잘못된 값으로 요청하여:

- `401 Unauthorized`
- `Invalid credentials`
- `LOGIN_FAILED` Audit Log

를 확인한다.

---

### Valid ADMIN Token

`POST /admin/auth/login`을 호출하여 정상 ADMIN JWT를 발급받고,  
관리자 API 테스트에 사용한다.

ADMIN Token 발급 로직은 pytest Fixture로 구성하여  
필요한 테스트에서 재사용한다.

---

### Invalid Token

형식이 올바르지 않은 명시적인 Invalid Token Test Data를 사용한다.

---

### Expired Token

실제 서비스 JWT 구조와 동일한 Claims를 사용하되  
`exp`를 과거 시각으로 설정하여 만료된 JWT를 생성한다.

이를 통해 만료 토큰 시나리오를 반복 가능한 형태로 검증한다.

ADMIN 비밀번호와 JWT Secret은 `.env` 환경변수에서 읽으며  
테스트 코드와 GitHub 저장소에는 저장하지 않는다.

---

## 9. DB Verification Strategy

pytest에서 PostgreSQL에 직접 연결하여  
API 결과를 교차검증한다.

### USER 데이터 검증

- 생성된 username 존재 여부
- `role = USER`
- status 값
- password_hash 저장 여부
- 평문 password 미저장 여부
- 중복 username row 개수
- Invalid Status 요청 후 기존 DB 값 유지 여부
- 상태 변경 후 DB 반영 여부
- 테스트 종료 후 Cleanup 여부

DB 관련 공통 기능은 `db_helper.py`에 분리하여 재사용한다.

```text
get_user_by_username()
get_user_status()
update_user_status()
count_users_by_username()
delete_user_by_username()
```

API 검증과 DB 검증을 함께 수행함으로써  
HTTP Response만 정상이고 실제 DB 상태는 예상과 다른 경우까지  
확인할 수 있도록 구성하였다.

---

## 10. Audit Log Verification Strategy

로그인 및 인가 실패 시 API Response뿐 아니라  
PostgreSQL의 `audit_logs` 테이블도 함께 확인한다.

검증 대상:

- event_type
- username
- endpoint

주요 Event:

```text
LOGIN_SUCCESS
LOGIN_FAILED
ACCESS_DENIED
```

Audit Log 검증에서는 단순히 전체 테이블의 최신 row만 조회하지 않는다.

테스트 API 호출 전에 마지막 Audit Log `id`를 확보하고,  
API 호출 이후 생성된 row에서 다음 조건을 사용한다.

```text
id > 요청 전 마지막 id
event_type 일치
username 일치
endpoint 일치
```

이를 통해 기존 로그 또는 다른 테스트에서 생성된 로그와  
현재 테스트에서 생성된 Audit Log가 혼동되는 것을 줄인다.

Token이 없거나 유효하지 않아 사용자 식별이 불가능한 경우에는  
`username IS NULL` 조건으로 ACCESS_DENIED 로그를 검증한다.

---

## 11. Setup / Cleanup Strategy

pytest Fixture와 Helper를 역할에 따라 분리하였다.

### Fixture

Fixture는 공통 환경 또는  
Setup / Teardown Lifecycle 관리가 필요한 경우 사용한다.

주요 Fixture:

| Fixture | 역할 |
| --- | --- |
| `base_url` | 테스트 대상 API 주소 제공 |
| `db_connection` | PostgreSQL 연결 / 종료 |
| `admin_user` | 환경변수 기반 ADMIN Credential 제공 |
| `admin_token` | 정상 ADMIN JWT 발급 |
| `expired_admin_token` | 만료된 ADMIN JWT 생성 |
| `default_user` | 테스트 USER 동적 생성 / Cleanup |
| `inactive_user` | 테스트 USER INACTIVE Setup / ACTIVE Restore |

### `default_user` Setup / Teardown

```text
Setup
  ↓
Dynamic USER Create
  ↓
yield username/password
  ↓
Test
  ↓
finally
  ↓
USER Cleanup
```

테스트 중 Assertion이 실패해도 `finally`에서 Cleanup을 수행한다.

### `inactive_user` Setup / Restore

```text
default_user
     ↓
Original Status 확인
     ↓
INACTIVE Setup
     ↓
Test
     ↓
Original Status Restore
     ↓
default_user Cleanup
```

`inactive_user`가 끝난 뒤 ACTIVE로 복원되고,  
그 이후 상위 `default_user` fixture에서 최종적으로 USER를 삭제한다.

### USER Lifecycle Cleanup

USER Lifecycle에서 생성한 계정도 테스트 성공 / 실패 여부와 관계없이 정리한다.

```python
try:
    # USER Lifecycle
finally:
    cleanup_user(...)
```

Cleanup은 제품 DELETE 기능 검증이 아니며  
자동화 실행 환경을 원상복구하기 위한 Teardown 목적이다.

---

## 12. BUG-001 Regression

BUG-001은 USER Lifecycle 내부 Regression Step으로 자동화하였다.

### 기존 문제

중복 username 생성 요청 시 PostgreSQL UNIQUE Constraint에서

```text
psycopg.errors.UniqueViolation
```

이 발생했으나 예외가 처리되지 않아:

```text
500 Internal Server Error
```

가 반환되었다.

### 수정 후 기대 동작

- 중복 username 요청 시 `409 Conflict`
- `detail = "Username already exists"`
- 동일 username의 추가 row 미생성
- 서버 `5xx` 미발생

### 자동화 방식

Lifecycle CREATE Step에서 생성한 USER의 username을 그대로 사용하여  
동일한 생성 요청을 다시 수행한다.

```text
CREATE USER
    ↓
DB row = 1
    ↓
동일 username으로 재요청
    ↓
409 Conflict
    ↓
DB row = 1 유지
```

추가 테스트 계정을 만들지 않고  
동일 Lifecycle 데이터로 BUG-001 Regression을 검증한다.

### Regression Result

**PASS**

확인 항목:

- 동일 username 재요청 시 `409 Conflict`
- `Username already exists` 반환
- 동일 username의 추가 USER row 미생성
- 기존 USER row 수 유지
- 서버 `5xx` 미발생
- `DUPLICATE USERNAME` Step PASS

BUG-001은 수정 확인 후 전체 Regression Suite에 포함하여  
반복 검증할 수 있도록 구성하였다.

---

## 13. Test Structure

```text
tests/
├─ data/
│  ├─ __init__.py
│  └─ test_data.py
│
├─ helpers/
│  ├─ __init__.py
│  ├─ db_helper.py
│  └─ user_helper.py
│
├─ conftest.py
├─ test_user_auth.py
├─ test_admin_auth.py
├─ test_authorization.py
└─ test_users.py
```

### 역할

#### `conftest.py`

- API Base URL
- DB Connection
- ADMIN Credential
- ADMIN Token
- Expired ADMIN Token
- Dynamic USER Setup / Cleanup
- INACTIVE USER 상태 Setup / Restore

#### `test_data.py`

- 테스트 USER username prefix
- 테스트용 password
- Wrong Password
- Invalid Status
- Invalid Token 등 공개 가능한 정적 테스트 데이터

#### `db_helper.py`

- USER DB 조회
- USER 상태 조회 / 변경
- username row count 조회
- Audit Log 조회
- 테스트 데이터 Cleanup

#### `user_helper.py`

- USER 생성 검증
- BUG-001 중복 username 검증
- Invalid Status 검증
- USER 상태 변경 검증
- USER 목록 검증
- Step PASS / FAIL 처리
- Lifecycle Cleanup

#### `test_user_auth.py`

- Dynamic USER 정상 로그인
- Wrong Password 로그인
- INACTIVE USER 로그인
- ADMIN의 USER 로그인 경로 접근 차단
- USER Audit Log 검증

#### `test_admin_auth.py`

- ADMIN 로그인
- ADMIN 로그인 실패
- ADMIN Audit Log 검증

#### `test_authorization.py`

- No Token
- Invalid Token
- Expired Token
- ACCESS_DENIED Audit Log

#### `test_users.py`

- USER Lifecycle 실행
- `user_helper.py` 검증 함수 순차 호출
- 중간 FAIL 시 Lifecycle 즉시 중단
- `finally` 기반 Cleanup

---

## 14. Fresh Database Reproducibility

기존 환경에서만 테스트가 통과하는지 확인하기 위해  
PostgreSQL Volume을 제거한 신규 Database에서도 Full Regression을 수행하였다.

### 검증 순서

```text
docker compose down -v
        ↓
기존 PostgreSQL Volume 제거
        ↓
setup.ps1
        ↓
신규 Database / ADMIN 초기화
        ↓
python -m pytest .\tests -v
        ↓
Full Regression
```

### 결과

```text
10 Passed
0 Failed
0 Errors
```

신규 Database에는 기존 일반 USER가 존재하지 않았지만,  
pytest fixture가 테스트에 필요한 USER를 동적으로 생성하여  
전체 Test Suite가 정상적으로 수행되었다.

이를 통해 다음을 확인하였다.

- 기존 일반 USER 사전 생성 불필요
- 동적 USER Setup 정상
- INACTIVE 상태 Setup / Restore 정상
- USER Lifecycle 정상
- 테스트 종료 후 Cleanup 정상
- 신규 Database에서도 동일 Regression 실행 가능

---

## 15. HTML Test Report & Full Regression Result

전체 자동화 테스트 수행 결과는  
`pytest-html`을 이용하여 HTML Report로 생성한다.

HTML Report의 목적은 단순 실행 로그를 보관하는 것이 아니라  
전체 Regression 수행 결과와 Lifecycle 내부 검증 결과를  
하나의 결과물에서 확인할 수 있도록 하는 것이다.

### Report 확인 항목

- 전체 pytest Test Function 수
- PASS / FAIL 결과
- 테스트별 실행 시간
- 실패 테스트 Assertion / Traceback
- USER Lifecycle 실행 결과
- Lifecycle 내부 Step별 PASS / FAIL 로그
- Cleanup 수행 로그

### USER Lifecycle Report

`test_user_lifecycle`은 pytest 기준 하나의 Test Function이다.

따라서 HTML 결과에서는 하나의 테스트 항목으로 표시되며  
Lifecycle 내부 검증 결과는 Captured Output에서 확인한다.

```text
[PASS] CREATE USER
[PASS] DUPLICATE USERNAME
[PASS] INVALID USER STATUS
[PASS] UPDATE ACTIVE -> INACTIVE
[PASS] UPDATE INACTIVE -> ACTIVE
[PASS] GET USER LIST
[CLEANUP] Test User
```

중간 Step에서 Assertion이 실패하면  
이후 Lifecycle Step은 실행하지 않으며  
`finally`에서 생성한 테스트 데이터를 Cleanup한다.

### Full Regression Result

| 항목 | 결과 |
| --- | ---: |
| pytest Test Function | 10 |
| Passed | 10 |
| Failed | 0 |
| Errors | 0 |

신규 Database 환경에서도 동일하게:

```text
10 Passed
0 Failed
0 Errors
```

를 확인하였다.

### Report 생성 명령

```powershell
python -m pytest .\tests -v --capture=tee-sys --html=.\reports\full_test_report.html --self-contained-html
```

`--capture=tee-sys`를 사용하여 Lifecycle의  
`[PASS]`, `[FAIL]`, `[CLEANUP]` 출력을 터미널과 HTML Report에서 함께 확인한다.

### Report 파일

```text
reports/
└─ full_test_report.html
```

Report는 포트폴리오에서 다음 내용을 확인하는 자료로 사용한다.

- 자동화 테스트가 실제 실행 가능한 상태인지
- 전체 Regression 결과
- 인증 / 인가 / USER 관리 테스트 결과
- Lifecycle 내부 Step 결과
- BUG-001 Regression 결과
- 테스트 데이터 Cleanup 결과

---

## 16. Execution

### 기본 Full Regression

프로젝트 루트에서 실행한다.

```powershell
python -m pytest .\tests -v
```

Lifecycle 내부 Step 로그까지 터미널에서 확인하려면:

```powershell
python -m pytest .\tests -v -s
```

### HTML Report 생성

```powershell
python -m pytest .\tests -v --capture=tee-sys --html=.\reports\full_test_report.html --self-contained-html
```

### 실행 흐름

```text
Docker / PostgreSQL / API 실행 확인
                ↓
전체 pytest Suite 실행
                ↓
Authentication Test
                ↓
Dynamic USER Setup
                ↓
Authorization Test
                ↓
USER Lifecycle Test
                ↓
DB / Audit Log 검증
                ↓
Restore / Cleanup
                ↓
전체 수행 종료
                ↓
HTML Test Report 생성
```

---

## 17. Automation Goal

본 프로젝트의 자동화 목표는 자동화 비율 자체를 높이는 것이 아니다.

**수동 테스트에서 식별한 핵심 위험과 실제 결함을 선정하고,  
API + DB + Audit Log를 연결한 반복 가능한 Regression Test로 전환하는 것**을 목표로 한다.

인증 / 인가 테스트는 개별 pytest Test Function으로 구성하고,  
테스트에 필요한 일반 USER는 실행 시 동적으로 생성하여  
기존 Database 데이터에 대한 의존성을 줄였다.

USER 관리 기능은 API별로 테스트 데이터를 반복 생성하는 대신  
하나의 테스트 USER를 Lifecycle 전체에서 재사용하도록 구성하였다.

이를 통해 다음을 확인하였다.

- 인증 / 인가 핵심 시나리오 반복 Regression
- API Response와 DB 상태 교차검증
- Audit Log 자동 검증
- BUG-001 Regression 자동화
- 반복되는 USER 검증 로직 분리
- 테스트 데이터 Setup / Cleanup
- 기존 일반 USER 데이터 의존성 제거
- 신규 Database 환경에서 Full Regression 재현
- 중간 실패 시 Cleanup 수행
- 전체 Regression 결과 HTML Report 제공

자동화는 수동 테스트를 대체하기 위한 목적이 아니라,  
**반복 수행 가치가 높은 핵심 위험을 안정적으로 재검증하기 위한 수단**으로 사용하였다.