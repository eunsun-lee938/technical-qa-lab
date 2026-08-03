# Requirements

## Authentication

### REQ-AUTH-001
ACTIVE 상태의 사용자는 정상 ID/PW로 로그인할 수 있다.

### REQ-AUTH-002
잘못된 비밀번호 입력 시 로그인이 거부되어야 한다.

### REQ-AUTH-003
INACTIVE 사용자는 정상 ID/PW를 입력해도 로그인할 수 없다.


## User Management

### REQ-USER-001
ADMIN은 새로운 사용자를 생성할 수 있다.

### REQ-USER-002
동일한 username은 중복 생성할 수 없다.

### REQ-USER-003
ADMIN은 사용자의 ACTIVE/INACTIVE 상태를 변경할 수 있다.

### REQ-USER-004
ADMIN은 사용자의 USER/ADMIN 권한을 변경할 수 있다.


## Authorization

### REQ-AUTHZ-001
ADMIN은 관리자 API를 사용할 수 있다.

### REQ-AUTHZ-002
USER는 관리자 API를 사용할 수 없다.

### REQ-AUTHZ-003
USER는 자신의 권한을 ADMIN으로 변경할 수 없다.

### REQ-AUTHZ-004
USER는 다른 사용자의 권한을 변경할 수 없다.

### REQ-AUTHZ-005
인증되지 않은 사용자는 보호된 API를 사용할 수 없다.


## Logging

### REQ-LOG-001
로그인 성공 결과를 로그에서 확인할 수 있어야 한다.

### REQ-LOG-002
로그인 실패 결과를 로그에서 확인할 수 있어야 한다.

### REQ-LOG-003
권한이 없는 API 접근은 로그에 기록되어야 한다.