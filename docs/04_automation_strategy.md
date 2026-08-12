# 04. Automation Strategy

## 1. 목적

Technical QA Lab의 자동화는 수동 테스트 전체를 코드로 복제하는 것이 목적이 아니다.

반복 수행 가치가 높은 핵심 인증 / 인가 / 계정 관리 / 데이터 / Audit Log 시나리오를
pytest로 자동화하여 다음 역량을 검증한다.

* API 자동 회귀 테스트
* JWT 인증 / 인가 검증
* API Response와 PostgreSQL 데이터 교차 검증
* Audit Log 자동 검증
* 테스트 데이터 Setup / Cleanup
* 실제 결함의 Regression 자동화
* 기능 단위 모듈을 조합한 Lifecycle 기반 자동화
* 전체 자동화 수행 결과의 HTML Test Report 생성

---

## 2. Automation Tool

자동화 도구는 **pytest**를 사용한다.

Postman Collection은 관리자 API 호출, JWT Negative Scenario,
수동 재현 및 요청 보관 용도로 유지한다.

전체 자동화 수행 결과는 **pytest-html**을 사용하여
PASS / FAIL 결과를 HTML Report로 생성한다.

### pytest를 선택한 이유

1. HTTP Response뿐 아니라 PostgreSQL 데이터까지 하나의 테스트 흐름에서 검증할 수 있다.
2. Audit Log 조회를 API 동작과 연결하여 자동 검증하기 쉽다.
3. 테스트 데이터 생성 / 상태 변경 / 정리를 코드로 제어할 수 있다.
4. BUG-001과 같은 결함 Regression을 반복 실행하기 쉽다.
5. 기능별 검증 함수를 모듈화하고 Lifecycle 형태로 조합할 수 있다.
6. 전체 자동화 결과를 Test Report 형태로 남길 수 있다.
7. 향후 CI 연동이 필요한 경우 확장하기 쉽다.

### 도구 역할 분리

| 도구          | 역할                                      |
| ----------- | --------------------------------------- |
| Swagger     | Public API 명세 및 Smoke 확인                |
| Postman     | ADMIN API / JWT / Negative 수동 시나리오 및 재현 |
| PostgreSQL  | 데이터 / Constraint / Audit Log 직접 검증      |
| pytest      | 핵심 기능 및 결함 Regression 자동화               |
| pytest-html | 전체 자동화 수행 결과 HTML Report 생성             |

---

## 3. Automation Selection Criteria

다음 조건을 기준으로 자동화 대상을 선정하였다.

### 자동화 우선

* 인증 / 인가 등 실패 영향도가 높은 기능
* 릴리스마다 반복 확인할 가능성이 높은 기능
* 입력과 기대 결과가 명확하여 자동 판정 가능한 기능
* API 결과와 DB / Audit Log를 함께 검증할 가치가 있는 기능
* 실제 결함 발생 이력이 있어 Regression 가치가 높은 기능
* 하나의 사용자 흐름에서 연속적으로 검증할 가치가 높은 기능

### 수동 유지

* UI / 문서 노출 여부처럼 육안 확인 가치가 높은 항목
* 동일 인증 조건을 엔드포인트별로 반복 확인하는 상세 영향 범위 테스트
* DB Constraint를 직접 깨뜨리는 일회성 정책 검증
* 최초 환경 구성 및 Docker 재현성 확인

---

## 4. Automation Scope

수동 테스트에서 선정한 **15개의 핵심 검증 의도**를 자동화하였다.

인증 / 인가 기능은 독립 pytest Test Function으로 구성하고,
USER 관리 기능은 테스트 데이터의 반복 생성 / 삭제를 줄이기 위해
하나의 `test_user_lifecycle` 내부에서 기능별 Step을 순차 실행하도록 구성하였다.

최종 구성은 다음과 같다.

* 독립 pytest Test Function: **9개**
* USER Lifecycle Test Function: **1개**
* USER Lifecycle 내부 검증 Step: **6개**
* 전체 pytest Test Function: **10개**
* 전체 핵심 자동화 검증 의도: **15개**

