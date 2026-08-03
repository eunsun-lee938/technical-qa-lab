# Technical QA Lab - Project Plan

## 1. 프로젝트 개요

계정 및 권한 관리 API 서비스를 테스트 대상으로 구성하고,
QA 관점에서 요구사항 분석, Test Case 설계, API/DB/로그 검증,
회귀 테스트 및 일부 테스트 자동화를 수행하는 개인 프로젝트이다.

## 2. 프로젝트 목적

기존 서비스 QA 경험을 기반으로 검증 범위를
API, Database, Linux 및 시스템 환경으로 확장하는 것을 목표로 한다.

코드 개발 자체보다 다음 QA 프로세스를 직접 수행하고 기록하는 데 목적이 있다.

- 요구사항 분석
- 정상/예외 조건 도출
- Test Case 설계
- API 검증
- DB 데이터 검증
- 계정/권한 검증
- 로그 확인
- Regression Test
- 일부 반복 테스트 자동화

## 3. 가상 시나리오

기업 내부에서 사용하는 계정 관리 시스템을 가정한다.

사용자는 다음 두 권한으로 구분한다.

- ADMIN
- USER

계정 상태는 다음과 같이 구분한다.

- ACTIVE
- INACTIVE

ADMIN은 사용자 생성, 상태 변경, 권한 변경 등의 관리자 기능을 사용할 수 있다.

USER는 관리자 기능을 사용할 수 없으며,
자신이나 다른 사용자의 권한을 ADMIN으로 변경할 수 없다.

## 4. 테스트 환경

- Python
- FastAPI
- Swagger
- PostgreSQL
- Docker
- Git / GitHub

## 5. 테스트 방향

API 응답만 확인하지 않고 필요한 경우 다음 결과를 함께 검증한다.

1. API Response
2. Database 상태
3. Application Log

예:

USER 권한으로 관리자 권한 변경 시도

Expected:
- API: 403 Forbidden
- DB: 기존 USER 권한 유지
- Log: ACCESS_DENIED 기록

## 6. 프로젝트 진행 순서

1. 프로젝트 기획
2. 요구사항 정의
3. 테스트 환경 구축
4. Test Case 작성
5. Swagger 기반 API 테스트
6. DB 검증
7. 로그 검증
8. 결함 기록
9. Regression Test
10. 일부 테스트 자동화
11. README 및 결과 정리