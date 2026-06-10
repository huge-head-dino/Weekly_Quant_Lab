# Week 1 Methodology

## 분석 목적

본 분석은 "달러가 강하면 KOSPI는 정말 약한가"라는 질문을 교육 및 포트폴리오 목적에서 점검하기 위한 것이다. 투자 추천이나 가격 예측을 목표로 하지 않는다.

## 데이터 출처

- 라이브러리: `yfinance`
- KOSPI 지수 티커: `^KS11`
- USD/KRW 환율 티커: `KRW=X`

## 분석 기간

- 기본값: `2010-01-01`부터 실행일 종료일까지
- 실행 시 `--start-date`, `--end-date` 인자로 고정 가능
- 최종 사용 기간은 `summary_table.csv`에 기록

## 데이터 정리 방식

1. KOSPI와 USD/KRW 종가 데이터를 각각 다운로드한다.
2. 빈 데이터는 즉시 예외를 발생시킨다.
3. 날짜를 `DatetimeIndex`로 정규화한다.
4. 두 시계열을 날짜 기준 inner join하여 공통 관측치만 사용한다.

## 계산 지표

### 1. 일별 수익률

- `kospi_return = kospi_close.pct_change()`
- `usdkrw_return = usdkrw_close.pct_change()`

### 2. 상관관계

- KOSPI 일별 수익률과 USD/KRW 일별 변화율의 Pearson correlation 계산

### 3. 분위수 분석

- USD/KRW 일별 변화율을 5개 분위수로 분할
- 각 분위수별로 다음을 계산
  - KOSPI 평균 수익률
  - KOSPI 중앙값 수익률
  - 표본 수
  - KOSPI 상승 확률

### 4. 환율 급등 이벤트 스터디

- USD/KRW 일별 변화율 상위 10%를 환율 급등일로 정의
- 각 이벤트일에 대해 KOSPI의 1일, 5일, 20일 forward return 계산
- 각 구간별 평균, 중앙값, 승률, 표본 수 계산

## 산출물

- `week1/outputs/tables/quantile_summary.csv`
- `week1/outputs/tables/event_study_summary.csv`
- `week1/outputs/tables/summary_table.csv`
- `week1/outputs/charts/kospi_usdkrw_scatter.png`
- `week1/outputs/charts/kospi_return_by_fx_quantile.png`
- `week1/outputs/charts/forward_return_after_fx_spike.png`

## 한계

- 상관관계와 분위수 차이는 인과관계를 입증하지 않는다.
- 데이터는 외부 공급자 응답 상태에 영향을 받는다.
- 기간 선택과 이벤트 정의 방식에 따라 결과가 달라질 수 있다.
