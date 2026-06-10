from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data_loader import configure_yfinance_cache, load_week1_prices
from src.event_study import add_forward_returns, summarize_event_study
from src.metrics import (
    add_daily_returns,
    build_summary_table,
    calculate_return_correlation,
    summarize_returns_by_quantile,
)
from src.plots import (
    save_forward_return_bar_chart,
    save_quantile_bar_chart,
    save_scatter_plot,
)
from src.utils import ensure_directories, save_dataframe

DEFAULT_START_DATE = "2010-01-01"
DEFAULT_END_DATE = date.today().isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Week 1 분석: 달러 강세와 KOSPI 관계 점검"
    )
    parser.add_argument(
        "--start-date",
        default=DEFAULT_START_DATE,
        help="분석 시작일 (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        default=DEFAULT_END_DATE,
        help="분석 종료일 (YYYY-MM-DD)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    raw_dir = REPO_ROOT / "week1" / "data" / "raw"
    processed_dir = REPO_ROOT / "week1" / "data" / "processed"
    chart_dir = REPO_ROOT / "week1" / "outputs" / "charts"
    table_dir = REPO_ROOT / "week1" / "outputs" / "tables"
    report_asset_dir = REPO_ROOT / "week1" / "outputs" / "report_assets"
    cache_dir = raw_dir / ".cache"

    ensure_directories(
        [raw_dir, processed_dir, chart_dir, table_dir, report_asset_dir, cache_dir]
    )
    configure_yfinance_cache(cache_dir)

    prices, raw_frames = load_week1_prices(
        start_date=args.start_date,
        end_date=args.end_date,
    )

    analysis_df = add_daily_returns(prices)
    analysis_df = add_forward_returns(analysis_df)

    correlation = calculate_return_correlation(analysis_df)
    quantile_summary = summarize_returns_by_quantile(analysis_df)
    event_summary, event_details, fx_spike_threshold = summarize_event_study(analysis_df)
    summary_table = build_summary_table(
        df=analysis_df,
        correlation=correlation,
        quantile_summary=quantile_summary,
        fx_spike_event_count=len(event_details),
        fx_spike_threshold=fx_spike_threshold,
    )

    save_dataframe(raw_frames["kospi"], raw_dir / "kospi_raw.csv")
    save_dataframe(raw_frames["usdkrw"], raw_dir / "usdkrw_raw.csv")
    save_dataframe(analysis_df, processed_dir / "analysis_dataset.csv")
    save_dataframe(event_details, processed_dir / "fx_spike_events.csv")
    save_dataframe(quantile_summary, table_dir / "quantile_summary.csv", index=False)
    save_dataframe(event_summary, table_dir / "event_study_summary.csv", index=False)
    save_dataframe(summary_table, table_dir / "summary_table.csv", index=False)

    save_scatter_plot(
        analysis_df,
        chart_dir / "kospi_usdkrw_scatter.png",
    )
    save_quantile_bar_chart(
        quantile_summary,
        chart_dir / "kospi_return_by_fx_quantile.png",
    )
    save_forward_return_bar_chart(
        event_summary,
        chart_dir / "forward_return_after_fx_spike.png",
    )

    print("Week 1 분석 완료")
    print(f"- 분석 기간: {analysis_df.index.min():%Y-%m-%d} ~ {analysis_df.index.max():%Y-%m-%d}")
    print(f"- 관측치 수: {len(analysis_df[['kospi_return', 'usdkrw_return']].dropna())}")
    print(f"- 상관계수: {correlation:.6f}")
    print(f"- 환율 급등 이벤트 수: {len(event_details)}")
    print(f"- 표 저장 위치: {table_dir}")
    print(f"- 차트 저장 위치: {chart_dir}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] Week 1 분석 실행 실패: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
