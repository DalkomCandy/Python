# 나만의 금융 대시보드

투자 포트폴리오(주식/ETF/암호화폐)를 입력하면 [yfinance](https://github.com/ranaroussi/yfinance)로
실시간 시세를 조회해 평가금액, 손익, 자산 배분, 가치 추이를 보여주는 Streamlit 대시보드.

## 실행 방법

```bash
cd "11. Portfolio/Finance_Dashboard"
pip install -r requirements.txt
streamlit run app.py
```

## 기능

- **보유 종목 편집**: 사이드바에서 티커/수량/매입단가를 직접 수정하거나 CSV로 업로드
- **실시간 평가금액 · 손익**: Yahoo Finance 시세를 기준 통화(KRW/USD)로 환산해 계산
- **자산 배분**: 종목별 평가금액 비중 도넛 차트
- **종목별 수익률**: 수익/손실을 색으로 구분한 막대 차트
- **가치 추이**: 최근 6개월 포트폴리오 평가금액 라인 차트
- **상세 테이블**: 종목별 현재가/평가금액/손익/수익률 요약

## 티커 표기 (Yahoo Finance 기준)

| 자산 | 예시 |
|---|---|
| 국내 주식 (KOSPI) | `005930.KS` (삼성전자) |
| 국내 주식 (KOSDAQ) | `247540.KQ` |
| 국내 ETF | `069500.KS` (KODEX 200) |
| 해외 주식 | `AAPL`, `TSLA` |
| 암호화폐 | `BTC-USD`, `ETH-USD` |

`portfolio_sample.csv`를 참고해 본인의 보유 종목으로 교체하면 됩니다.
