# 04. Automation Strategy

## 1. 목적

Technical QA Lab의 자동화는 수동 테스트 전체를 코드로 복제하는 것이 목적이 아니다.

반복 수행 가치가 높은 핵심 인증 / 인가 / 계정 관리 / 데이터 / Audit Log 시나리오를
pytest로 자동화하여 다음 역량을 검증한다.

- API 자동 회귀 테스트
- JWT 인증 / 인가 검증
- API Response와 PostgreSQL 데이터 교차 검증
- Audit Log 자동 검증
- 테스트 데이터 Setup / Cleanup
- 실제 결함의 Regression 자동화

---

## 2. Automation Tool

자동화 도구는 **pytest**를 사용한다.

Postman Collection은 관리자 API 호출, JWT Negative Scenario,
수동 재현 및 요청 보관 용도로 유지한다.

### pytest를 선택한 이유

1. HTTP Response뿐 아니라 PostgreSQL 데이터까지 한 테스트에서 검증할 수 있다.
2. Audit Log 조회를 API 동작과 연결하여 자동 검증하기 쉽다.
3. 테스트 데이터 생성 / 상태 변경 / 정리를 코드로 제어할 수 있다.
4. BUG-001과 같은 결함 Regression을 반복 실행하기 쉽다.
5. 향후 CI 연동이 필요한 경우 확장하기 쉽다.

### 도구 역할 분리

| 도구 | 역할 |
|---|---|
| Swagger | Public API 명세 및 Smoke 확인 |
| Postman | ADMIN API / JWT / Negative 수동 시나리오 및 재현 |
| PostgreSQL | 데이터 / Constraint / Audit Log 직접 검증 |
| pytest | 핵심 기능 및 결함 Regression 자동화 |

---

## 3. Automation Selection Criteria

다음 조건을 기준으로 자동화 대상을 선정한다.

### 자동화 우선

- 인증 / 인가 등 실패 영향도가 높은 기능
- 릴리스마다 반복 확인할 가능성이 높은 기능
- 입력과 기대 결과가 명확하여 자동 판정 가능한 기능
- API 결과와 DB / Audit Log를 함께 검증할 가치가 있는 기능
- 실제 결함 발생 이력이 있어 Regression 가치가 높은 기능

### 수동 유지

- UI/문서 노출 여부처럼 육안 확인 가치가 높은 항목
- 동일 인증 조건을 엔드포인트별로 반복 확인하는 상세 영향 범위 테스트
- DB Constraint를 직접 깨뜨리는 일회성 정책 검증
- 최초 환경 구성 및 Docker 재현성 확인

---

## 4. Automation Scope

자동화 대상은 총 **15개 pytest 시나리오**로 선정한다.

| Pytest Scenario | Manual TC | 검증 포인트 |
|---|---|---|
| `test_user_login_success` | TC01, TC33 | 200 / USER 정보 / LOGIN_SUCCESS |
| `test_user_login_wrong_password` | TC02, TC35 | 401 / Invalid credentials / LOGIN_FAILED |
| `test_user_login_inactive` | TC04 | 403 / Account is inactive |
| `test_admin_blocked_from_user_login` | TC05 | USER 로그인 경로에서 ADMIN 차단 |
| `test_admin_login_success` | TC11, TC36 | 200 / ADMIN JWT / LOGIN_SUCCESS |
| `test_admin_login_failure` | TC07, TC37 | 401 / token 미발급 / LOGIN_FAILED |
| `test_admin_api_without_token` | TC09, TC40 | 401 / ACCESS_DENIED / endpoint |
| `test_admin_api_invalid_token` | TC14, TC41 | 401 / Invalid token / ACCESS_DENIED |
| `test_admin_api_expired_token` | TC26, TC42 | 401 / Expired token / ACCESS_DENIED |
| `test_create_user` | TC15, TC32 | 201 / role USER / DB / password hash |
| `test_duplicate_username` | TC16, TC27 | 409 / 중복 row 미생성 / BUG-001 Regression |
| `test_update_user_inactive` | TC19 | 200 / INACTIVE / DB 반영 |
| `test_update_user_active` | TC20 | 200 / ACTIVE / DB 반영 |
| `test_invalid_user_status` | TC23 | 422 / DB 값 미변경 |
| `test_get_users` | TC24 | USER 목록 / ADMIN 및 password_hash 미노출 |

---

## 5. Test Design

