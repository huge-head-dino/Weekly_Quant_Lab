from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save_figure(fig: plt.Figure, output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def save_scatter_plot(
    df: pd.DataFrame,
    output_path: Path,
    x_col: str = "usdkrw_return",
    y_col: str = "kospi_return",
) -> None:
    """Save a scatter plot of USD/KRW returns vs KOSPI returns."""
    clean = df[[x_col, y_col]].dropna()
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(clean[x_col] * 100, clean[y_col] * 100, alpha=0.55, color="#1f77b4")
    ax.axhline(0, color="#666666", linewidth=0.8)
    ax.axvline(0, color="#666666", linewidth=0.8)
    ax.set_title("KOSPI vs USD/KRW Daily Moves")
    ax.set_xlabel("USD/KRW Daily Return (%)")
    ax.set_ylabel("KOSPI Daily Return (%)")
    _save_figure(fig, output_path)


def save_quantile_bar_chart(
    quantile_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save a bar chart of mean KOSPI returns by FX-return quantile."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        quantile_summary["fx_quantile"],
        quantile_summary["kospi_return_mean"] * 100,
        color="#2a9d8f",
    )
    ax.axhline(0, color="#666666", linewidth=0.8)
    ax.set_title("Mean KOSPI Return by USD/KRW Quantile")
    ax.set_xlabel("USD/KRW Return Quantile")
    ax.set_ylabel("Mean KOSPI Return (%)")
    _save_figure(fig, output_path)


def save_forward_return_bar_chart(
    event_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save a bar chart of mean forward returns after FX spike events."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        event_summary["horizon"],
        event_summary["average_forward_return"] * 100,
        color="#e76f51",
    )
    ax.axhline(0, color="#666666", linewidth=0.8)
    ax.set_title("Mean Forward Return After USD/KRW Spike")
    ax.set_xlabel("Forward Horizon")
    ax.set_ylabel("Mean Forward Return (%)")
    _save_figure(fig, output_path)


def save_rolling_correlation_chart(
    rolling_df: pd.DataFrame,
    output_path: Path,
    title: str,
) -> None:
    """Save a rolling-correlation time-series chart."""
    if "rolling_correlation" not in rolling_df.columns:
        raise KeyError("롤링 상관관계 차트를 그리려면 'rolling_correlation' 열이 필요합니다.")

    clean = rolling_df[["rolling_correlation"]].dropna()
    if clean.empty:
        raise ValueError("롤링 상관관계 차트를 그릴 데이터가 없습니다.")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        clean.index,
        clean["rolling_correlation"],
        color="#264653",
        linewidth=1.3,
    )
    ax.axhline(0, color="#666666", linewidth=0.8, linestyle="--")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Rolling Correlation")
    fig.autofmt_xdate()
    _save_figure(fig, output_path)
