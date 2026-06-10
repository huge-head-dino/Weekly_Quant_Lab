# PROJECT_LOG

## Current Status

- Project Name: Weekly Quant Lab
- Current Phase: Week 1 초기 구현
- Week 1 Topic: 달러 강세와 KOSPI 관계 분석
- Current Goal: 폴더 구조 생성, 데이터 수집, 분석 스크립트, 초안 작성
- Important Principles: 투자 추천 금지, 재현 가능성, 한계 명시

## Cumulative Log

### 2026-06-10

- Week 1 분석 프로젝트의 기본 폴더 구조를 생성했다.
- `src/` 공통 모듈에 데이터 로딩, 수익률 계산, 분위수 요약, 이벤트 스터디, 차트 저장 함수를 분리했다.
- `week1/run_week1.py`에 데이터 다운로드부터 CSV/PNG 저장까지 이어지는 재현 가능한 실행 파이프라인을 구성했다.
- `week1/README.md`, `week1/article.md`, `week1/notes/methodology.md` 초안을 작성했다.
- 실행 검증을 위한 `py_compile` 및 실제 스크립트 실행 경로를 준비했다.
- `yfinance` 캐시 경로를 프로젝트 내부로 고정해 Windows 환경에서의 로컬 DB 경로 오류를 우회했다.
- 실제 실행 검증을 완료했고, 기준 실행에서는 2010-01-04부터 2026-06-09까지 4,030개 관측치와 403개 환율 급등 이벤트가 생성됐다.
