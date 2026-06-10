from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from src.utils import calculate_positive_rate


def add_forward_returns(
    df: pd.DataFrame,
    price_col: str = "kospi_close",
    horizons: Iterable[int] = (1, 5, 20),
) -> pd.DataFrame:
    """Append forward returns for the given price column."""
    result = df.copy()
    if price_col not in result.columns:
        raise KeyError(f"필수 가격 열이 없습니다: {price_col}")

    for horizon in horizons:
        column_name = f"forward_return_{int(horizon)}d"
        result[column_name] = result[price_col].shift(-int(horizon)) / result[price_col] - 1.0

    return result


def summarize_event_study(
    df: pd.DataFrame,
    signal_col: str = "usdkrw_return",
    event_quantile: float = 0.9,
    horizons: Iterable[int] = (1, 5, 20),
) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    """Summarize KOSPI forward returns after USD/KRW spike events."""
    if signal_col not in df.columns:
        raise KeyError(f"필수 신호 열이 없습니다: {signal_col}")

    signal = df[signal_col].dropna()
    if signal.empty:
        raise ValueError("이벤트 기준이 될 환율 변화율 데이터가 없습니다.")

    threshold = float(signal.quantile(event_quantile))
    event_mask = df[signal_col] >= threshold
    event_details = df.loc[event_mask].copy()

    if event_details.empty:
        raise ValueError("환율 급등 이벤트가 식별되지 않았습니다.")

    event_details["is_fx_spike"] = True
    event_details["fx_spike_threshold"] = threshold

    summary_rows: list[dict[str, object]] = []
    for horizon in horizons:
        column_name = f"forward_return_{int(horizon)}d"
        if column_name not in event_details.columns:
            raise KeyError(f"필수 forward return 열이 없습니다: {column_name}")

        series = event_details[column_name].dropna()
        summary_rows.append(
            {
                "horizon": f"{int(horizon)}d",
                "average_forward_return": float(series.mean()) if not series.empty else float("nan"),
                "median_forward_return": float(series.median()) if not series.empty else float("nan"),
                "win_rate": calculate_positive_rate(series),
                "sample_size": int(series.shape[0]),
                "fx_spike_threshold": threshold,
            }
        )

    summary = pd.DataFrame(summary_rows)
    event_details.index.name = "Date"
    return summary, event_details, threshold
