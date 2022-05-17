# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 14:15:22 2020

@author: RadarJ
"""

# -*- coding: utf-8 -*-
# (Fixed-Weight)
# Monthly rebalancing
#reset -sf #
#clear #
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
# =============================================================================
# Data
# =============================================================================
# Data
data_excel = pd.ExcelFile('C:/Users/RadarJ/Desktop/CLASSES/2nd Grade/2학기/Trading by 양기성 교수님/수업/HW10_편재원.xlsx')
data_df = data_excel.parse(sheet_name='data_m', header=1) # d / w(Fri) / m(EoM)
rawTime = data_df.iloc[:, 0].copy() # Date (index X)
rawK200 = data_df.iloc[:, 1].copy() # KOSPI200
rawUSD = data_df.iloc[:, 5].copy() # USDKRW
rawLIBOR1m = data_df.iloc[:, 6].copy() # USD LIBOR 1m


# C/G HPR (%, in KRW)
rawCR1 = rawK200.pct_change()*100 # (rawK200/rawK200.shift(1) - 1)*100
rawCR2 = rawUSD.pct_change()*100 # (rawUSD/rawUSD.shift(1) - 1)*100


# I/G HPR (%, in KRW)
rawIR1 = 0 # K200 배당 데이터가 없음 (대안: TR을 사용하면 됨 )
rawIR2_USD = rawLIBOR1m.shift(1)/12 # 금리의 정의를 고려하여 shift(1)
rawIR2 = ((1 + rawCR2/100)*(1 + rawIR2_USD/100) - 1)*100 # 원화로 환산


# HPR = C/G HPR + I/G HPR ( : %)
rawR1 = rawCR1 + rawIR1
rawR2 = rawCR2 + rawIR2
# =============================================================================
# Back Test 시작시점 기준으로 데이터 정리 (이 작업을 원하지 않으면 엑셀을 편집 )
# =============================================================================
# Back Test 시작일에 해당하는 index 찾기
stDateNum = 19941228 # Back Test 시작일 (투자 시작일 )
stDate = pd.to_datetime(str(stDateNum), format='%Y%m%d')
idx = np.argmin(np.abs(rawTime - stDate)) # Back Test 시작일에 해당하는 index

# Back Test 시작일 이후 데이터만 정리 (.copy():깊은 복사 . 값복사 개념.)
Time = rawTime[idx:].copy().reset_index(drop=True) # index
R1 = rawR1[idx:].copy().reset_index(drop=True)
R2 = rawR2[idx:].copy().reset_index(drop=True)
numData = Time.shape[0]


# =============================================================================
# Value, DD
# =============================================================================
# Weight
w1 = 0.5 # K200의 투자비중
w2 = 1 - w1 # USDt의 투자비중


# Portfolio Value
Rp = pd.Series(np.zeros(numData)) # 수직률 (단위 : %)
Vp = pd.Series(np.zeros(numData)) # Value
Vp[0] = 100 # 투자원금 = 100
for t in range(1,numData):
    Rp[t] = w1*R1[t] + w2*R2[t] # HPR
    Vp[t] = Vp[t-1]*(1 + Rp[t]/100) # Value
    

# Portfolio DD
MAXp = Vp.cummax()
DDp = (Vp/MAXp - 1)*100 # 단위: %


# =============================================================================
# 벤치마크의 Value, DD 계산
# =============================================================================
K200 = rawK200[idx:].copy().reset_index(drop=True)


# BM Value ( )
Vb = (K200/K200[0])*100


# BM DD
MAXb = Vb.cummax()
DDb = (Vb/MAXb - 1)*100 # 단위: %


# =============================================================================
#
# =============================================================================
# Value MDD
fig = plt.figure(figsize=(10, 7)) # figsize = (가로길이, 세로길이)
gs = gridspec.GridSpec(nrows=2,   # row 개수 
                       ncols=1,   # col 개수
                       height_ratios=[8, 3],
                       width_ratios=[5])   # subplot




ax0 = plt.subplot(gs[0])
ax0.plot(Time, Vp, label='Fixed-Weight', color='red')
ax0.plot(Time,Vb, label='K200', color='blue')
ax0.set_title('<Value>')
ax0.grid(True)
ax0.legend()


ax1 = plt.subplot(gs[1])
ax1.plot(Time, DDp, color='red')
ax1.plot(Time, DDb, color='blue')
ax1.set_title('<Draw-down>')
ax1.grid(True)

plt.show()
