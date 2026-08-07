# 03. Test Coverage

## 1. 목적

본 문서는 Technical QA Lab의 수동 테스트 및 자동화 대상 범위를 정리한다.

테스트 범위는 기능의 단순 정상 동작 확인에 그치지 않고 다음 항목을 포함한다.

- USER / ADMIN 인증
- JWT 기반 관리자 API 인가
- 사용자 계정 생성 / 조회 / 상태 변경
- DB 제약조건 및 데이터 무결성
- 비밀번호 해시 저장 및 민감정보 미노출
- LOGIN_SUCCESS / LOGIN_FAILED / ACCESS_DENIED Audit Log
- 실제 결함 수정 후 Regression

---

## 2. Manual Test Coverage

수동 테스트는 총 **42개 TC**를 기준으로 수행한다.

수동 테스트에서는 동일한 인증 조건이라도 API 기능별 영향 범위를 확인하기 위해
POST / PATCH / GET 엔드포인트를 각각 검증하는 방식을 유지한다.

### 주요 검증 영역

| 영역 | 검증 내용 |
|---|---|
| USER 인증 | 정상 로그인, 잘못된 비밀번호, 미존재 계정, INACTIVE 계정, ADMIN 계정 차단 |
| ADMIN 인증 | 정상/실패 로그인, JWT 발급 |
| 관리자 API 인가 | 토큰 없음, 잘못된 토큰, 만료 토큰 |
| 계정 관리 | USER 생성, 중복 username, 상태 변경, 목록 조회 |
| 데이터 검증 | UNIQUE / CHECK / 단일 ADMIN 제약, password hash |
| Audit Log | LOGIN_SUCCESS, LOGIN_FAILED, ACCESS_DENIED, endpoint 기록 |
| 문서 노출 | Swagger 관리자 API 미노출 |

---

## 3. Requirement Coverage

요구사항은 총 **34개**를 기준으로 관리한다.

| 구분 | 요구사항 수 | 비율 |
|---|---:|---:|
| Fully Covered | 31 | 91.2% |
| Partially Covered | 2 | 5.9% |
| Uncovered | 1 | 2.9% |
| Total | 34 | 100% |

### Partially Covered

- `REQ-USER-007`  
  일반 사용자 관리 API를 통한 ADMIN 권한 상승이 불가능한 구조는 구현되어 있으나,
  별도의 권한 변경 API 자체가 존재하지 않아 직접적인 권한 상승 요청 시나리오는 제한적으로 검증한다.

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

## 4. Planned Automation Coverage

자동화는 전체 수동 TC를 그대로 옮기지 않고,
반복 회귀 가치가 높고 결과를 명확하게 자동 판정할 수 있는 핵심 시나리오를 선정한다.

### 자동화 대상

| Pytest Scenario | Manual TC Mapping | 핵심 검증 |
|---|---|---|
| `test_user_login_success` | TC01, TC33 | USER 로그인 200 + LOGIN_SUCCESS Audit |
| `test_user_login_wrong_password` | TC02, TC35 | 401 + LOGIN_FAILED Audit |
| `test_user_login_inactive` | TC04 | INACTIVE USER 403 |
| `test_admin_blocked_from_user_login` | TC05 | ADMIN의 USER 로그인 차단 |
| `test_admin_login_success` | TC11, TC36 | ADMIN 로그인 + JWT + LOGIN_SUCCESS Audit |
| `test_admin_login_failure` | TC07, TC37 | ADMIN 로그인 실패 + LOGIN_FAILED Audit |
| `test_admin_api_without_token` | TC09, TC40 | 무토큰 접근 거부 + ACCESS_DENIED |
| `test_admin_api_invalid_token` | TC14, TC41 | 잘못된 JWT 접근 거부 + ACCESS_DENIED |
| `test_admin_api_expired_token` | TC26, TC42 | 만료 JWT 접근 거부 + ACCESS_DENIED |
| `test_create_user` | TC15, TC32 | USER 생성 + DB 저장 + password hash |
| `test_duplicate_username` | TC16, TC27 | 중복 차단 + BUG-001 Regression |
| `test_update_user_inactive` | TC19 | ACTIVE → INACTIVE |
| `test_update_user_active` | TC20 | INACTIVE → ACTIVE |
| `test_invalid_user_status` | TC23 | 잘못된 status 422 + 데이터 미변경 |
| `test_get_users` | TC24 | USER 목록 + ADMIN/password_hash 미노출 |

### Planned Automation Coverage 계산

선정한 pytest 시나리오: **15개**

15개의 pytest 시나리오가 직접 커버하는 수동 TC의 고유 ID는 총 **24개**이다.

- 전체 Manual TC: 42개
- 자동화로 커버되는 Manual TC Intent: 24개

**Planned Automation Coverage = 24 / 42 × 100 = 57.1%**

> pytest 테스트 개수 15개를 단순히 42개로 나눈 값은 자동화 커버리지로 사용하지 않는다.  
> 하나의 pytest 시나리오에서 API Response와 DB / Audit Log를 함께 검증하여
> 여러 Manual TC의 검증 목적을 통합하기 때문이다.

---

## 5. Manual Only / Selective Automation

다음 항목은 수동 검증을 유지한다.

- Swagger에서 관리자 API가 노출되지 않는지 확인
- 동일 인증 조건을 POST / PATCH / GET 엔드포인트별로 반복하는 세부 회귀
- DB에 직접 잘못된 값을 삽입하여 CHECK / UNIQUE / 단일 ADMIN Constraint를 확인하는 테스트
- Docker 최초 구축 및 환경 재현 확인
- 자동화 대표 시나리오와 검증 목적이 중복되는 세부 Negative Case

수동 테스트를 제거하는 것이 아니라,
**수동 테스트는 넓은 범위를 확인하고 pytest는 핵심 회귀를 빠르게 반복 검증하는 역할**로 분리한다.

---

## 6. Coverage Summary

| 지표 | 결과 |
|---|---:|
| Manual TC | 42 |
| Requirement Full Coverage | 91.2% (31/34) |
| Requirement Partial 포함 관련 비율 | 97.1% (33/34) |
| Planned Pytest Scenario | 15 |
| Planned Automation Coverage | 57.1% (24/42) |

자동화 구현 완료 후 본 문서의 `Planned Automation Coverage`를
실제 실행 기준 `Automation Coverage`로 갱신한다.
