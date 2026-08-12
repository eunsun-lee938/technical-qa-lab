# Technical QA Lab

> **서비스 QA 경험을 기반으로 API·Database·인증/인가·Audit Log까지 검증 범위를 확장한 Technical QA 프로젝트**

계정 및 권한 관리 API를 테스트 대상으로 구성하고,
요구사항 분석부터 Test Case 설계, 수동 검증, 결함 관리, Regression Test, 핵심 시나리오 자동화까지 QA 프로세스를 직접 수행했습니다.

이 프로젝트의 목적은 백엔드 서비스를 개발하는 것이 아니라,
**API 응답만 확인하는 기능 테스트를 넘어 실제 데이터 상태와 접근통제, 로그까지 연결하여 검증하는 QA 과정을 구현하고 기록하는 것**입니다.

---

## 1. Project Overview

### Test Target

기업 내부에서 사용하는 계정 관리 시스템을 가정했습니다.

* 사용자 권한: `USER`, `ADMIN`
* 사용자 상태: `ACTIVE`, `INACTIVE`
* USER / ADMIN 로그인 경로 분리
* JWT 기반 관리자 API 접근통제
* 사용자 생성 및 상태 변경
* PostgreSQL 데이터 저장
* 인증 및 접근거부 Audit Log 기록

### QA Scope

다음 영역을 중심으로 검증했습니다.

| 영역                   | 주요 검증 내용                                       |
| -------------------- | ---------------------------------------------- |
| Authentication       | 정상/실패 로그인, INACTIVE 계정, USER/ADMIN 로그인 정책      |
| Authorization        | No Token, Invalid JWT, Expired JWT, ADMIN 접근통제 |
| Account Management   | USER 생성, 중복 username, 상태 변경, 목록 조회             |
| Database             | UNIQUE/CHECK 제약, 데이터 상태, password hash 저장      |
| Audit Log            | LOGIN_SUCCESS, LOGIN_FAILED, ACCESS_DENIED     |
| Information Exposure | ADMIN 정보 및 password_hash 미노출                   |
| Regression           | 발견된 결함 수정 후 재검증 및 자동화                          |

---

## 2. QA Approach

이 프로젝트에서는 API 응답 하나만으로 테스트 결과를 판단하지 않았습니다.

필요한 경우 다음 세 계층을 함께 확인했습니다.

```text
API Response
     ↓
Database State
     ↓
Audit Log
```

예를 들어 접근이 거부되어야 하는 요청이라면 단순히 `401/403` 응답만 확인하는 것이 아니라,

* 올바른 HTTP Status가 반환되는지
* DB 데이터가 의도하지 않게 변경되지 않았는지
* 접근 거부 이벤트가 Audit Log에 기록되는지

를 함께 검증했습니다.

전체 QA 흐름은 다음과 같이 구성했습니다.

```text
Requirement Analysis
        ↓
Test Condition
        ↓
Manual Test Case
        ↓
API / DB / Audit Log Verification
        ↓
Defect
        ↓
Regression Test
        ↓
Selective Automation
```

---

## 3. Test Design & Coverage

총 **34개 요구사항**을 기준으로 테스트 범위를 정의하고
**42개 Manual Test Case**를 설계했습니다.

### Requirement Coverage

| 구분                        |        결과 |
| ------------------------- | --------: |
| Total Requirements        |        34 |
| Fully Covered             |        31 |
| Partially Covered         |         2 |
| Uncovered                 |         1 |
| Full Requirement Coverage | **91.2%** |

수동 테스트에서는 정상 동작뿐 아니라 다음 조건을 포함했습니다.

* 정상 / 예외 조건
* 사용자 상태
* USER / ADMIN 권한 차이
* 잘못된 인증정보
* JWT 없음 / Invalid / Expired
* DB Constraint
* 데이터 변경 여부
* 민감정보 노출 여부
* Audit Log 생성 여부

> 상세 범위: [`docs/03_test_coverage.md`](docs/03_test_coverage.md)

---

## 4. Representative Defect

### BUG-001 — Duplicate Username Request Returns 500

동일한 username으로 USER를 다시 생성했을 때 DB의 UNIQUE 제약조건에 의해 중복 저장은 차단되었지만, API에서 다음 결과가 발생했습니다.

**Expected**

```text
409 Conflict
Username already exists
```

**Actual**

```text
500 Internal Server Error
```

### Root Cause

`POST /admin/users`에서 PostgreSQL의
`psycopg.errors.UniqueViolation` 예외가 처리되지 않아 서버까지 전파되는 문제였습니다.

### Regression Result

수정 후 다음 항목을 재검증했습니다.

* 중복 username 요청 → `409 Conflict`
* 추가 USER row 미생성
* 정상 USER 생성 기능 영향 없음
* Regression Test PASS
* 핵심 Regression 시나리오에 포함

> 상세 결함 보고서: [`docs/05_defects.md`](docs/05_defects.md)

---

## 5. Test Automation

전체 Manual TC를 그대로 자동화하는 방식은 사용하지 않았습니다.

다음 조건에 해당하는 시나리오를 우선적으로 자동화했습니다.

* 반복 수행 가치가 높은 기능
* 인증/인가처럼 실패 영향도가 높은 기능
* 결과를 명확하게 자동 판정할 수 있는 기능
* API와 DB/Audit Log를 함께 검증할 가치가 있는 기능
* 실제 결함 발생 이력이 있는 Regression
* 하나의 사용자 Lifecycle로 연결할 가치가 있는 기능