| Pytest Test / Step                     | Manual TC  | 검증 포인트                                   |
| -------------------------------------- | ---------- | ---------------------------------------- |
| `test_user_login_success`              | TC01, TC33 | 200 / USER 정보 / LOGIN_SUCCESS            |
| `test_user_login_wrong_password`       | TC02, TC35 | 401 / Invalid credentials / LOGIN_FAILED |
| `test_user_login_inactive`             | TC04       | 403 / Account is inactive                |
| `test_admin_blocked_from_user_login`   | TC05       | USER 로그인 경로에서 ADMIN 차단                   |
| `test_admin_login_success`             | TC11, TC36 | 200 / ADMIN JWT / LOGIN_SUCCESS          |
| `test_admin_login_failure`             | TC07, TC37 | 401 / token 미발급 / LOGIN_FAILED           |
| `test_admin_api_without_token`         | TC09, TC40 | 401 / ACCESS_DENIED / endpoint           |
| `test_admin_api_invalid_token`         | TC14, TC41 | 401 / Invalid Token / ACCESS_DENIED      |
| `test_admin_api_expired_token`         | TC26, TC42 | 401 / Expired Token / ACCESS_DENIED      |
| `test_user_lifecycle` - CREATE         | TC15, TC32 | 201 / role USER / DB / password hash     |
| `test_user_lifecycle` - DUPLICATE      | TC16, TC27 | 409 / 중복 row 미생성 / BUG-001 Regression    |
| `test_user_lifecycle` - INVALID STATUS | TC23       | 422 / DB 값 미변경                           |
| `test_user_lifecycle` - INACTIVE       | TC19       | 200 / INACTIVE / DB 반영                   |
| `test_user_lifecycle` - ACTIVE         | TC20       | 200 / ACTIVE / DB 반영                     |
| `test_user_lifecycle` - GET USERS      | TC24       | USER 목록 / ADMIN 및 password_hash 미노출      |

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

* 생성된 USER의 API Response 및 DB 저장 결과
* 동일 username 재요청 시 BUG-001 Regression
* 잘못된 status 입력 시 Validation
* ACTIVE / INACTIVE 상태 전환
* 상태 변경 결과의 DB 반영
* USER 목록 조회 결과
* ADMIN 및 password_hash 미노출

제품 요구사항에는 USER DELETE 기능이 존재하지 않으므로,
Lifecycle 마지막의 DB 삭제는 제품 기능 테스트가 아닌
**테스트 데이터 Cleanup 목적**으로만 수행한다.

---

## 6. Modular Test Design

USER 관리 기능의 실제 검증 로직은
`user_helper.py`의 독립 함수로 분리하였다.

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

`test_users.py`는 세부 API 검증 코드를 직접 반복하지 않고,
각 기능 모듈을 Lifecycle 순서에 따라 호출하는 역할을 담당한다.

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

각 기능 함수는 다음 범위를 검증한다.

```text
API Request
    ↓
HTTP Status
    ↓
Response Body
    ↓
DB 상태
```

공통 실행 함수 `run_step()`은 각 기능 모듈의 실행 결과를
`[PASS]` 또는 `[FAIL]`로 출력한다.

중간 단계에서 Assertion이 실패할 경우 예외를 다시 발생시켜
Lifecycle을 즉시 중단한다.

이후 `finally` 구문에서 Cleanup을 수행하여
실패 시에도 생성한 테스트 USER가 DB에 남지 않도록 구성하였다.

---

## 7. Test Data Strategy

자동화 간 데이터 의존성을 최소화하되,
동일 USER Lifecycle 내부에서는 하나의 테스트 데이터를 재사용한다.

* 고정된 `user_id`에 의존하지 않는다.
* 테스트용 username은 실행마다 동적으로 생성한다.
* Lifecycle 시작 시 테스트 USER를 1회 생성한다.
* 생성된 USER의 `id`는 API Response에서 확보한다.
* 동일 USER를 중복 username / Validation / 상태 변경 / 목록 조회에 재사용한다.
* 기능별 검증을 위해 USER를 반복 생성 / 삭제하지 않는다.
* Lifecycle 중간에 FAIL이 발생해도 `finally` Cleanup을 수행한다.
* Cleanup은 제품 DELETE 기능이 아닌 테스트 Teardown 성격으로 사용한다.
* 기존 `admin01`은 시스템 ADMIN Fixture로 사용한다.
* ADMIN 비밀번호 및 JWT Secret은 환경변수에서 읽는다.
* 공개 가능한 정적 테스트 값은 `test_data.py`에서 관리한다.

