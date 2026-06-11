# Week 1 README

## 주제

- 달러가 강하면 KOSPI는 정말 약할까?

## 핵심 질문

- USD/KRW 환율이 상승한 날 또는 상승 구간에서 KOSPI 수익률은 실제로 낮았는가?

## 프로젝트 글쓰기 기준

- Week 1 글은 무료 블로그형 리서치 노트 형식으로 작성한다.
- 목표 독자 수준은 Level 3 / 5다.
- 금융시장과 데이터 분석의 기본 개념은 쓰되, 처음 읽는 독자도 따라올 수 있도록 설명을 붙인다.

## 데이터 출처

- `yfinance`
- KOSPI: `^KS11`
- USD/KRW: `KRW=X`
- DXY: `DX-Y.NYB`

분석 스크립트는 기본적으로 KOSPI와 USD/KRW를 날짜 기준으로 inner join한 뒤, 일별 수익률, 분위수 분석, 이벤트 스터디, 252거래일 롤링 상관관계를 계산한다. 확장 분석에서는 DXY를 자동 다운로드하고, 외국인 순매수 CSV가 있으면 추가 분석을 수행한다.

## 실행 방법

- 문법 확인: `python -m py_compile src/data_loader.py src/metrics.py src/plots.py src/event_study.py src/utils.py week1/run_week1.py`
- Week 1 실행: `python week1/run_week1.py`
- 기간 고정 실행: `python week1/run_week1.py --start-date 2010-01-01 --end-date 2026-06-10`

## 생성 산출물

- `week1/data/raw/kospi_raw.csv`
- `week1/data/raw/usdkrw_raw.csv`
- `week1/data/raw/dxy_raw.csv`
- `week1/data/processed/analysis_dataset.csv`
- `week1/data/processed/fx_spike_events.csv`
- `week1/data/external/foreign_net_buy_sample.csv`
- `week1/outputs/tables/quantile_summary.csv`
- `week1/outputs/tables/event_study_summary.csv`
- `week1/outputs/tables/rolling_correlation.csv`
- `week1/outputs/tables/summary_table.csv`
- `week1/outputs/tables/dxy_summary.csv`
- `week1/outputs/tables/won_specific_pressure_quantile_summary.csv`
- `week1/outputs/tables/dxy_usdkrw_rolling_corr.csv`
- `week1/outputs/charts/kospi_usdkrw_scatter.png`
- `week1/outputs/charts/kospi_return_by_fx_quantile.png`
- `week1/outputs/charts/forward_return_after_fx_spike.png`
- `week1/outputs/charts/rolling_correlation_252d.png`
- `week1/outputs/charts/dxy_usdkrw_rolling_corr.png`
- `week1/outputs/charts/kospi_return_by_won_specific_pressure_quantile.png`

조건부 산출물:

- `week1/outputs/tables/foreign_flow_summary.csv`
- `week1/outputs/tables/foreign_flow_quantile_summary.csv`
- `week1/outputs/tables/foreign_selloff_event_summary.csv`
- `week1/outputs/charts/kospi_return_by_foreign_flow_quantile.png`
- `week1/outputs/charts/forward_return_after_foreign_selloff.png`

## 리서치 노트

- `week1/article.md`: 무료 블로그형 Level 3 리서치 노트 초안
- `week1/notes/references.md`: 논문, KCMI 자료, 최근 시장 보도 요약과 링크
- `week1/notes/research_context.md`: 왜 단순 상관관계만으로 부족한지, 이번 분석이 어떤 포지션에 있는지 정리한 메모
- `week1/notes/methodology.md`: 데이터와 계산 방식 요약

## 외부 데이터 구조

- 실제 입력 파일 경로: `week1/data/external/foreign_net_buy.csv`
- 샘플 파일 경로: `week1/data/external/foreign_net_buy_sample.csv`
- CSV 필수 컬럼: `date`, `foreign_net_buy_krw`
- `foreign_net_buy_krw`는 원화 기준 순매수 금액으로 가정한다.
- 양수는 외국인 순매수, 음수는 외국인 순매도를 의미한다.
- 실제 데이터 출처는 KRX 정보데이터시스템 또는 사용자가 직접 확보한 데이터를 사용한다.

## 주의사항

- 이 분석은 교육 및 포트폴리오 목적이다.
- 투자 추천, 가격 예측, 수익률 보장 표현을 포함하지 않는다.
- 상관관계는 인과관계가 아니다.
- USD/KRW는 순수한 달러 강세 변수로 해석하기 어렵다.
- DXY는 `DX-Y.NYB` 기준으로 자동 다운로드를 시도하며, 실패하면 DXY 확장 분석만 건너뛴다.
- 외국인 순매수 파일이 없으면 관련 분석은 건너뛰고 전체 실행은 실패하지 않는다.
- 전체 기간 평균은 국면별 차이를 가릴 수 있으므로 롤링 상관관계와 이벤트 스터디를 함께 확인하는 편이 좋다.
- 표본 수와 분석 기간은 실행 결과에 따라 달라질 수 있으므로 저장된 CSV를 함께 확인해야 한다.
- `yfinance` 응답 상태나 네트워크 상황에 따라 다운로드가 실패할 수 있다.
