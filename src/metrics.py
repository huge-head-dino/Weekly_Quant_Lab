from __future__ import annotations

from typing import Iterable, Mapping

import pandas as pd

from src.utils import calculate_positive_rate, format_analysis_period


def _validate_required_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    """Raise a clear error when one or more required columns are missing."""
    missing_columns = [column for column in columns if column not in df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise KeyError(f"필수 열이 없습니다: {missing_text}")


def calculate_correlation(df: pd.DataFrame, x_col: str, y_col: str) -> float:
    """Calculate correlation between two columns after aligning valid rows."""
    _validate_required_columns(df, [x_col, y_col])
    clean = df[[x_col, y_col]].dropna()
    if clean.empty:
        raise ValueError(f"상관관계를 계산할 데이터가 없습니다: {x_col}, {y_col}")
    return float(clean[x_col].corr(clean[y_col]))


def add_daily_returns(
    df: pd.DataFrame,
    price_columns: Iterable[str] = ("kospi_close", "usdkrw_close"),
) -> pd.DataFrame:
    """Append daily percentage returns for the provided price columns."""
    result = df.copy()
    _validate_required_columns(result, price_columns)

    for column in price_columns:
        return_column = column.replace("_close", "_return")
        result[return_column] = result[column].pct_change()

    return result


def add_won_specific_fx_pressure(
    df: pd.DataFrame,
    usdkrw_col: str = "usdkrw_return",
    dxy_col: str = "dxy_return",
    output_col: str = "won_specific_fx_pressure",
) -> pd.DataFrame:
    """Approximate won-specific FX pressure as USD/KRW return minus DXY return."""
    result = df.copy()
    _validate_required_columns(result, [usdkrw_col, dxy_col])
    result[output_col] = result[usdkrw_col] - result[dxy_col]
    return result


def calculate_return_correlation(
    df: pd.DataFrame,
    kospi_col: str = "kospi_return",
    fx_col: str = "usdkrw_return",
) -> float:
    """Calculate correlation between KOSPI returns and USD/KRW returns."""
    return calculate_correlation(df, kospi_col, fx_col)


def calculate_rolling_correlation(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    window: int = 252,
) -> pd.DataFrame:
    """Calculate rolling correlation between two return columns."""
    if window < 2:
        raise ValueError("rolling window는 2 이상이어야 합니다.")

    _validate_required_columns(df, [x_col, y_col])

    clean = df[[x_col, y_col]].dropna().copy()
    if clean.empty:
        raise ValueError("롤링 상관관계를 계산할 데이터가 없습니다.")

    # 두 시계열을 같은 날짜에 맞춘 뒤 rolling correlation을 계산한다.
    rolling_corr = clean[x_col].rolling(window=window).corr(clean[y_col])
    rolling_df = rolling_corr.to_frame(name="rolling_correlation").dropna()
    rolling_df.index.name = clean.index.name or "Date"

    if rolling_df.empty:
        raise ValueError(
            "롤링 상관관계 결과가 모두 비어 있습니다. 표본 수나 window 값을 확인해 주세요."
        )

    return rolling_df


def _summarize_target_by_quantile(
    df: pd.DataFrame,
    signal_col: str,
    target_col: str,
    quantiles: int,
    label_col: str,
) -> pd.DataFrame:
    """Summarize target behavior across signal quantiles using reusable labels."""
    _validate_required_columns(df, [signal_col, target_col])

    clean = df[[signal_col, target_col]].dropna().copy()
    if clean.empty:
        raise ValueError(f"분위수 분석에 사용할 데이터가 없습니다: {signal_col}, {target_col}")

    quantile_bucket = pd.qcut(clean[signal_col], q=quantiles, duplicates="drop")
    unique_bucket_count = quantile_bucket.nunique(dropna=True)
    if unique_bucket_count == 0:
        raise ValueError(f"분위수를 계산할 수 없습니다: {signal_col}")

    clean["_quantile_code"] = quantile_bucket.cat.codes + 1
    clean[label_col] = clean["_quantile_code"].map(lambda code: f"Q{int(code)}")

    grouped = clean.groupby(["_quantile_code", label_col], observed=True)
    summary = grouped.agg(
        **{
            f"{signal_col}_min": (signal_col, "min"),
            f"{signal_col}_max": (signal_col, "max"),
            f"{signal_col}_mean": (signal_col, "mean"),
            f"{signal_col}_median": (signal_col, "median"),
            f"{target_col}_mean": (target_col, "mean"),
            f"{target_col}_median": (target_col, "median"),
            "sample_size": (target_col, "size"),
        }
    )
    summary[f"{target_col}_positive_rate"] = grouped[target_col].apply(calculate_positive_rate)

    return summary.reset_index().sort_values("_quantile_code").drop(columns=["_quantile_code"])


def summarize_returns_by_quantile(
    df: pd.DataFrame,
    signal_col: str = "usdkrw_return",
    target_col: str = "kospi_return",
    quantiles: int = 5,
) -> pd.DataFrame:
    """Summarize target returns across quantiles of the signal column."""
    summary = _summarize_target_by_quantile(
        df=df,
        signal_col=signal_col,
        target_col=target_col,
        quantiles=quantiles,
        label_col="fx_quantile",
    )
    return summary.rename(columns={f"{target_col}_positive_rate": "kospi_positive_rate"})


def summarize_won_specific_pressure_by_quantile(
    df: pd.DataFrame,
    signal_col: str = "won_specific_fx_pressure",
    target_col: str = "kospi_return",
    quantiles: int = 5,
) -> pd.DataFrame:
    """Summarize KOSPI returns across quantiles of won-specific FX pressure."""
    summary = _summarize_target_by_quantile(
        df=df,
        signal_col=signal_col,
        target_col=target_col,
        quantiles=quantiles,
        label_col="won_specific_pressure_quantile",
    )
    return summary.rename(columns={f"{target_col}_positive_rate": "kospi_positive_rate"})


def summarize_foreign_flow_by_quantile(
    df: pd.DataFrame,
    signal_col: str = "foreign_net_buy_krw",
    target_col: str = "kospi_return",
    quantiles: int = 5,
) -> pd.DataFrame:
    """Summarize KOSPI returns across quantiles of foreign net-buy flows."""
    summary = _summarize_target_by_quantile(
        df=df,
        signal_col=signal_col,
        target_col=target_col,
        quantiles=quantiles,
        label_col="foreign_flow_quantile",
    )
    return summary.rename(columns={f"{target_col}_positive_rate": "kospi_positive_rate"})


def summarize_dxy_relationships(
    df: pd.DataFrame,
    kospi_col: str = "kospi_return",
    usdkrw_col: str = "usdkrw_return",
    dxy_col: str = "dxy_return",
    pressure_col: str = "won_specific_fx_pressure",
) -> pd.DataFrame:
    """Build a long-form table of DXY extension metrics."""
    _validate_required_columns(df, [kospi_col, usdkrw_col, dxy_col, pressure_col])
    clean = df[[kospi_col, usdkrw_col, dxy_col, pressure_col]].dropna()
    if clean.empty:
        raise ValueError("DXY 확장 분석에 사용할 데이터가 없습니다.")

    start_date, end_date = format_analysis_period(clean.index)
    rows = [
        {"section": "dxy", "metric": "analysis_start", "value": start_date},
        {"section": "dxy", "metric": "analysis_end", "value": end_date},
        {"section": "dxy", "metric": "observation_count", "value": int(len(clean))},
        {
            "section": "dxy",
            "metric": "kospi_dxy_correlation",
            "value": calculate_correlation(clean, kospi_col, dxy_col),
        },
        {
            "section": "dxy",
            "metric": "usdkrw_dxy_correlation",
            "value": calculate_correlation(clean, usdkrw_col, dxy_col),
        },
        {
            "section": "dxy",
            "metric": "kospi_won_specific_pressure_correlation",
            "value": calculate_correlation(clean, kospi_col, pressure_col),
        },
        {
            "section": "dxy",
            "metric": "won_specific_pressure_mean",
            "value": float(clean[pressure_col].mean()),
        },
        {
            "section": "dxy",
            "metric": "won_specific_pressure_median",
            "value": float(clean[pressure_col].median()),
        },
    ]
    return pd.DataFrame(rows)


def summarize_foreign_flow_relationships(
    df: pd.DataFrame,
    flow_col: str = "foreign_net_buy_krw",
    kospi_col: str = "kospi_return",
    usdkrw_col: str = "usdkrw_return",
    pressure_col: str = "won_specific_fx_pressure",
) -> pd.DataFrame:
    """Build a long-form table of foreign-flow extension metrics."""
    _validate_required_columns(df, [flow_col, kospi_col, usdkrw_col])

    rows: list[dict[str, object]] = []
    base_clean = df[[flow_col, kospi_col, usdkrw_col]].dropna()
    if base_clean.empty:
        raise ValueError("외국인 순매수 확장 분석에 사용할 데이터가 없습니다.")

    start_date, end_date = format_analysis_period(base_clean.index)
    rows.extend(
        [
            {"section": "foreign_flow", "metric": "analysis_start", "value": start_date},
            {"section": "foreign_flow", "metric": "analysis_end", "value": end_date},
            {
                "section": "foreign_flow",
                "metric": "observation_count",
                "value": int(len(base_clean)),
            },
            {
                "section": "foreign_flow",
                "metric": "foreign_net_buy_mean_krw",
                "value": float(base_clean[flow_col].mean()),
            },
            {
                "section": "foreign_flow",
                "metric": "foreign_net_buy_median_krw",
                "value": float(base_clean[flow_col].median()),
            },
            {
                "section": "foreign_flow",
                "metric": "foreign_net_buy_kospi_correlation",
                "value": calculate_correlation(base_clean, flow_col, kospi_col),
            },
            {
                "section": "foreign_flow",
                "metric": "foreign_net_buy_usdkrw_correlation",
                "value": calculate_correlation(base_clean, flow_col, usdkrw_col),
            },
        ]
    )

    if pressure_col in df.columns:
        pressure_clean = df[[flow_col, pressure_col]].dropna()
        if not pressure_clean.empty:
            rows.append(
                {
                    "section": "foreign_flow",
                    "metric": "foreign_net_buy_won_specific_pressure_correlation",
                    "value": calculate_correlation(pressure_clean, flow_col, pressure_col),
                }
            )

    return pd.DataFrame(rows)


def summarize_bottom_quantile_event_forward_returns(
    df: pd.DataFrame,
    signal_col: str,
    event_quantile: float = 0.1,
    horizons: Iterable[int] = (1, 5, 20),
    event_name: str = "event",
) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    """Summarize forward returns after lower-tail events such as foreign selloffs."""
    _validate_required_columns(df, [signal_col])

    signal = df[signal_col].dropna()
    if signal.empty:
        raise ValueError(f"이벤트 기준이 될 데이터가 없습니다: {signal_col}")

    threshold = float(signal.quantile(event_quantile))
    event_details = df.loc[df[signal_col] <= threshold].copy()
    if event_details.empty:
        raise ValueError(f"하위 분위 이벤트가 식별되지 않았습니다: {signal_col}")

    event_details[f"is_{event_name}"] = True
    event_details[f"{event_name}_threshold"] = threshold

    rows: list[dict[str, object]] = []
    for horizon in horizons:
        return_col = f"forward_return_{int(horizon)}d"
        _validate_required_columns(event_details, [return_col])
        series = event_details[return_col].dropna()
        rows.append(
            {
                "horizon": f"{int(horizon)}d",
                "average_forward_return": float(series.mean()) if not series.empty else float("nan"),
                "median_forward_return": float(series.median()) if not series.empty else float("nan"),
                "win_rate": calculate_positive_rate(series),
                "sample_size": int(series.shape[0]),
                "event_threshold": threshold,
                "event_name": event_name,
            }
        )

    event_details.index.name = "Date"
    return pd.DataFrame(rows), event_details, threshold


def build_summary_table(
    df: pd.DataFrame,
    correlation: float,
    quantile_summary: pd.DataFrame,
    fx_spike_event_count: int,
    fx_spike_threshold: float,
    rolling_summary: Mapping[str, object] | None = None,
    kospi_col: str = "kospi_return",
    fx_col: str = "usdkrw_return",
) -> pd.DataFrame:
    """Build a long-form summary table for reporting."""
    _validate_required_columns(df, [kospi_col, fx_col])

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

    if rolling_summary is not None:
        rows.extend(
            [
                {
                    "section": "rolling_correlation",
                    "metric": "rolling_corr_window",
                    "value": rolling_summary["rolling_corr_window"],
                },
                {
                    "section": "rolling_correlation",
                    "metric": "rolling_corr_latest",
                    "value": rolling_summary["rolling_corr_latest"],
                },
                {
                    "section": "rolling_correlation",
                    "metric": "rolling_corr_mean",
                    "value": rolling_summary["rolling_corr_mean"],
                },
                {
                    "section": "rolling_correlation",
                    "metric": "rolling_corr_min",
                    "value": rolling_summary["rolling_corr_min"],
                },
                {
                    "section": "rolling_correlation",
                    "metric": "rolling_corr_max",
                    "value": rolling_summary["rolling_corr_max"],
                },
            ]
        )

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
