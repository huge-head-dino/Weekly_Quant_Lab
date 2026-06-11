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


def _save_mean_return_bar_chart(
    summary_df: pd.DataFrame,
    category_col: str,
    value_col: str,
    output_path: Path,
    title: str,
    x_label: str,
    y_label: str,
    color: str,
) -> None:
    if category_col not in summary_df.columns or value_col not in summary_df.columns:
        raise KeyError(f"차트 생성에 필요한 열이 없습니다: {category_col}, {value_col}")

    clean = summary_df[[category_col, value_col]].dropna()
    if clean.empty:
        raise ValueError("막대 차트를 그릴 데이터가 없습니다.")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(clean[category_col], clean[value_col] * 100, color=color)
    ax.axhline(0, color="#666666", linewidth=0.8)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    _save_figure(fig, output_path)


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
    _save_mean_return_bar_chart(
        summary_df=quantile_summary,
        category_col="fx_quantile",
        value_col="kospi_return_mean",
        output_path=output_path,
        title="Mean KOSPI Return by USD/KRW Quantile",
        x_label="USD/KRW Return Quantile",
        y_label="Mean KOSPI Return (%)",
        color="#2a9d8f",
    )


def save_won_specific_pressure_quantile_chart(
    quantile_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save mean KOSPI returns across won-specific FX pressure quantiles."""
    _save_mean_return_bar_chart(
        summary_df=quantile_summary,
        category_col="won_specific_pressure_quantile",
        value_col="kospi_return_mean",
        output_path=output_path,
        title="Mean KOSPI Return by Won-Specific FX Pressure Quantile",
        x_label="Won-Specific FX Pressure Quantile",
        y_label="Mean KOSPI Return (%)",
        color="#457b9d",
    )


def save_foreign_flow_quantile_chart(
    quantile_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save mean KOSPI returns across foreign-flow quantiles."""
    _save_mean_return_bar_chart(
        summary_df=quantile_summary,
        category_col="foreign_flow_quantile",
        value_col="kospi_return_mean",
        output_path=output_path,
        title="Mean KOSPI Return by Foreign Net-Buy Quantile",
        x_label="Foreign Net-Buy Quantile",
        y_label="Mean KOSPI Return (%)",
        color="#6a994e",
    )


def save_forward_return_bar_chart(
    event_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save a bar chart of mean forward returns after FX spike events."""
    _save_mean_return_bar_chart(
        summary_df=event_summary,
        category_col="horizon",
        value_col="average_forward_return",
        output_path=output_path,
        title="Mean Forward Return After USD/KRW Spike",
        x_label="Forward Horizon",
        y_label="Mean Forward Return (%)",
        color="#e76f51",
    )


def save_foreign_selloff_forward_return_chart(
    event_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save a bar chart of mean forward returns after foreign selloff events."""
    _save_mean_return_bar_chart(
        summary_df=event_summary,
        category_col="horizon",
        value_col="average_forward_return",
        output_path=output_path,
        title="Mean Forward Return After Foreign Selloff",
        x_label="Forward Horizon",
        y_label="Mean Forward Return (%)",
        color="#bc6c25",
    )


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