자동화 테스트는 가능한 경우 다음 순서로 검증한다.

```text
Precondition / Test Data Setup
        ↓
API Request
        ↓
HTTP Status 검증
        ↓
Response Body 검증
        ↓
DB / Audit Log 검증
        ↓
Test Data Cleanup
```

수동 TC에서는 API 검증과 DB / Audit 검증을 별도 TC로 관리할 수 있지만,
pytest에서는 하나의 사용자 행동으로 발생한 결과를 하나의 자동화 시나리오에서 연결하여 검증한다.

---

## 6. Test Data Strategy

자동화 간 데이터 의존성을 최소화한다.

- 고정된 `user_id`에 의존하지 않는다.
- 테스트용 username은 실행마다 충돌하지 않도록 생성한다.
- 테스트에서 생성한 USER의 id를 Response 또는 DB에서 확보하여 후속 검증에 사용한다.
- 상태 변경 테스트는 필요한 상태를 Setup 단계에서 명시적으로 만든다.
- 테스트 종료 후 생성 데이터는 가능한 범위에서 정리한다.
- 기존 `admin01`은 시스템 ADMIN Fixture로 사용하되 비밀번호는 환경변수에서 읽는다.

---

## 7. Authentication / Token Strategy

### Valid ADMIN Token

`POST /admin/auth/login`으로 정상 ADMIN JWT를 발급받아 관리자 API 테스트에 사용한다.

### Invalid Token

정상 JWT를 의도적으로 변경하거나 명시적인 invalid token fixture를 사용한다.

### Expired Token

만료 상태가 확실한 JWT를 Fixture로 준비하여 테스트한다.

토큰 값은 테스트 코드나 GitHub 저장소에 직접 저장하지 않는다.

---

## 8. DB / Audit Verification Strategy

pytest에서 PostgreSQL에 직접 연결하여 API 결과를 교차 검증한다.

### 사용자 데이터

- 생성된 username 존재 여부
- role = USER
- status 값
- password_hash 저장 여부
- 중복 username row 개수

### Audit Log

- event_type
- username
- endpoint
- 요청 이후 생성된 최신 로그

Audit 검증에서는 단순히 `ORDER BY id DESC LIMIT 1` 결과만 신뢰하기보다,
테스트 요청과 관련된 username / endpoint / event_type 조건을 함께 사용하여
다른 테스트 로그와 혼동되지 않도록 한다.

---

## 9. BUG-001 Regression

BUG-001은 자동화 필수 대상이다.

### 기존 문제

중복 username 생성 요청 시 PostgreSQL UNIQUE Constraint에서
`psycopg.errors.UniqueViolation`이 발생하고 처리되지 않아
`500 Internal Server Error`가 반환되었다.

### 수정 후 기대 동작

- 중복 username 요청 시 `409 Conflict`
- `detail = "Username already exists"`
- 동일 username의 추가 row 미생성
- 서버 5xx 미발생

`test_duplicate_username`에서 위 항목을 반복 검증한다.

---

## 10. Planned Test Structure

```text
tests/
├─ conftest.py
├─ test_user_auth.py
├─ test_admin_auth.py
├─ test_authorization.py
└─ test_users.py
```

### 역할

- `conftest.py`
  - 환경변수
  - DB Connection
  - ADMIN Token
  - Test User Setup / Cleanup Fixture

- `test_user_auth.py`
  - USER 로그인
  - USER Audit Log

- `test_admin_auth.py`
  - ADMIN 로그인
  - ADMIN Audit Log

- `test_authorization.py`
  - no token
  - invalid token
  - expired token
  - ACCESS_DENIED Audit

- `test_users.py`
  - USER 생성 / 조회 / 상태 변경
  - Validation
  - BUG-001 Regression
  - DB 교차 검증

---

## 11. Execution

기본 실행 명령은 다음과 같이 사용한다.

```powershell
pytest -v
```

구현이 완료되면 전체 테스트 결과와 실제 자동화 커버리지를 확인하여
`03_test_coverage.md`를 최종 갱신한다.

---

## 12. Automation Goal

본 프로젝트의 자동화 목표는 자동화 비율 자체를 높이는 것이 아니다.

**수동 테스트로 발견한 핵심 위험과 결함을 선정하고,
API + DB + Audit Log를 연결한 반복 가능한 Regression Test로 전환하는 것**을 목표로 한다.