### Automation Scope

* 독립 pytest Test Function: **9개**
* USER Lifecycle Test Function: **1개**
* Lifecycle 내부 검증 Step: **6개**
* 전체 pytest Test Function: **10개**
* 핵심 자동화 검증 의도: **15개**

USER 관리 기능은 다음 Lifecycle로 구성했습니다.

```text
CREATE USER
    ↓
DUPLICATE USERNAME
    ↓
INVALID STATUS
    ↓
ACTIVE → INACTIVE
    ↓
INACTIVE → ACTIVE
    ↓
GET USER LIST
    ↓
CLEANUP
```

테스트 도중 Assertion이 실패하더라도 `finally`에서 테스트 데이터를 정리하도록 구성했습니다.

### Full Regression Result

```text
10 Passed
0 Failed
0 Errors
```

전체 Test Suite를 실행하여 인증·인가·USER Lifecycle 자동화가 정상 동작하는 것을 확인했습니다.

> 자동화 설계: [`docs/04_automation_strategy.md`](docs/04_automation_strategy.md)
> 실행 결과: [`reports/full_test_report.html`](reports/full_test_report.html)

---

## 6. Test Environment

테스트 환경의 차이로 결과가 달라지는 문제를 줄이기 위해 API와 Database를 Docker Compose로 구성했습니다.

```text
Postman / Browser / pytest
            │
            ▼
      Docker Compose
      ├─ FastAPI API
      └─ PostgreSQL 16
```

`setup.ps1`을 통해 다음 초기 환경 구성을 자동화했습니다.

```text
Docker 실행 확인
       ↓
.env 생성
       ↓
DB / ADMIN Password 생성
       ↓
JWT Secret 생성
       ↓
docker compose build & up
       ↓
DB / API 실행
       ↓
Health Check
```

실제 secret 값은 Git 저장소에 포함하지 않고 환경변수로 관리합니다.

> 구축 및 실행 방법: [`docs/02_environment_setup.md`](docs/02_environment_setup.md)

---

## 7. Tools & Technologies

### QA

* Test Case Design
* Manual Testing
* Regression Testing
* Defect Reporting
* Requirement Coverage
* Test Automation

### API / Data

* FastAPI
* REST API
* Swagger
* Postman
* PostgreSQL
* SQL

### Authentication / Security-related Verification

* JWT
* Authentication / Authorization
* Role Based Access Control
* bcrypt Password Hash
* Audit Log
* Sensitive Data Exposure Check

### Automation / Environment

* Python
* pytest
* pytest-html
* Docker
* Docker Compose
* PowerShell
* Git / GitHub

---

## 8. Project Documents

| Document                                                      | 내용                               |
| ------------------------------------------------------------- | -------------------------------- |
| [`00_project_plan.md`](docs/00_project_plan.md)               | 프로젝트 목적 및 QA 방향                  |
| [`01_requirements.md`](docs/01_requirements.md)               | 요구사항 정의                          |
| [`02_environment_setup.md`](docs/02_environment_setup.md)     | 테스트 환경 구축 및 실행                   |
| [`03_test_coverage.md`](docs/03_test_coverage.md)             | Manual TC 및 Requirement Coverage |
| [`04_automation_strategy.md`](docs/04_automation_strategy.md) | 자동화 대상 선정 및 설계                   |
| [`05_defects.md`](docs/05_defects.md)                         | 발견 결함 및 Regression 결과            |
| [`full_test_report.html`](reports/full_test_report.html)      | pytest Full Regression 실행 결과     |

---

## 9. What This Project Demonstrates

이 프로젝트를 통해 다음 QA 역량을 확인하고자 했습니다.

**1. 요구사항을 테스트 조건으로 구체화**

정상 동작뿐 아니라 상태, 권한, 인증정보, 데이터 제약조건에 따른 예외조건을 테스트 범위로 구성했습니다.

**2. API 결과를 여러 계층에서 교차검증**

HTTP Response뿐 아니라 PostgreSQL 데이터와 Audit Log까지 연결하여 검증했습니다.

**3. 결함을 Regression으로 연결**

발견한 결함을 재현하고 수정 결과를 검증한 뒤 반복 확인이 필요한 시나리오는 pytest Regression Test에 포함했습니다.

**4. 수동 테스트와 자동화의 역할 구분**

모든 TC를 자동화하기보다 반복성·위험도·판정 가능성을 기준으로 핵심 시나리오를 선정했습니다.

**5. 반복 가능한 테스트 환경 구성**

Docker Compose와 초기화 스크립트를 통해 테스트 환경의 재현성을 고려했습니다.

---

## 10. Repository Structure

```text
technical-qa-lab/
├─ app/                    # Test Target API
├─ db/                     # PostgreSQL Schema / Initialization
├─ docs/                   # QA Documents
├─ tests/                  # pytest Regression Tests
├─ reports/
│  └─ full_test_report.html
├─ Dockerfile
├─ docker-compose.yml
├─ setup.ps1
├─ requirements.txt
└─ README.md
```

> **Note**
> `app/`은 포트폴리오의 주된 결과물이 아니라 QA 검증을 수행하기 위해 구성한 최소 테스트 대상입니다.
> 이 프로젝트의 중심은 `docs/`, `tests/`, `reports/`에 기록된 **테스트 설계·검증·결함·Regression 과정**입니다.
