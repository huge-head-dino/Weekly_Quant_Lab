from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def ensure_directories(paths: Iterable[Path]) -> None:
    """Create directories if they do not exist."""
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def save_dataframe(df: pd.DataFrame, path: Path, index: bool = True) -> None:
    """Save a DataFrame as UTF-8 CSV, creating parent directories if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index, encoding="utf-8-sig")


def calculate_positive_rate(series: pd.Series) -> float:
    """Return the fraction of observations above zero."""
    clean = series.dropna()
    if clean.empty:
        return float("nan")
    return float((clean > 0).mean())


def format_analysis_period(index: pd.Index) -> tuple[str, str]:
    """Format start and end dates from a DatetimeIndex-like object."""
    if len(index) == 0:
        raise ValueError("분석 기간을 계산할 수 없습니다. 인덱스가 비어 있습니다.")

    date_index = pd.to_datetime(index)
    return (
        date_index.min().strftime("%Y-%m-%d"),
        date_index.max().strftime("%Y-%m-%d"),
    )
