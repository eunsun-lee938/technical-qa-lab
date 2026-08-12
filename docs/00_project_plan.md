# Technical QA Lab - Project Plan

## 1. 프로젝트 개요

계정 및 권한 관리 API 서비스를 테스트 대상으로 구성하고,
QA 관점에서 요구사항 분석, Test Case 설계, API / DB / Audit Log 검증,
결함 관리, Regression Test 및 핵심 시나리오 자동화를 수행하는 개인 프로젝트이다.

## 2. 프로젝트 목적

기존 서비스 QA 경험을 기반으로 검증 범위를
API, Database, 인증 / 인가, Audit Log 및 시스템 환경으로 확장하는 것을 목표로 한다.

Backend 개발 자체보다 다음 QA 프로세스를 직접 수행하고 기록하는 데 목적이 있다.

- 요구사항 분석
- 정상 / 예외 조건 도출
- Test Case 설계
- API 검증
- DB 데이터 검증
- 인증 / 인가 및 접근통제 검증
- Audit Log 검증
- 결함 기록 및 수정 확인
- Regression Test
- 핵심 반복 시나리오 자동화
- 전체 자동화 결과 Report 생성

## 3. 가상 시나리오

기업 내부에서 사용하는 계정 관리 시스템을 가정한다.

사용자는 다음 두 권한으로 구분한다.

- ADMIN
- USER

계정 상태는 다음과 같이 구분한다.

- ACTIVE
- INACTIVE

ADMIN은 다음 사용자 관리 기능을 사용할 수 있다.

- USER 생성
- USER 목록 조회
- USER 상태 변경

USER는 관리자 기능을 사용할 수 없다.

일반 USER의 role을 ADMIN으로 변경하는 기능은 제공하지 않으며,
관리자 API는 유효한 ADMIN JWT가 있는 요청만 접근할 수 있도록 구성한다.

## 4. 테스트 환경

- Python
- FastAPI
- Swagger
- Postman
- PostgreSQL
- Docker
- Docker Compose
- pytest
- pytest-html
- PowerShell
- Git / GitHub

## 5. 테스트 방향

API 응답만으로 테스트 결과를 판단하지 않고,
검증 목적에 따라 Database 상태와 Audit Log를 함께 확인한다.

### 예시 1 - 중복 username 생성

Expected:

- API: `409 Conflict`
- DB: 동일 username의 추가 row 미생성
- 기존 데이터 유지

### 예시 2 - 유효하지 않은 JWT로 관리자 API 접근

Expected:

- API: `401 Unauthorized`
- Audit Log: `ACCESS_DENIED` 기록
- 실제 요청 endpoint 기록

수동 테스트에서는 정상 / 예외 / 권한 / 상태 조건을 폭넓게 검증하고,
반복 회귀 가치가 높은 핵심 시나리오는 pytest 자동화 대상으로 선정한다.

## 6. 프로젝트 진행 흐름

1. 프로젝트 기획
2. 요구사항 정의
3. 테스트 환경 구축
4. Test Case 설계
5. Postman 기반 API 테스트
6. DB 데이터 검증
7. Audit Log 검증
8. 결함 기록
9. 결함 수정 확인 및 Regression Test
10. 핵심 시나리오 pytest 자동화
11. Full Regression 실행
12. HTML Test Report 생성
13. Coverage 및 결과 정리
14. README 최종 작성