---

## 8. Authentication / Token Strategy

### Valid ADMIN Token

`POST /admin/auth/login`을 호출하여 정상 ADMIN JWT를 발급받고,
관리자 API 테스트에 사용한다.

ADMIN Token 발급 로직은 pytest Fixture로 구성하여
필요한 테스트에서 재사용한다.

### Invalid Token

형식이 올바르지 않은 명시적인 Invalid Token Test Data를 사용한다.

### Expired Token

실제 서비스 JWT 구조와 동일한 Claims를 사용하되
`exp`를 과거 시각으로 설정하여 만료된 JWT를 생성한다.

이를 통해 이미 만료된 토큰을 항상 재현 가능하게 검증한다.

ADMIN 비밀번호와 JWT Secret은 `.env` 환경변수에서 읽으며
테스트 코드와 GitHub 저장소에는 저장하지 않는다.

---

## 9. DB Verification Strategy

pytest에서 PostgreSQL에 직접 연결하여
API 결과를 교차 검증한다.

### USER 데이터 검증

* 생성된 username 존재 여부
* `role = USER`
* status 값
* password_hash 저장 여부
* 평문 password 미저장 여부
* 중복 username row 개수
* Invalid Status 요청 후 기존 DB 값 유지 여부
* 상태 변경 후 DB 반영 여부

DB 관련 공통 기능은 `db_helper.py`에 분리하여 재사용한다.

```text
get_user_by_username()
get_user_status()
update_user_status()
count_users_by_username()
delete_user_by_username()
```

API 검증과 DB 검증을 함께 수행함으로써
HTTP Response만 정상이고 실제 DB 상태는 잘못된 경우까지
확인할 수 있도록 구성하였다.

---

## 10. Audit Log Verification Strategy

로그인 및 인가 실패 시 API Response뿐 아니라
PostgreSQL의 `audit_logs` 테이블도 함께 확인한다.

검증 대상은 다음과 같다.

* event_type
* username
* endpoint

주요 Event는 다음과 같다.

```text
LOGIN_SUCCESS
LOGIN_FAILED
ACCESS_DENIED
```

Audit Log 검증에서는 단순히 전체 테이블의 최신 row만 조회하지 않는다.

테스트 API 호출 전에 마지막 Audit Log `id`를 확보하고,
API 호출 이후 생성된 row 중 다음 조건을 함께 사용한다.

```text
id > 요청 전 마지막 id
event_type 일치
username 일치
endpoint 일치
```

이를 통해 기존 로그 또는 다른 테스트에서 생성된 로그와
현재 테스트 로그가 혼동되는 것을 방지한다.

Token이 없거나 유효하지 않아 사용자 식별이 불가능한 경우에는
`username IS NULL` 조건으로 ACCESS_DENIED 로그를 검증한다.

---

## 11. Setup / Cleanup Strategy

pytest Fixture와 Helper를 역할에 따라 분리하였다.

### Fixture

Fixture는 공통 환경 또는 Setup / Teardown Lifecycle이 필요한 경우 사용한다.

예:

* DB Connection
* ADMIN Credential
* ADMIN Token
* Expired ADMIN Token
* INACTIVE USER 상태 Setup / Restore

단순한 username, wrong password, invalid token 등의 정적 데이터는
불필요한 Fixture로 감싸지 않고 `test_data.py`에서 직접 사용한다.

### Cleanup

USER Lifecycle에서 생성한 테스트 계정은
테스트 성공 / 실패 여부와 관계없이 정리한다.

```python
try:
    # Lifecycle
finally:
    cleanup_user(...)
```

중간 Step에서 FAIL이 발생하더라도 `finally`가 실행되므로,
테스트 데이터가 PostgreSQL에 누적되는 것을 방지한다.

Cleanup은 제품의 DELETE 기능 검증이 아니며,
자동화 실행 환경을 원상복구하기 위한 Teardown 용도이다.

---

## 12. BUG-001 Regression

BUG-001은 USER Lifecycle 내부의 Regression Step으로 자동화하였다.

### 기존 문제

중복 username 생성 요청 시 PostgreSQL UNIQUE Constraint에서

