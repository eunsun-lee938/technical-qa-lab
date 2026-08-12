# Defect Report

Technical QA Lab 수동 테스트 수행 중 확인된 결함을 기록한다.

---

## BUG-001 - 중복 username 생성 요청 시 500 Internal Server Error 발생

### Related Requirements

* `REQ-DATA-001`
  username은 중복 저장될 수 없다.

### Preconditions

* ADMIN 계정으로 인증이 완료된 상태
* 유효한 ADMIN JWT가 발급된 상태
* 동일한 username을 가진 USER 계정이 이미 존재하는 상태

### Reproduction Steps

1. ADMIN 계정으로 로그인한다.
2. 발급받은 정상 ADMIN JWT를 Authorization Bearer Token으로 설정한다.
3. 기존에 존재하는 USER와 동일한 username을 사용하여 `POST /admin/users` 요청을 전송한다.
4. API 응답을 확인한다.
5. `users` 테이블을 조회하여 동일 username의 계정이 추가 생성되었는지 확인한다.

### Actual Result

* 동일 username의 계정은 추가 생성되지 않음
* API 응답으로 `500 Internal Server Error` 발생

### Expected Result

* 동일 username의 계정이 추가 생성되지 않아야 한다.
* 중복 username 요청에 대한 오류 응답이 반환되어야 한다.
* 처리 가능한 중복 요청으로 인해 서버 5xx 오류가 발생하지 않아야 한다.

### Status

**Closed**

### Cause

`users.username` 컬럼의 UNIQUE 제약조건에 의해 중복 username 저장은 정상적으로 차단되었으나,
`POST /admin/users`에서 발생한 `psycopg.errors.UniqueViolation` 예외를 처리하지 않아
예외가 서버까지 전파되면서 `500 Internal Server Error`가 반환됨.

### Fix

`POST /admin/users`에서 `psycopg.errors.UniqueViolation` 예외를 처리하도록 수정하고,
중복 username 요청 시 `409 Conflict`와
`Username already exists` 오류 메시지를 반환하도록 변경함.

### Regression Result

**PASS**

수정 후 동일 조건으로 재검증하였다.

* 기존 username으로 재요청 시 `409 Conflict` 반환 확인
* `Username already exists` 오류 메시지 반환 확인
* 중복 USER 계정이 추가 생성되지 않음 확인
* 정상 USER 생성 기능 정상 동작 확인

추가로 해당 결함을 pytest Regression Test에 포함하여 반복 검증이 가능하도록 구성하였다.

* 대상: USER Lifecycle의 `DUPLICATE USERNAME` Step
* 검증 항목

  * 중복 username 요청 시 `409 Conflict`
  * 중복 USER row 미생성
* Full Regression 실행 결과: **PASS**

따라서 BUG-001은 수정 검증 및 자동 회귀 검증을 완료하여 **Closed** 처리한다.
