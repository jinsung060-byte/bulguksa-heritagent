# 도시 문화유산 언론 담론 분석

## 연구 목적

BIGKinds 뉴스 데이터를 이용하여 도시 문화유산 관련 키워드와
시기별 핵심 담론의 변화를 분석한다.

## 분석 대상

- 광화문
- 돈화문

## 분석 기간

2001년부터 2025년까지, 5개년 단위로 구분한다.

## 데이터

- 수집 출처: BIGKinds
- 분석 기간: 2001~2025년
- 구분 단위: 5개년
- 데이터 형식: Excel

## 분석 과정

1. 데이터 구조 확인
2. 데이터 전처리
3. 키워드 분석
4. 공동출현 네트워크 분석
5. RAG 벡터 저장소 구축
6. 핵심 담론 분석

## 가상환경 실행 방법

PowerShell 실행 정책을 현재 터미널에서만 임시로 변경한다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

가상환경을 활성화한다.

```powershell
.\.venv\Scripts\Activate.ps1
```

필요한 라이브러리를 설치한다.

```powershell
python -m pip install -r requirements.txt
```

Python 환경을 확인한다.

```powershell
python --version
where.exe python
```