`psycopg.errors.UniqueViolation`

이 발생했으나 예외가 처리되지 않아

`500 Internal Server Error`

가 반환되었다.

### 수정 후 기대 동작

* 중복 username 요청 시 `409 Conflict`
* `detail = "Username already exists"`
* 동일 username의 추가 row 미생성
* 서버 `5xx` 미발생

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

추가 테스트 계정을 생성하지 않고
동일 Lifecycle 데이터로 BUG-001 Regression을 반복 검증한다.

### Regression Execution Result

**PASS**

Full Regression 실행을 통해 다음 항목을 확인하였다.

* 동일 username 재요청 시 `409 Conflict` 반환
* `detail = "Username already exists"` 반환
* 동일 username의 추가 USER row 미생성
* 기존 USER row 수 유지
* 서버 `5xx` 미발생
* USER Lifecycle의 `DUPLICATE USERNAME` Step PASS

Full Regression 결과:

```text
[PASS] CREATE USER
[PASS] DUPLICATE USERNAME
```

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

* DB Connection
* ADMIN Credential
* ADMIN Token
* Expired ADMIN Token
* USER 상태 Setup / Restore
* 공통 테스트 환경

#### `test_data.py`

* 일반 USER Credential
* Wrong Password
* 테스트 USER 생성용 데이터
* Invalid Status
* Invalid Token 등 공개 가능한 정적 테스트 데이터

#### `db_helper.py`

* USER DB 조회
* USER 상태 조회 / 변경
* username row count 조회
* Audit Log 조회
* 테스트 데이터 Cleanup

#### `user_helper.py`

* USER 생성 검증
* BUG-001 중복 username 검증
* Invalid Status 검증
* USER 상태 변경 검증
* USER 목록 검증
* 기능 Step PASS / FAIL 처리
* Lifecycle Cleanup

#### `test_user_auth.py`

* USER 로그인
* USER 로그인 예외
* ADMIN의 USER 로그인 경로 접근 차단
* USER Audit Log

#### `test_admin_auth.py`

* ADMIN 로그인
* ADMIN 로그인 실패
* ADMIN Audit Log

#### `test_authorization.py`

* No Token
* Invalid Token
* Expired Token
* ACCESS_DENIED Audit

#### `test_users.py`

* USER Lifecycle 실행
* `user_helper.py`의 기능 모듈 순차 호출
* 중간 FAIL 시 Lifecycle 즉시 중단
* `finally` 기반 Cleanup

---

## 14. HTML Test Report & Full Regression Result

전체 자동화 테스트 수행 결과는
`pytest-html`을 이용하여 HTML Report로 생성한다.

HTML Report의 목적은 단순 실행 로그를 보관하는 것이 아니라,
전체 Regression 수행 결과와 Lifecycle 내부 검증 결과를
하나의 결과물에서 확인할 수 있도록 하는 것이다.

### Report 확인 항목

* 전체 pytest Test Function 수
* PASS / FAIL 결과
* 테스트별 실행 시간
* 실패 테스트의 Assertion / Traceback
* USER Lifecycle 실행 결과
* Lifecycle 내부 Step별 PASS / FAIL 로그
* Cleanup 수행 로그

### USER Lifecycle Report

`test_user_lifecycle`은 pytest 기준으로 하나의 Test Function이다.

따라서 HTML 결과 테이블에서는 하나의 테스트 항목으로 표시되며,
Lifecycle 내부 기능 검증 결과는 해당 테스트의 Captured Output에서 확인한다.

Full Regression에서 다음 Lifecycle Step이 모두 PASS하였다.

```text
[PASS] CREATE USER
[PASS] DUPLICATE USERNAME
[PASS] INVALID USER STATUS
[PASS] UPDATE ACTIVE -> INACTIVE
[PASS] UPDATE INACTIVE -> ACTIVE
[PASS] GET USER LIST
[CLEANUP] Test User
```

중간 Step에서 Assertion이 실패할 경우
이후 Lifecycle Step은 실행하지 않으며,
`finally`를 통해 생성한 테스트 데이터를 Cleanup한다.

### Full Regression Result

전체 `tests/` 디렉터리를 대상으로 Full Regression을 수행하였다.

