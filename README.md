# 03. Test Coverage

## 1. 목적

본 문서는 Technical QA Lab의 수동 테스트 범위와
실제 구현된 pytest 자동화 Coverage를 정리한다.

테스트 범위는 기능의 단순 정상 동작 확인에 그치지 않고 다음 항목을 포함한다.

- USER / ADMIN 인증
- JWT 기반 관리자 API 인가
- 사용자 계정 생성 / 조회 / 상태 변경
- DB 제약조건 및 데이터 무결성
- 비밀번호 해시 저장 및 민감정보 미노출
- LOGIN_SUCCESS / LOGIN_FAILED / ACCESS_DENIED Audit Log
- 실제 결함 수정 후 Regression
- USER Lifecycle 기반 자동화
- Full Regression 실행 결과 확인

---

## 2. Manual Test Coverage

수동 테스트는 총 **42개 TC**를 기준으로 관리한다.

수동 테스트에서는 동일한 인증 조건이라도 API 기능별 영향 범위를 확인하기 위해
POST / PATCH / GET 엔드포인트를 각각 검증하는 방식을 유지한다.

### 주요 검증 영역

| 영역 | 검증 내용 |
| --- | --- |
| USER 인증 | 정상 로그인, 잘못된 비밀번호, 미존재 계정, INACTIVE 계정, ADMIN 계정 차단 |
| ADMIN 인증 | 정상 / 실패 로그인, JWT 발급 |
| 관리자 API 인가 | 토큰 없음, 잘못된 토큰, 만료 토큰 |
| 계정 관리 | USER 생성, 중복 username, 상태 변경, 목록 조회 |
| 데이터 검증 | UNIQUE / CHECK / 단일 ADMIN 제약, password hash |
| Audit Log | LOGIN_SUCCESS, LOGIN_FAILED, ACCESS_DENIED, endpoint 기록 |
| 문서 노출 | Swagger 관리자 API 미노출 |

수동 테스트는 상세 영향 범위와 정책 검증을 넓게 확인하는 역할을 담당하고,
pytest 자동화는 그중 반복 회귀 가치가 높은 핵심 검증 의도를 선정하여 수행한다.

---

## 3. Requirement Coverage

요구사항은 총 **34개**를 기준으로 관리한다.

| 구분 | 요구사항 수 | 비율 |
| --- | ---: | ---: |
| Fully Covered | 31 | 91.2% |
| Partially Covered | 2 | 5.9% |
| Uncovered | 1 | 2.9% |
| Total | 34 | 100% |

### Partially Covered

- `REQ-USER-007`

  일반 사용자 관리 API를 통한 ADMIN 권한 상승이 불가능한 구조는 구현되어 있으나,
  별도의 권한 변경 API 자체가 존재하지 않아
  직접적인 권한 상승 요청 시나리오는 제한적으로 검증한다.

- `REQ-ADMIN-003`

  ADMIN 계정은 ACTIVE 상태여야 관리자 기능을 사용할 수 있도록 구현되어 있으나,
  전체 관리자 기능에 대해 INACTIVE ADMIN 상태를 반복 검증하지는 않는다.

### Uncovered

- `REQ-ADMIN-001`

  시스템 최초 ADMIN 계정이 별도 초기화 절차를 통해 생성되는 정책은 구현되어 있으나,
  수동 TC에서는 초기 설치 시점의 ADMIN 생성 절차 자체를 독립 TC로 수행하지 않는다.

> Requirement Full Coverage는 **31 / 34 = 91.2%**로 계산한다.  
> Partial을 포함한 관련 요구사항 비율은 **33 / 34 = 97.1%**이지만,
> 이를 Full Coverage로 표현하지 않는다.

---

## 4. Automation Coverage

자동화는 전체 수동 TC를 코드로 그대로 복제하지 않고,
반복 회귀 가치가 높고 결과를 명확하게 자동 판정할 수 있는
핵심 검증 의도를 선정하여 구현하였다.

초기에는 기능별 15개의 독립 pytest Scenario를 계획하였으나,
USER 관리 기능의 테스트 데이터 생성 / 삭제 반복을 줄이고
실제 사용자 흐름에 가까운 검증을 수행하기 위해
USER 관리 영역을 하나의 Lifecycle Test로 리팩터링하였다.

