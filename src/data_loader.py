from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

import pandas as pd
import yfinance as yf


def configure_yfinance_cache(cache_dir: str | Path) -> None:
    """Point yfinance caches to a writable project-local directory."""
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    yf.set_tz_cache_location(str(cache_path))


def _extract_price_series_from_columns(
    raw_data: pd.DataFrame,
    ticker: str,
    price_columns: Iterable[str],
) -> pd.Series:
    """Pick the first available price column from a yfinance download result."""
    if raw_data.empty:
        raise ValueError(
            f"{ticker} 다운로드 결과가 비어 있습니다. 티커와 날짜 범위를 확인해 주세요."
        )

    if isinstance(raw_data.columns, pd.MultiIndex):
        top_level_columns = set(raw_data.columns.get_level_values(0))
        for price_column in price_columns:
            if price_column not in top_level_columns:
                continue
            price_data = raw_data[price_column]
            if isinstance(price_data, pd.DataFrame):
                if ticker in price_data.columns:
                    return price_data[ticker]
                return price_data.iloc[:, 0]
            return price_data
    else:
        for price_column in price_columns:
            if price_column in raw_data.columns:
                return raw_data[price_column]

    price_text = ", ".join(price_columns)
    raise ValueError(f"{ticker} 데이터에 사용할 가격 열이 없습니다: {price_text}")


def _extract_close_series(
    raw_data: pd.DataFrame,
    ticker: str,
    series_name: str,
    price_column: str = "Close",
) -> pd.DataFrame:
    price_series = _extract_price_series_from_columns(
        raw_data=raw_data,
        ticker=ticker,
        price_columns=[price_column],
    )

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


def load_dxy_price(
    start_date: str,
    end_date: str | None = None,
    dxy_ticker: str = "DX-Y.NYB",
) -> pd.DataFrame:
    """Download DXY prices, preferring adjusted close when available."""
    try:
        raw_data = yf.download(
            tickers=dxy_ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=False,
            threads=False,
        )
    except Exception as exc:
        raise RuntimeError(f"yfinance DXY 다운로드 실패: {dxy_ticker} ({exc})") from exc

    price_series = _extract_price_series_from_columns(
        raw_data=raw_data,
        ticker=dxy_ticker,
        price_columns=["Adj Close", "Close"],
    )
    frame = price_series.to_frame(name="dxy_close").dropna()
    frame.index = pd.to_datetime(frame.index).tz_localize(None)
    frame = frame[~frame.index.duplicated(keep="last")].sort_index()

    if frame.empty:
        raise ValueError("DXY 다운로드 결과가 비어 있습니다. 티커와 날짜 범위를 확인해 주세요.")

    frame.index.name = "Date"
    return frame


def load_foreign_net_buy_csv(file_path: str | Path) -> pd.DataFrame | None:
    """Load optional foreign net-buy data from a user-provided CSV file."""
    csv_path = Path(file_path)
    if not csv_path.exists():
        return None

    df = pd.read_csv(csv_path)
    required_columns = {"date", "foreign_net_buy_krw"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise KeyError(f"외국인 순매수 CSV에 필수 열이 없습니다: {missing_text}")

    result = df[["date", "foreign_net_buy_krw"]].copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    if result["date"].isna().any():
        raise ValueError("외국인 순매수 CSV의 date 열에 datetime으로 변환할 수 없는 값이 있습니다.")

    result["foreign_net_buy_krw"] = pd.to_numeric(
        result["foreign_net_buy_krw"],
        errors="coerce",
    )
    if result["foreign_net_buy_krw"].isna().any():
        raise ValueError(
            "외국인 순매수 CSV의 foreign_net_buy_krw 열에 numeric으로 변환할 수 없는 값이 있습니다."
        )

    result["date"] = result["date"].dt.tz_localize(None)
    # 같은 날짜가 여러 번 들어오면 투자자별 세부 항목을 합쳐 온 경우일 수 있어 날짜별 합산을 택한다.
    result = (
        result.groupby("date", as_index=False)["foreign_net_buy_krw"]
        .sum()
        .sort_values("date")
    )
    result = result.set_index("date")
    result.index.name = "Date"

    return result


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
