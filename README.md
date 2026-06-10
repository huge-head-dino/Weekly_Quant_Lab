# Weekly Quant Lab

Weekly Quant Lab은 매주 하나의 시장 질문을 데이터로 점검하는 교육 및 포트폴리오용 분석 프로젝트입니다. 모든 결과는 투자 추천이나 가격 예측이 아니라, 재현 가능한 리서치 워크플로를 보여 주기 위한 목적에 맞춰 작성합니다.

## 프로젝트 목표

- 한국어 중심의 주간 퀀트 분석 기록 축적
- 재현 가능한 Python 분석 코드 유지
- 데이터 출처, 분석 기간, 표본 수, 한계를 명시하는 문서화 습관 정착

## Week 1 주제

- 주제: 달러가 강하면 KOSPI는 정말 약할까?
- 핵심 질문: USD/KRW 환율이 상승한 날 또는 상승 구간에서 KOSPI 수익률은 실제로 낮았는가?

## 데이터 출처

- 가격 데이터: `yfinance`
- KOSPI 지수: `^KS11`
- USD/KRW 환율: `KRW=X`

`week1/run_week1.py`는 두 시계열을 같은 거래일 기준으로 inner join하여 분석합니다. 기본 분석 기간은 `2010-01-01`부터 실행일 기준 종료일까지이며, 실행 인자로 변경할 수 있습니다.

## 빠른 실행 방법

```bash
python -m pip install -r requirements.txt
python -m py_compile src/data_loader.py src/metrics.py src/plots.py src/event_study.py src/utils.py week1/run_week1.py
python week1/run_week1.py
```

고정된 기간으로 재현하려면 날짜 인자를 함께 사용합니다.

```bash
python week1/run_week1.py --start-date 2010-01-01 --end-date 2026-06-10
```

## 생성 산출물

- 표: `week1/outputs/tables/`
- 차트: `week1/outputs/charts/`
- 원본 및 가공 데이터: `week1/data/`
- 글 초안: `week1/article.md`

## 프로젝트 원칙

- 투자 추천 금지
- 가격 예측 금지
- 수익률 보장 표현 금지
- 모든 분석은 교육 및 포트폴리오 목적
- 데이터 출처, 분석 기간, 표본 수, 한계 명시

## 폴더 구조

```text
Weekly_Quant_Lab/
  README.md
  PROJECT_LOG.md
  AGENTS.md
  requirements.txt
  src/
    data_loader.py
    metrics.py
    plots.py
    event_study.py
    utils.py
  week1/
    README.md
    article.md
    run_week1.py
    data/
      raw/
      processed/
    outputs/
      charts/
      tables/
      report_assets/
    notes/
      methodology.md
```