최종 자동화 구성은 다음과 같다.

- 독립 pytest Test Function: **9개**
- USER Lifecycle Test Function: **1개**
- 전체 pytest Test Function: **10개**
- USER Lifecycle 내부 검증 Step: **6개**
- 전체 핵심 자동화 검증 의도: **15개**

### 자동화 대상

| Pytest Test / Step | Manual TC Mapping | 핵심 검증 |
| --- | --- | --- |
| `test_user_login_success` | TC01, TC33 | USER 로그인 200 + LOGIN_SUCCESS Audit |
| `test_user_login_wrong_password` | TC02, TC35 | 401 + LOGIN_FAILED Audit |
| `test_user_login_inactive` | TC04 | INACTIVE USER 403 |
| `test_admin_blocked_from_user_login` | TC05 | ADMIN의 USER 로그인 경로 차단 |
| `test_admin_login_success` | TC11, TC36 | ADMIN 로그인 + JWT + LOGIN_SUCCESS Audit |
| `test_admin_login_failure` | TC07, TC37 | ADMIN 로그인 실패 + LOGIN_FAILED Audit |
| `test_admin_api_without_token` | TC09, TC40 | 무토큰 접근 거부 + ACCESS_DENIED |
| `test_admin_api_invalid_token` | TC14, TC41 | 잘못된 JWT 접근 거부 + ACCESS_DENIED |
| `test_admin_api_expired_token` | TC26, TC42 | 만료 JWT 접근 거부 + ACCESS_DENIED |
| `test_user_lifecycle` - CREATE | TC15, TC32 | USER 생성 + DB 저장 + password hash |
| `test_user_lifecycle` - DUPLICATE | TC16, TC27 | 중복 차단 + BUG-001 Regression |
| `test_user_lifecycle` - INVALID STATUS | TC23 | 잘못된 status 422 + DB 값 미변경 |
| `test_user_lifecycle` - INACTIVE | TC19 | ACTIVE → INACTIVE + DB 반영 |
| `test_user_lifecycle` - ACTIVE | TC20 | INACTIVE → ACTIVE + DB 반영 |
| `test_user_lifecycle` - GET USERS | TC24 | USER 목록 + ADMIN / password_hash 미노출 |

---

## 5. USER Lifecycle Coverage

USER 관리 기능은 기능별로 별도의 테스트 USER를 생성하는 대신,
하나의 USER를 생성하여 Lifecycle 전체에서 재사용한다.

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

각 Step은 독립된 검증 함수로 구성되어 있으며,
`test_user_lifecycle`에서 순서대로 호출한다.

### CREATE USER

검증 항목:

- HTTP 201
- 생성 username
- role = USER
- status = ACTIVE
- PostgreSQL에 USER 저장 여부
- password_hash 저장 여부
- 평문 password 미저장 여부

### DUPLICATE USERNAME

BUG-001 Regression Step이다.

검증 항목:

- 동일 username 재요청
- HTTP 409
- `detail = "Username already exists"`
- 동일 username row = 1 유지
- 서버 5xx 미발생

### INVALID USER STATUS

검증 항목:

- 허용되지 않은 status 입력
- HTTP 422
- 요청 전 DB status 확인
- 요청 후 기존 DB status 유지

### ACTIVE → INACTIVE

검증 항목:

- HTTP 200
- Response status = INACTIVE
- PostgreSQL status = INACTIVE

### INACTIVE → ACTIVE

검증 항목:

- HTTP 200
- Response status = ACTIVE
- PostgreSQL status = ACTIVE

### GET USER LIST

검증 항목:

- HTTP 200
- Lifecycle에서 생성한 USER 존재
- USER role만 목록에 포함
- ADMIN 계정 미노출
- password_hash 미노출

### Cleanup

제품 요구사항에는 USER DELETE API가 존재하지 않는다.

따라서 Lifecycle 종료 후 수행하는 USER 삭제는 제품 기능 검증이 아닌
**테스트 데이터 Cleanup /