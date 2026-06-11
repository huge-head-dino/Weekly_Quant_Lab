# PROJECT_LOG

## Current Status

- Project Name: Weekly Quant Lab
- Status Summary: Week 1 DXY 및 선택형 외국인 순매수 확장 분석 구현 중
- Week 1 Topic: 달러 강세와 KOSPI 관계 분석
- Current Work: DXY 자동 다운로드, USD/KRW와 DXY 비교를 통한 원화 고유 압력 proxy, 외국인 순매수 선택 입력 구조를 Week 1 분석과 글에 연결
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

### 2026-06-11

- `week1/notes/references.md`를 새로 만들어 김상배(2023) 논문, KCMI 환율 관련 자료, 최근 시장 보도 요지를 정리했다.
- `week1/notes/research_context.md`를 새로 만들어 이번 분석이 왜 단순 상관관계 이상을 봐야 하는지, 기존 연구와 어떤 점에서 다르고 어떤 포지션에 있는지 정리했다.
- `week1/article.md`를 연구 맥락, 현재 시장 맥락, 자체 데이터 결과가 자연스럽게 이어지는 리서치 콘텐츠 초안으로 재구성했다.
- `week1/README.md`에 리서치 노트 문서를 소개해 분석 산출물과 해석 문서를 함께 따라갈 수 있도록 했다.
- `PROJECT_LOG.md`의 현재 상태를 Week 1 리서치 맥락 보강 단계에 맞게 갱신했다.

### 2026-06-11 (Level 3 블로그형 방향 조정)

- 무료/유료 콘텐츠 분리 없이 Week 1 글을 그대로 블로그에 올릴 수 있는 무료 블로그형 리서치 노트로 재정렬했다.
- `week1/article.md`를 Level 3 독자 기준에 맞게 다시 쓰고, 도입부, 독자 수준 안내, 핵심 요약, 마무리 문단을 보강했다.
- 문서 안의 설명을 지나치게 초보자용으로 낮추지 않으면서도, 상관관계, 분위수, 이벤트 스터디, 롤링 윈도우 같은 개념이 자연스럽게 이해되도록 문장을 조정했다.
- `week1/README.md`에 프로젝트 글쓰기 기준과 Week 1 글의 포맷을 명시했다.

### 2026-06-11 (DXY 및 외국인 순매수 확장)

- `src/data_loader.py`에 `DX-Y.NYB` 기반 DXY 다운로드 함수와 선택형 외국인 순매수 CSV 로더를 추가했다.
- `src/metrics.py`에 DXY 수익률, USD/KRW와 DXY 비교, `won_specific_fx_pressure` 근사치, 외국인 순매수 분위수 및 순매도 이벤트 분석 함수를 추가했다.
- `src/plots.py`에 DXY 롤링 상관관계 차트, 원화 고유 압력 분위수 차트, 외국인 순매수 분위수 차트, 외국인 순매도 이벤트 차트 함수를 추가했다.
- `week1/run_week1.py`에서 DXY 자동 다운로드를 시도하고 실패 시 확장 분석만 건너뛰는 구조를 넣었다.
- `week1/run_week1.py`에서 `foreign_net_buy.csv`가 없으면 외국인 수급 분석을 건너뛰고 전체 실행은 유지하는 안전한 흐름을 구성했다.
- `week1/data/external/foreign_net_buy_sample.csv`를 추가해 선택형 외부 데이터 입력 형식을 문서와 함께 맞췄다.
- 실제 실행에서는 DXY 확장 산출물이 생성됐고, 외국인 순매수 파일이 없어 관련 분석은 의도대로 건너뛰었다.
