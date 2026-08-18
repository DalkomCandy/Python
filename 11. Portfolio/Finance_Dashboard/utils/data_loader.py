"""Yahoo Finance(yfinance)로부터 시세를 조회하는 헬퍼 모듈."""
from __future__ import annotations

import streamlit as st
import yfinance as yf

DEFAULT_USDKRW = 1350.0


@st.cache_data(ttl=300, show_spinner=False)
def fetch_current_prices(tickers: list[str]) -> dict:
    """티커별 현재가와 거래 통화를 조회한다."""
    prices = {}
    for ticker in tickers:
        try:
            fast = yf.Ticker(ticker).fast_info
            price = fast.get("lastPrice") or fast.get("last_price")
            currency = fast.get("currency") or "USD"
        except Exception:
            price, currency = None, "USD"
        prices[ticker] = {"price": price, "currency": currency}
    return prices


@st.cache_data(ttl=300, show_spinner=False)
def fetch_fx_rate(base_currency: str) -> dict:
    """기준 통화로 환산하기 위한 통화별 환율 테이블을 반환한다."""
    try:
        usd_krw = yf.Ticker("KRW=X").fast_info.get("lastPrice") or DEFAULT_USDKRW
    except Exception:
        usd_krw = DEFAULT_USDKRW

    if base_currency == "KRW":
        return {"USD": usd_krw, "KRW": 1.0}
    return {"KRW": 1.0 / usd_krw, "USD": 1.0}


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_history(ticker: str, period: str = "6mo"):
    """티커의 과거 종가 시계열을 조회한다."""
    try:
        hist = yf.Ticker(ticker).history(period=period)
    except Exception:
        return None
    if hist is None or hist.empty:
        return None
    return hist["Close"]
