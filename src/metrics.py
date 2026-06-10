from __future__ import annotations

from typing import Iterable

import pandas as pd

from src.utils import calculate_positive_rate, format_analysis_period


def add_daily_returns(
    df: pd.DataFrame,
    price_columns: Iterable[str] = ("kospi_close", "usdkrw_close"),
) -> pd.DataFrame:
    """Append daily percentage returns for the provided price columns."""
    result = df.copy()
    for column in price_columns:
        if column not in result.columns:
            raise KeyError(f"필수 가격 열이 없습니다: {column}")
        return_column = column.replace("_close", "_return")
        result[return_column] = result[column].pct_change()
    return result


def calculate_return_correlation(
    df: pd.DataFrame,
    kospi_col: str = "kospi_return",
    fx_col: str = "usdkrw_return",
) -> float:
    """Calculate correlation between KOSPI returns and USD/KRW returns."""
    clean = df[[kospi_col, fx_col]].dropna()
    if clean.empty:
        raise ValueError("상관관계를 계산할 데이터가 없습니다.")
    return float(clean[kospi_col].corr(clean[fx_col]))


def summarize_returns_by_quantile(
    df: pd.DataFrame,
    signal_col: str = "usdkrw_return",
    target_col: str = "kospi_return",
    quantiles: int = 5,
) -> pd.DataFrame:
    """Summarize target returns across quantiles of the signal column."""
    clean = df[[signal_col, target_col]].dropna().copy()
    if clean.empty:
        raise ValueError("분위수 분석에 사용할 데이터가 없습니다.")

    quantile_bucket = pd.qcut(clean[signal_col], q=quantiles, duplicates="drop")
    unique_bucket_count = quantile_bucket.nunique(dropna=True)
    if unique_bucket_count == 0:
        raise ValueError("환율 변화율 분위수를 계산할 수 없습니다.")

    clean["fx_quantile_code"] = quantile_bucket.cat.codes + 1
    clean["fx_quantile"] = clean["fx_quantile_code"].map(lambda code: f"Q{int(code)}")

    grouped = clean.groupby(["fx_quantile_code", "fx_quantile"], observed=True)
    summary = grouped.agg(
        usdkrw_return_min=(signal_col, "min"),
        usdkrw_return_max=(signal_col, "max"),
        usdkrw_return_mean=(signal_col, "mean"),
        usdkrw_return_median=(signal_col, "median"),
        kospi_return_mean=(target_col, "mean"),
        kospi_return_median=(target_col, "median"),
        sample_size=(target_col, "size"),
    )

    positive_rate = grouped[target_col].apply(calculate_positive_rate)
    summary["kospi_positive_rate"] = positive_rate

    return summary.reset_index().sort_values("fx_quantile_code").drop(
        columns=["fx_quantile_code"]
    )


def build_summary_table(
    df: pd.DataFrame,
    correlation: float,
    quantile_summary: pd.DataFrame,
    fx_spike_event_count: int,
    fx_spike_threshold: float,
    kospi_col: str = "kospi_return",
    fx_col: str = "usdkrw_return",
) -> pd.DataFrame:
    """Build a long-form summary table for reporting."""
    clean = df[[kospi_col, fx_col]].dropna()
    start_date, end_date = format_analysis_period(df.index)

    rows: list[dict[str, object]] = [
        {"section": "overall", "metric": "analysis_start", "value": start_date},
        {"section": "overall", "metric": "analysis_end", "value": end_date},
        {
            "section": "overall",
            "metric": "observation_count",
            "value": int(len(clean)),
        },
        {"section": "overall", "metric": "correlation", "value": correlation},
        {
            "section": "overall",
            "metric": "fx_spike_event_count",
            "value": int(fx_spike_event_count),
        },
        {
            "section": "overall",
            "metric": "fx_spike_threshold",
            "value": fx_spike_threshold,
        },
    ]

    for row in quantile_summary.itertuples(index=False):
        rows.extend(
            [
                {
                    "section": "fx_quantile",
                    "metric": f"{row.fx_quantile}_kospi_return_mean",
                    "value": row.kospi_return_mean,
                },
                {
                    "section": "fx_quantile",
                    "metric": f"{row.fx_quantile}_kospi_return_median",
                    "value": row.kospi_return_median,
                },
                {
                    "section": "fx_quantile",
                    "metric": f"{row.fx_quantile}_kospi_positive_rate",
                    "value": row.kospi_positive_rate,
                },
                {
                    "section": "fx_quantile",
                    "metric": f"{row.fx_quantile}_sample_size",
                    "value": int(row.sample_size),
                },
            ]
        )

    return pd.DataFrame(rows)
