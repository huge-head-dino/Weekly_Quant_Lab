from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data_loader import (
    configure_yfinance_cache,
    load_dxy_price,
    load_foreign_net_buy_csv,
    load_week1_prices,
)
from src.event_study import add_forward_returns, summarize_event_study
from src.metrics import (
    add_daily_returns,
    add_won_specific_fx_pressure,
    build_summary_table,
    calculate_rolling_correlation,
    summarize_bottom_quantile_event_forward_returns,
    summarize_dxy_relationships,
    summarize_foreign_flow_by_quantile,
    summarize_foreign_flow_relationships,
    summarize_returns_by_quantile,
    summarize_won_specific_pressure_by_quantile,
    calculate_return_correlation,
)
from src.plots import (
    save_foreign_flow_quantile_chart,
    save_foreign_selloff_forward_return_chart,
    save_forward_return_bar_chart,
    save_quantile_bar_chart,
    save_rolling_correlation_chart,
    save_scatter_plot,
    save_won_specific_pressure_quantile_chart,
)
from src.utils import ensure_directories, save_dataframe

DEFAULT_START_DATE = "2010-01-01"
DEFAULT_END_DATE = date.today().isoformat()
ROLLING_WINDOW = 252


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
    external_dir = REPO_ROOT / "week1" / "data" / "external"
    chart_dir = REPO_ROOT / "week1" / "outputs" / "charts"
    table_dir = REPO_ROOT / "week1" / "outputs" / "tables"
    report_asset_dir = REPO_ROOT / "week1" / "outputs" / "report_assets"
    cache_dir = raw_dir / ".cache"

    ensure_directories(
        [
            raw_dir,
            processed_dir,
            external_dir,
            chart_dir,
            table_dir,
            report_asset_dir,
            cache_dir,
        ]
    )
    configure_yfinance_cache(cache_dir)

    prices, raw_frames = load_week1_prices(
        start_date=args.start_date,
        end_date=args.end_date,
    )

    analysis_df = add_daily_returns(prices)
    analysis_df = add_forward_returns(analysis_df)

    correlation = calculate_return_correlation(analysis_df)
    rolling_df = calculate_rolling_correlation(
        analysis_df,
        x_col="kospi_return",
        y_col="usdkrw_return",
        window=ROLLING_WINDOW,
    )
    quantile_summary = summarize_returns_by_quantile(analysis_df)
    event_summary, event_details, fx_spike_threshold = summarize_event_study(analysis_df)

    rolling_summary = {
        "rolling_corr_window": ROLLING_WINDOW,
        "rolling_corr_latest": float(rolling_df["rolling_correlation"].iloc[-1]),
        "rolling_corr_mean": float(rolling_df["rolling_correlation"].mean()),
        "rolling_corr_min": float(rolling_df["rolling_correlation"].min()),
        "rolling_corr_max": float(rolling_df["rolling_correlation"].max()),
    }

    summary_table = build_summary_table(
        df=analysis_df,
        correlation=correlation,
        quantile_summary=quantile_summary,
        fx_spike_event_count=len(event_details),
        fx_spike_threshold=fx_spike_threshold,
        rolling_summary=rolling_summary,
    )

    dxy_analysis_df = None
    dxy_summary = None
    won_specific_quantile_summary = None
    dxy_rolling_corr_df = None
    dxy_prices = None

    try:
        dxy_prices = load_dxy_price(
            start_date=args.start_date,
            end_date=args.end_date,
        )
        dxy_analysis_df = analysis_df.join(dxy_prices, how="inner")
        if dxy_analysis_df.empty:
            raise ValueError("DXY와 기존 분석 데이터를 합친 결과가 비어 있습니다.")

        dxy_analysis_df = add_daily_returns(dxy_analysis_df, price_columns=("dxy_close",))
        dxy_analysis_df = add_won_specific_fx_pressure(dxy_analysis_df)
        dxy_summary = summarize_dxy_relationships(dxy_analysis_df)
        won_specific_quantile_summary = summarize_won_specific_pressure_by_quantile(
            dxy_analysis_df
        )
        dxy_rolling_corr_df = calculate_rolling_correlation(
            dxy_analysis_df,
            x_col="usdkrw_return",
            y_col="dxy_return",
            window=ROLLING_WINDOW,
        )
    except Exception as exc:
        print(f"[WARNING] DXY extension skipped: {exc}")
        dxy_analysis_df = None
        dxy_summary = None
        won_specific_quantile_summary = None
        dxy_rolling_corr_df = None
        dxy_prices = None

    foreign_flow_summary = None
    foreign_flow_quantile_summary = None
    foreign_selloff_event_summary = None
    foreign_flow_df = None

    foreign_csv_path = external_dir / "foreign_net_buy.csv"
    foreign_net_buy = load_foreign_net_buy_csv(foreign_csv_path)
    if foreign_net_buy is None:
        print("[WARNING] foreign_net_buy.csv not found, skipping foreign flow analysis")
    else:
        try:
            foreign_flow_df = analysis_df.join(foreign_net_buy, how="inner")
            if foreign_flow_df.empty:
                raise ValueError("외국인 순매수 데이터와 기존 분석 데이터의 공통 날짜가 없습니다.")

            if dxy_analysis_df is not None:
                foreign_flow_df = foreign_flow_df.join(
                    dxy_analysis_df[["dxy_close", "dxy_return", "won_specific_fx_pressure"]],
                    how="left",
                )

            foreign_flow_summary = summarize_foreign_flow_relationships(foreign_flow_df)
            foreign_flow_quantile_summary = summarize_foreign_flow_by_quantile(
                foreign_flow_df
            )
            foreign_selloff_event_summary, _, _ = summarize_bottom_quantile_event_forward_returns(
                foreign_flow_df,
                signal_col="foreign_net_buy_krw",
                event_quantile=0.1,
                event_name="foreign_selloff_event",
            )
        except Exception as exc:
            print(f"[WARNING] foreign flow analysis skipped: {exc}")
            foreign_flow_summary = None
            foreign_flow_quantile_summary = None
            foreign_selloff_event_summary = None
            foreign_flow_df = None

    # 원본과 가공 데이터를 함께 남겨 두면 결과를 다시 확인하기 쉽다.
    save_dataframe(raw_frames["kospi"], raw_dir / "kospi_raw.csv")
    save_dataframe(raw_frames["usdkrw"], raw_dir / "usdkrw_raw.csv")
    if dxy_prices is not None:
        save_dataframe(dxy_prices, raw_dir / "dxy_raw.csv")

    save_dataframe(analysis_df, processed_dir / "analysis_dataset.csv")
    save_dataframe(event_details, processed_dir / "fx_spike_events.csv")
    save_dataframe(quantile_summary, table_dir / "quantile_summary.csv", index=False)
    save_dataframe(event_summary, table_dir / "event_study_summary.csv", index=False)
    save_dataframe(rolling_df, table_dir / "rolling_correlation.csv")
    save_dataframe(summary_table, table_dir / "summary_table.csv", index=False)

    if dxy_summary is not None and won_specific_quantile_summary is not None:
        save_dataframe(dxy_summary, table_dir / "dxy_summary.csv", index=False)
        save_dataframe(
            won_specific_quantile_summary,
            table_dir / "won_specific_pressure_quantile_summary.csv",
            index=False,
        )
    if dxy_rolling_corr_df is not None:
        save_dataframe(dxy_rolling_corr_df, table_dir / "dxy_usdkrw_rolling_corr.csv")

    if foreign_flow_summary is not None and foreign_flow_quantile_summary is not None:
        save_dataframe(foreign_flow_summary, table_dir / "foreign_flow_summary.csv", index=False)
        save_dataframe(
            foreign_flow_quantile_summary,
            table_dir / "foreign_flow_quantile_summary.csv",
            index=False,
        )
    if foreign_selloff_event_summary is not None:
        save_dataframe(
            foreign_selloff_event_summary,
            table_dir / "foreign_selloff_event_summary.csv",
            index=False,
        )

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
    save_rolling_correlation_chart(
        rolling_df,
        chart_dir / "rolling_correlation_252d.png",
        title="252-Day Rolling Correlation: KOSPI vs USD/KRW Returns",
    )

    if dxy_rolling_corr_df is not None and won_specific_quantile_summary is not None:
        save_rolling_correlation_chart(
            dxy_rolling_corr_df,
            chart_dir / "dxy_usdkrw_rolling_corr.png",
            title="252-Day Rolling Correlation: USD/KRW vs DXY Returns",
        )
        save_won_specific_pressure_quantile_chart(
            won_specific_quantile_summary,
            chart_dir / "kospi_return_by_won_specific_pressure_quantile.png",
        )

    if foreign_flow_quantile_summary is not None:
        save_foreign_flow_quantile_chart(
            foreign_flow_quantile_summary,
            chart_dir / "kospi_return_by_foreign_flow_quantile.png",
        )
    if foreign_selloff_event_summary is not None:
        save_foreign_selloff_forward_return_chart(
            foreign_selloff_event_summary,
            chart_dir / "forward_return_after_foreign_selloff.png",
        )

    print("Week 1 분석 완료")
    print(f"- 분석 기간: {analysis_df.index.min():%Y-%m-%d} ~ {analysis_df.index.max():%Y-%m-%d}")
    print(f"- 관측치 수: {len(analysis_df[['kospi_return', 'usdkrw_return']].dropna())}")
    print(f"- 상관계수: {correlation:.6f}")
    print(f"- 환율 급등 이벤트 수: {len(event_details)}")
    print(f"- 252일 롤링 상관관계 최근 값: {rolling_summary['rolling_corr_latest']:.6f}")
    if dxy_summary is not None:
        dxy_rows = dxy_summary.set_index("metric")["value"]
        print(f"- KOSPI와 DXY 상관계수: {float(dxy_rows['kospi_dxy_correlation']):.6f}")
        print(f"- USD/KRW와 DXY 상관계수: {float(dxy_rows['usdkrw_dxy_correlation']):.6f}")
    if foreign_flow_summary is not None:
        print("- 외국인 순매수 CSV를 반영한 확장 분석이 생성되었습니다.")
    print(f"- 표 저장 위치: {table_dir}")
    print(f"- 차트 저장 위치: {chart_dir}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] Week 1 분석 실행 실패: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