| 항목                   | 결과 |
| -------------------- | -: |
| pytest Test Function | 10 |
| Passed               | 10 |
| Failed               |  0 |

전체 pytest Test Function이 PASS하였으며,
USER Lifecycle 내부 6개 Step과 Cleanup도 정상 수행되었다.

### Report 생성 기준

최종 HTML Report는 특정 테스트 파일만 실행한 결과가 아니라
**전체 Test Suite를 Full Run한 결과**를 기준으로 생성한다.

```powershell
python -m pytest .\tests -v --capture=tee-sys --html=.\reports\full_test_report.html --self-contained-html
```

HTML Report 생성 시 `--capture=tee-sys`를 사용하여
Lifecycle 내부의 `[PASS]`, `[FAIL]`, `[CLEANUP]` 출력을
터미널과 HTML Report에서 함께 확인할 수 있도록 한다.

### Report 파일

```text
reports/
└─ full_test_report.html
```

단일 HTML 파일로 생성하여
별도 CSS / Asset 파일 없이 결과를 확인할 수 있도록 구성한다.

Report는 포트폴리오에서 다음 내용을 증빙하는 자료로 활용한다.

* 자동화 테스트가 실제 실행 가능한 상태임을 확인
* 전체 Regression 결과 확인
* 인증 / 인가 / USER 관리 테스트 결과 확인
* Lifecycle 내부 Step 수행 결과 확인
* BUG-001 Regression 결과 확인
* 테스트 데이터 Cleanup 여부 확인

---

## 15. Execution

### 기본 전체 자동화 실행

전체 pytest Test Suite의 동작을 확인하는 경우 다음 명령을 사용한다.

```powershell
python -m pytest .\tests -v -s
```

`-v` 옵션으로 Test Function 단위 결과를 확인하고,
`-s` 옵션으로 USER Lifecycle 내부의 Step 로그를 실시간 확인한다.

### HTML Report 생성용 Full Regression 실행

최종 Test Report 생성 시에는 다음 명령을 사용한다.

```powershell
python -m pytest .\tests -v --capture=tee-sys --html=.\reports\full_test_report.html --self-contained-html
```

HTML Report 생성 시 `-s` 대신 `--capture=tee-sys`를 사용한다.

이를 통해 Lifecycle의 `[PASS]`, `[FAIL]`, `[CLEANUP]` 출력을
터미널에서 확인하면서 동시에 Test Report에서도 사용할 수 있도록
Captured Output을 유지한다.

### 실행 흐름

```text
Docker / PostgreSQL / API 실행 상태 확인
                ↓
전체 pytest Suite 실행
                ↓
Authentication Test
                ↓
Authorization Test
                ↓
USER Lifecycle Test
                ↓
DB / Audit Log 검증
                ↓
Test Data Cleanup
                ↓
전체 수행 종료
                ↓
HTML Test Report 생성
```

최종 자동화 결과는 `reports/full_test_report.html`을 열어 확인한다.

---

## 16. Automation Goal

본 프로젝트의 자동화 목표는 자동화 비율 자체를 높이는 것이 아니다.

**수동 테스트에서 식별한 핵심 위험과 실제 결함을 선정하고,
API + DB + Audit Log를 연결한 반복 가능한 Regression Test로 전환하는 것**을 목표로 한다.

인증 / 인가 영역은 테스트 간 독립성을 유지할 수 있도록
개별 pytest Test Function으로 구성하였다.

USER 관리 기능은 개별 API마다 테스트 데이터를 반복 생성하는 대신,
하나의 테스트 USER를 Lifecycle 전체에서 재사용하도록 구성하였다.

이를 통해 다음을 확인하였다.

* 인증 / 인가 핵심 시나리오의 반복 Regression
* API Response와 DB 상태 교차검증
* Audit Log 자동 검증
* 실제 결함 BUG-001의 Regression 자동화
* 기능 검증 로직의 모듈화
* 테스트 데이터 생성 / 삭제 반복 감소
* 중간 실패 시 데이터 Cleanup 보장
* 전체 Regression 결과의 HTML Report 제공

자동화는 수동 테스트를 대체하기 위한 목적이 아니라,
**반복 수행 가치가 높은 핵심 위험을 안정적으로 재검증하기 위한 수단**으로 사용하였다.
