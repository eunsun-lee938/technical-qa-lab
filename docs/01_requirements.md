# Requirements

## 1. Authentication

### REQ-AUTH-001
ACTIVE 상태의 USER는 정상 username/password로 로그인할 수 있다.

### REQ-AUTH-002
잘못된 비밀번호 입력 시 로그인이 거부되어야 한다.

### REQ-AUTH-003
존재하지 않는 username으로 로그인할 수 없다.

### REQ-AUTH-004
INACTIVE 상태의 USER는 정상 username/password를 입력해도 로그인할 수 없다.

### REQ-AUTH-005
ADMIN은 일반 사용자 로그인 API(`/auth/login`)를 사용할 수 없다.

### REQ-AUTH-006
ADMIN은 관리자 전용 로그인 API(`/admin/auth/login`)를 통해 로그인할 수 있다.

### REQ-AUTH-007
ADMIN 로그인 성공 시 관리자 API 접근에 사용할 JWT가 발급되어야 한다.


## 2. User Management

### REQ-USER-001
ADMIN은 새로운 USER 계정을 생성할 수 있다.

### REQ-USER-002
사용자 생성 시 role은 USER로 제한되어야 한다.

### REQ-USER-003
동일한 username은 중복 생성할 수 없다.

### REQ-USER-004
ADMIN은 USER 계정 목록을 조회할 수 있다.

### REQ-USER-005
일반 사용자 목록 조회 결과에 ADMIN 계정은 포함되지 않아야 한다.

### REQ-USER-006
ADMIN은 USER의 상태를 ACTIVE 또는 INACTIVE로 변경할 수 있다.

### REQ-USER-007
일반 USER의 role을 ADMIN으로 변경하는 기능을 제공하지 않아야 한다.

## 3. Admin Management

### REQ-ADMIN-001
시스템 ADMIN은 일반 사용자 생성 API가 아닌 별도의 초기화 과정으로 생성되어야 한다.

### REQ-ADMIN-002
시스템에는 두 번째 ADMIN 계정을 생성할 수 없어야 한다.

### REQ-ADMIN-003
ADMIN 계정은 ACTIVE 상태여야 관리자 인증 및 관리자 API를 사용할 수 있다.


## 4. Authorization

### REQ-AUTHZ-001
관리자 API는 유효한 ADMIN JWT를 가진 요청만 사용할 수 있다.

### REQ-AUTHZ-002
인증 정보가 없는 요청은 관리자 API에 접근할 수 없다.

### REQ-AUTHZ-003
유효하지 않은 JWT를 사용한 요청은 관리자 API에 접근할 수 없다.

### REQ-AUTHZ-004
만료된 JWT를 사용한 요청은 관리자 API에 접근할 수 없다.

### REQ-AUTHZ-005
관리자 API는 일반 Swagger 문서에 노출되지 않아야 한다.

> 관리자 API의 Swagger 비노출은 문서 노출 범위를 제한하기 위한 설정이며,
> 실제 접근통제는 ADMIN JWT 검증을 통해 수행한다.


## 5. Logging

### REQ-LOG-001
USER 로그인 성공 시 `LOGIN_SUCCESS` 이벤트가 Audit Log에 기록되어야 한다.

### REQ-LOG-002
USER 로그인 실패 시 `LOGIN_FAILED` 이벤트가 Audit Log에 기록되어야 한다.

### REQ-LOG-003
ADMIN 로그인 성공 시 `LOGIN_SUCCESS` 이벤트가 Audit Log에 기록되어야 한다.

### REQ-LOG-004
ADMIN 로그인 실패 시 `LOGIN_FAILED` 이벤트가 Audit Log에 기록되어야 한다.

### REQ-LOG-005
관리자 API 접근이 거부된 경우 `ACCESS_DENIED` 이벤트가 Audit Log에 기록되어야 한다.

### REQ-LOG-006
접근 거부 Audit Log에는 실제 요청한 endpoint가 기록되어야 한다.


## 6. Data Integrity

### REQ-DATA-001
username은 중복 저장될 수 없다.

### REQ-DATA-002
role은 ADMIN 또는 USER 값만 저장할 수 있다.

### REQ-DATA-003
status는 ACTIVE 또는 INACTIVE 값만 저장할 수 있다.

### REQ-DATA-004
사용자 비밀번호는 평문이 아닌 해시 형태로 DB에 저장되어야 한다.

### REQ-DATA-005
비밀번호 해시 값은 일반 API 응답에 포함되지 않아야 한다.

### REQ-DATA-006
DB 제약조건을 통해 두 번째 ADMIN 저장이 차단되어야 한다.
