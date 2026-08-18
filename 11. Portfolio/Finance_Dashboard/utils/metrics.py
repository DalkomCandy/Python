"""포트폴리오 평가금액, 손익, 자산 배분 등을 계산하는 모듈."""
from __future__ import annotations

import pandas as pd

from .data_loader import fetch_history


def _to_base(amount: float, currency: str, fx_rate: dict, base_currency: str) -> float:
    if amount is None:
        return 0.0
    if currency == base_currency:
        return amount
    return amount * fx_rate.get(currency, 1.0)


def compute_holdings_table(
    portfolio_df: pd.DataFrame, price_info: dict, fx_rate: dict, base_currency: str
) -> pd.DataFrame:
    """보유 종목별 현재가/평가금액/손익/수익률을 계산한 표를 만든다."""
    rows = []
    for _, row in portfolio_df.iterrows():
        ticker = str(row["ticker"]).strip()
        info = price_info.get(ticker, {})
        price = info.get("price")
        currency = info.get("currency") or base_currency

        quantity = float(row.get("quantity") or 0)
        avg_price = float(row.get("avg_price") or 0)

        avg_price_base = _to_base(avg_price, currency, fx_rate, base_currency)
        cost_value = avg_price_base * quantity

        if price is None:
            current_price_base = None
            market_value = None
            pl = None
            pl_pct = None
        else:
            current_price_base = _to_base(price, currency, fx_rate, base_currency)
            market_value = current_price_base * quantity
            pl = market_value - cost_value
            pl_pct = (pl / cost_value * 100) if cost_value else 0.0

        rows.append(
            {
                "종목명": row.get("name") or ticker,
                "티커": ticker,
                "카테고리": row.get("category") or "기타",
                "수량": quantity,
                "매입단가": avg_price_base,
                "현재가": current_price_base,
                "매입금액": cost_value,
                "평가금액": market_value,
                "손익": pl,
                "수익률(%)": pl_pct,
            }
        )
    return pd.DataFrame(rows)


def compute_allocation(holdings: pd.DataFrame, by: str = "종목명") -> pd.DataFrame:
    """지정한 기준(종목명/카테고리)으로 평가금액을 집계한다."""
    alloc = holdings.groupby(by, as_index=False)["평가금액"].sum()
    return alloc.sort_values("평가금액", ascending=False)


def compute_portfolio_history(
    portfolio_df: pd.DataFrame, price_info: dict, fx_rate: dict, base_currency: str, period: str = "6mo"
) -> pd.Series | None:
    """보유 수량 기준으로 최근 N개월 포트폴리오 평가금액 추이를 계산한다."""
    combined = None
    for _, row in portfolio_df.iterrows():
        ticker = str(row["ticker"]).strip()
        quantity = float(row.get("quantity") or 0)
        if quantity <= 0:
            continue

        hist = fetch_history(ticker, period=period)
        if hist is None or hist.empty:
            continue

        currency = price_info.get(ticker, {}).get("currency") or base_currency
        rate = 1.0 if currency == base_currency else fx_rate.get(currency, 1.0)

        value_series = hist * quantity * rate
        combined = value_series if combined is None else combined.add(value_series, fill_value=0)

    if combined is None:
        return None

    combined.index = pd.to_datetime(combined.index).tz_localize(None)
    return combined.sort_index()
