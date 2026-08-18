"""나만의 금융 대시보드 — Streamlit 기반 투자 포트폴리오 추적기.

사이드바에서 보유 종목(티커/수량/매입단가)을 입력하면 Yahoo Finance(yfinance)에서
실시간 시세를 조회해 평가금액, 손익, 자산 배분, 가치 추이를 시각화한다.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import fetch_current_prices, fetch_fx_rate
from utils.metrics import compute_allocation, compute_holdings_table, compute_portfolio_history

# dataviz 스킬의 검증된 참조 팔레트 (references/palette.md)
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
GOOD, CRITICAL, MUTED, SURFACE = "#0ca30c", "#d03b3b", "#898781", "#fcfcfb"

DEFAULT_PORTFOLIO_PATH = Path(__file__).parent / "portfolio_sample.csv"

st.set_page_config(page_title="나만의 금융 대시보드", page_icon="💰", layout="wide")
st.title("💰 나만의 금융 대시보드")
st.caption("보유 종목을 입력하면 실시간 시세를 불러와 평가금액과 수익률을 계산합니다.")

with st.sidebar:
    st.header("설정")
    base_currency = st.selectbox("기준 통화", ["KRW", "USD"], index=0)
    st.divider()

    st.subheader("보유 종목")
    st.caption("티커는 Yahoo Finance 기준입니다. (예: 005930.KS, AAPL, BTC-USD)")

    if "portfolio_df" not in st.session_state:
        st.session_state.portfolio_df = pd.read_csv(DEFAULT_PORTFOLIO_PATH)

    uploaded = st.file_uploader("CSV 업로드", type="csv")
    if uploaded is not None:
        st.session_state.portfolio_df = pd.read_csv(uploaded)

    st.session_state.portfolio_df = st.data_editor(
        st.session_state.portfolio_df,
        num_rows="dynamic",
        width='stretch',
        column_config={
            "ticker": "티커",
            "name": "종목명",
            "category": "카테고리",
            "quantity": st.column_config.NumberColumn("수량", min_value=0.0),
            "avg_price": st.column_config.NumberColumn("매입단가", min_value=0.0),
        },
    )

    if st.button("🔄 시세 새로고침", width='stretch'):
        st.cache_data.clear()

portfolio_df = st.session_state.portfolio_df.dropna(subset=["ticker"]).copy()
portfolio_df["ticker"] = portfolio_df["ticker"].astype(str).str.strip()
portfolio_df = portfolio_df[portfolio_df["ticker"] != ""]

if portfolio_df.empty:
    st.info("사이드바에서 보유 종목을 입력해주세요.")
    st.stop()

tickers = portfolio_df["ticker"].tolist()

with st.spinner("시세 조회 중..."):
    try:
        price_info = fetch_current_prices(tickers)
        fx_rate = fetch_fx_rate(base_currency)
    except Exception as exc:
        st.error(f"시세를 불러오지 못했습니다: {exc}")
        st.stop()

holdings = compute_holdings_table(portfolio_df, price_info, fx_rate, base_currency)

missing = holdings[holdings["현재가"].isna()]["티커"].tolist()
if missing:
    st.warning(
        f"다음 티커의 시세를 가져오지 못해 합계에서 제외했습니다: {', '.join(missing)}"
    )

priced = holdings[holdings["현재가"].notna()]
total_value = priced["평가금액"].sum()
total_cost = priced["매입금액"].sum()
total_pl = total_value - total_cost
total_pl_pct = (total_pl / total_cost * 100) if total_cost else 0.0


def fmt_money(x: float) -> str:
    return f"{x:,.0f} {base_currency}"


col1, col2, col3, col4 = st.columns(4)
col1.metric("총 평가금액", fmt_money(total_value))
col2.metric("총 매입금액", fmt_money(total_cost))
col3.metric("총 손익", fmt_money(total_pl), f"{total_pl_pct:+.2f}%")
col4.metric("보유 종목 수", f"{len(holdings)}개")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("자산 배분")
    alloc = compute_allocation(holdings, by="종목명")
    fig_pie = px.pie(
        alloc, names="종목명", values="평가금액", hole=0.45,
        color_discrete_sequence=CATEGORICAL,
    )
    fig_pie.update_traces(textinfo="percent+label")
    fig_pie.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_pie, width='stretch')

with right:
    st.subheader("종목별 수익률")
    ranked = priced.sort_values("수익률(%)")
    if ranked.empty:
        st.caption("시세를 가져온 종목이 없습니다.")
    else:
        bar_colors = [GOOD if v >= 0 else CRITICAL for v in ranked["수익률(%)"]]
        fig_bar = go.Figure(
            go.Bar(
                x=ranked["수익률(%)"], y=ranked["종목명"], orientation="h",
                marker_color=bar_colors,
                text=[f"{v:+.1f}%" for v in ranked["수익률(%)"]],
                textposition="outside",
            )
        )
        fig_bar.update_layout(
            margin=dict(t=10, b=10, l=10, r=40),
            xaxis_title="수익률 (%)", yaxis_title=None,
            plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
        )
        st.plotly_chart(fig_bar, width='stretch')

st.subheader("포트폴리오 가치 추이 (최근 6개월)")
with st.spinner("과거 시세 조회 중..."):
    history = compute_portfolio_history(portfolio_df, price_info, fx_rate, base_currency)

if history is not None and not history.empty:
    fig_line = go.Figure(
        go.Scatter(
            x=history.index, y=history.values, mode="lines",
            line=dict(color=CATEGORICAL[0], width=2),
            fill="tozeroy", fillcolor="rgba(42,120,214,0.08)",
        )
    )
    fig_line.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        yaxis_title=f"평가금액 ({base_currency})", xaxis_title=None,
        plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
    )
    st.plotly_chart(fig_line, width='stretch')
else:
    st.caption("과거 시세를 불러올 수 없습니다.")

st.subheader("보유 종목 상세")
display_cols = ["종목명", "티커", "카테고리", "수량", "매입단가", "현재가", "매입금액", "평가금액", "손익", "수익률(%)"]
number_formats = {
    "수량": "{:,.2f}",
    "매입단가": "{:,.0f}",
    "현재가": "{:,.0f}",
    "매입금액": "{:,.0f}",
    "평가금액": "{:,.0f}",
    "손익": "{:,.0f}",
    "수익률(%)": "{:+.2f}",
}
display_df = holdings[display_cols].copy()
for col, fmt in number_formats.items():
    display_df[col] = display_df[col].apply(lambda v, fmt=fmt: "—" if pd.isna(v) else fmt.format(v))

st.dataframe(display_df, width='stretch', hide_index=True)
