from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import yfinance as yf


def configure_yfinance_cache(cache_dir: str | Path) -> None:
    """Point yfinance caches to a writable project-local directory."""
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    yf.set_tz_cache_location(str(cache_path))


def _extract_close_series(
    raw_data: pd.DataFrame,
    ticker: str,
    series_name: str,
    price_column: str = "Close",
) -> pd.DataFrame:
    if raw_data.empty:
        raise ValueError(
            f"{ticker} 다운로드 결과가 비어 있습니다. 티커와 날짜 범위를 확인해 주세요."
        )

    if isinstance(raw_data.columns, pd.MultiIndex):
        if price_column not in raw_data.columns.get_level_values(0):
            raise ValueError(f"{ticker} 데이터에 '{price_column}' 열이 없습니다.")
        price_data = raw_data[price_column]
        if isinstance(price_data, pd.DataFrame):
            if ticker in price_data.columns:
                price_series = price_data[ticker]
            else:
                price_series = price_data.iloc[:, 0]
        else:
            price_series = price_data
    else:
        if price_column not in raw_data.columns:
            raise ValueError(f"{ticker} 데이터에 '{price_column}' 열이 없습니다.")
        price_series = raw_data[price_column]

    frame = price_series.to_frame(name=series_name).dropna()
    frame.index = pd.to_datetime(frame.index).tz_localize(None)
    frame = frame[~frame.index.duplicated(keep="last")].sort_index()

    if frame.empty:
        raise ValueError(f"{ticker}의 유효한 가격 데이터가 없습니다.")

    frame.index.name = "Date"
    return frame


def download_price_data(
    ticker: str,
    series_name: str,
    start_date: str,
    end_date: str | None = None,
    price_column: str = "Close",
) -> pd.DataFrame:
    """Download a single ticker from yfinance and return a normalized close series."""
    try:
        raw_data = yf.download(
            tickers=ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=False,
            threads=False,
        )
    except Exception as exc:
        raise RuntimeError(f"yfinance 다운로드 실패: {ticker} ({exc})") from exc

    return _extract_close_series(
        raw_data=raw_data,
        ticker=ticker,
        series_name=series_name,
        price_column=price_column,
    )


def load_week1_prices(
    start_date: str,
    end_date: str | None = None,
    kospi_ticker: str = "^KS11",
    usdkrw_ticker: str = "KRW=X",
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Download KOSPI and USD/KRW prices, then inner-join on dates."""
    kospi = download_price_data(
        ticker=kospi_ticker,
        series_name="kospi_close",
        start_date=start_date,
        end_date=end_date,
    )
    usdkrw = download_price_data(
        ticker=usdkrw_ticker,
        series_name="usdkrw_close",
        start_date=start_date,
        end_date=end_date,
    )

    merged = kospi.join(usdkrw, how="inner")
    if merged.empty:
        raise ValueError(
            "KOSPI와 USD/KRW를 날짜 기준으로 inner join한 결과가 비어 있습니다."
        )

    merged.index.name = "Date"
    return merged, {"kospi": kospi, "usdkrw": usdkrw}
