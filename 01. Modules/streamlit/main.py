import yfinance as yf
import streamlit as st
import pandas as pd

# Streamlit Markdown : https://docs.streamlit.io/library/api-reference/text/st.markdown

tickerSymbol = "GOOGL"

# Header of app application
st.write(f'''
         #***Simple*** Stock Price APP
         **{tickerSymbol}**
         ''')

tickerData = yf.Ticker(tickerSymbol)

tickerDf = tickerData.history(period='1d',start='2011-01-01', end='2022-01-01')

st.line_chart(tickerDf.Close)
st.line_chart(tickerDf.Volume)