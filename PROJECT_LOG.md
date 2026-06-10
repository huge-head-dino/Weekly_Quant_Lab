# PROJECT_LOG

## Current Status

- Project Name: Weekly Quant Lab
- Status Summary: Week 1 1차 분석 완료
- Week 1 Topic: 달러 강세와 KOSPI 관계 분석
- Current Work: 롤링 상관관계 추가 및 `article.md` 보고서 고도화
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

### 2026-06-10 (롤링 상관관계 업데이트)

- `calculate_rolling_correlation` 함수를 추가해 KOSPI 일별 수익률과 USD/KRW 일별 변화율의 252거래일 롤링 상관관계를 계산할 수 있게 했다.
- `save_rolling_correlation_chart` 함수를 추가해 롤링 상관관계 시계열 차트를 저장하도록 확장했다.
- `week1/run_week1.py`에서 `rolling_correlation.csv`와 `rolling_correlation_252d.png`를 생성하고, `summary_table.csv`에 롤링 통계 요약을 추가했다.
- `week1/article.md`를 실제 발행 가능한 초안 수준으로 다듬고, 생성된 차트 경로와 핵심 해석, 한계를 반영했다.
- `week1/README.md`에 롤링 상관관계 산출물을 추가하고, 전체 기간 평균이 국면별 차이를 가릴 수 있다는 주의사항을 보강했다.
