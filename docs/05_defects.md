# Defect Report

Technical QA Lab 수동 테스트 수행 중 확인된 결함을 기록한다.

---

## BUG-001 - 중복 username 생성 요청 시 500 Internal Server Error 발생

### Related Requirements
- REQ-DATA-001  
  username은 중복 저장될 수 없다.

### Preconditions
- ADMIN 계정으로 인증이 완료된 상태
- 유효한 ADMIN JWT가 발급된 상태
- 동일한 username을 가진 USER 계정이 이미 존재하는 상태

### Reproduction Steps
1. ADMIN 계정으로 로그인한다.
2. 발급받은 정상 ADMIN JWT를 Authorization Bearer Token으로 설정한다.
3. 기존에 존재하는 USER와 동일한 username을 사용하여 `POST /admin/users` 요청을 전송한다.
4. API 응답을 확인한다.
5. `users` 테이블을 조회하여 동일 username의 계정이 추가 생성되었는지 확인한다.

### Actual Result
- 동일 username의 계정은 추가 생성되지 않음
- API 응답으로 `500 Internal Server Error` 발생

### Expected Result
- 동일 username의 계정이 추가 생성되지 않아야 한다.
- 중복 username 요청에 대한 오류 응답이 반환되어야 한다.
- 처리 가능한 중복 요청으로 인해 서버 5xx 오류가 발생하지 않아야 한다.

### Status
OPEN

### Cause
확인 예정

### Fix
수정 예정

### Regression Result
수정 후 재검증 예정

---

## BUG-002 - 인증 및 접근 거부 이벤트가 audit_logs에 저장되지 않음

### Related Requirements
- REQ-LOG-001  
  USER 로그인 성공 시 `LOGIN_SUCCESS` 이벤트가 Audit Log에 기록되어야 한다.

- REQ-LOG-002  
  USER 로그인 실패 시 `LOGIN_FAILED` 이벤트가 Audit Log에 기록되어야 한다.

- REQ-LOG-005  
  관리자 API 접근이 거부된 경우 `ACCESS_DENIED` 이벤트가 Audit Log에 기록되어야 한다.

- REQ-LOG-006  
  접근 거부 Audit Log에는 실제 요청한 endpoint가 기록되어야 한다.

### Preconditions
- 테스트용 USER 계정이 존재하는 상태
- USER 계정의 로그인 및 접근 거부 조건을 수행할 수 있는 상태
- `audit_logs` 테이블을 조회할 수 있는 상태

### Reproduction Steps

#### USER 로그인 성공
1. ACTIVE 상태의 USER 계정으로 `/auth/login` 요청을 전송한다.
2. 로그인 성공 응답을 확인한다.
3. `audit_logs` 테이블에서 해당 USER의 최근 로그를 조회한다.
4. `LOGIN_SUCCESS` 이벤트 저장 여부를 확인한다.

#### USER 로그인 실패
1. USER 계정에 잘못된 비밀번호를 입력하여 `/auth/login` 요청을 전송한다.
2. 로그인 실패 응답을 확인한다.
3. `audit_logs` 테이블에서 해당 USER의 최근 로그를 조회한다.
4. `LOGIN_FAILED` 이벤트 저장 여부를 확인한다.

#### 관리자 API 접근 거부
1. 관리자 API에 인증되지 않은 조건으로 요청을 전송한다.
2. 접근 거부 응답을 확인한다.
3. `audit_logs` 테이블에서 최근 접근 거부 로그를 조회한다.
4. `ACCESS_DENIED` 이벤트 및 실제 요청 endpoint 저장 여부를 확인한다.

### Actual Result
- USER 로그인 성공 후 `LOGIN_SUCCESS` 이벤트가 `audit_logs`에서 확인되지 않음
- USER 로그인 실패 후 `LOGIN_FAILED` 이벤트가 `audit_logs`에서 확인되지 않음
- 관리자 API 접근 거부 후 `ACCESS_DENIED` 이벤트가 `audit_logs`에서 확인되지 않음
- `ACCESS_DENIED` 로그 자체가 생성되지 않아 요청 endpoint 역시 확인할 수 없음

### Expected Result
- USER 로그인 성공 시 `LOGIN_SUCCESS` 이벤트가 저장되어야 한다.
- USER 로그인 실패 시 `LOGIN_FAILED` 이벤트가 저장되어야 한다.
- 관리자 API 접근 거부 시 `ACCESS_DENIED` 이벤트가 저장되어야 한다.
- `ACCESS_DENIED` 이벤트에는 실제 요청한 endpoint가 기록되어야 한다.

### Status
OPEN

### Cause
확인 예정

### Fix
수정 예정

### Regression Result
수정 후 재검증 예정
