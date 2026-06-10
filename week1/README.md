# Week 1 README

## 주제

- 달러가 강하면 KOSPI는 정말 약할까?

## 핵심 질문

- USD/KRW 환율이 상승한 날 또는 상승 구간에서 KOSPI 수익률은 실제로 낮았는가?

## 데이터 출처

- `yfinance`
- KOSPI: `^KS11`
- USD/KRW: `KRW=X`

분석 스크립트는 두 데이터를 날짜 기준으로 inner join한 뒤, 일별 수익률과 이벤트 스터디를 계산합니다.

## 실행 방법

```bash
python -m py_compile src/data_loader.py src/metrics.py src/plots.py src/event_study.py src/utils.py week1/run_week1.py
python week1/run_week1.py
```

기간을 고정하려면 아래처럼 실행합니다.

```bash
python week1/run_week1.py --start-date 2010-01-01 --end-date 2026-06-10
```

## 생성 산출물

- `week1/data/raw/kospi_raw.csv`
- `week1/data/raw/usdkrw_raw.csv`
- `week1/data/processed/analysis_dataset.csv`
- `week1/data/processed/fx_spike_events.csv`
- `week1/outputs/tables/quantile_summary.csv`
- `week1/outputs/tables/event_study_summary.csv`
- `week1/outputs/tables/summary_table.csv`
- `week1/outputs/charts/kospi_usdkrw_scatter.png`
- `week1/outputs/charts/kospi_return_by_fx_quantile.png`
- `week1/outputs/charts/forward_return_after_fx_spike.png`

## 주의사항

- 이 분석은 교육 및 포트폴리오 목적입니다.
- 투자 추천, 가격 예측, 수익률 보장 표현을 포함하지 않습니다.
- 표본 수와 분석 기간은 실행 결과에 따라 달라질 수 있으므로 저장된 CSV를 함께 확인해야 합니다.
- `yfinance` 응답 상태나 네트워크 상황에 따라 다운로드가 실패할 수 있습니다.
