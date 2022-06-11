# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 11:04:49 2020

@author: RadarJ
"""

import os     # F9 누르면 실행
os.getcwd()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

data_excel = pd.ExcelFile('C:/Users/RadarJ/Desktop/CLASSES/2nd Grade/2학기/Trading by 양기성 교수님/과제/과제에서 쓰인 자료/data_K200.xlsx')
data_df = data_excel.parse(sheet_name='data_m', skiprows=1)   # skiprows=1 가로 첫줄이 비어있어서 인식을 못할 수 있음. 그래서 여긴 스킵해야함.
rawTime = data_df.iloc[:, 0].copy() # 엑셀 자료보다 번호가 2 차이남. 엑셀에서 100번은 1998-02-28이지만 스파이더에선 98번에 해당함. 이는 아래 데이터들도 해당함. 확인할 때 조심
rawK200 = data_df.iloc[:, 1].copy() # K200
rawUSD = data_df.iloc[:, 5].copy() # USD 환율 
rawLIBOR1m = data_df.iloc[:, 6].copy() # LIBOR 1개월  
numRaw = len(rawTime)  # 확인차


# C/G HPR (%, in KRW)
rawCR1 = rawK200.pct_change()*100   # (rawK200/rawK200.shift(1) -1)*100
rawCR2 = rawUSD.pct_change()*100    # (rawUSD/rawUSD.shift(1)-1)*100


# I/G HPR (%, in KRW)
rawIR1 = 0 # K200 배당 데이터가 없음 (대안: TR을 사용하면 됨)
rawLIBOR_IR1 = rawLIBOR1m.shift(1)/12  # 금리의 정의를 고려하여 한달 전 것을 가져와야 하기에 shift(1)
rawIR2 = ((1+rawLIBOR_IR1/100)*(1+rawCR2/100)-1)*100  # 원화로 환산


# HPR = C/G HPR + I/G HPR (단위: %)
rawR1 = rawCR1 + rawIR1
rawR2 = rawCR2 + rawIR2


# Back Test 시작일에 해당하는 index 찾기
stDateNum = 19941228  # back test 시작일 (투자 시작일)
stDate = pd.to_datetime(str(stDateNum), format = '%Y%m%d')
idx = np.argmin(np.abs(rawTime - stDate))   # back test 시작일에 해당하는 index

Time = rawTime[idx:].copy().reset_index(drop=True)   # 깊은 복사, index 초기화
R1 = rawR1[idx:].copy().reset_index(drop=True)
R2 = rawR2[idx:].copy().reset_index(drop=True)

numData = Time.shape[0]   # len(Data)  or len(Data.index) 


# Risk measure는 standard deviation으로 계산.
risk_horizon = 12  
rawstd1_bf = rawR1.rolling(risk_horizon).std() # 전체 std값이 나온다.
rawstd1 = rawstd1_bf[idx:]  # 계산을 쉽게 하고자 우리가 원하는 값(19941228~ 에 해당)부터 동원하고자 슬라이싱을 한다.

rawstd2_bf = rawR2.rolling(risk_horizon).std() # 전체 std값이 나온다.
rawstd2 = rawstd2_bf[idx:]  # 계산을 쉽게 하고자 우리가 원하는 값부터 동원하고자 슬라이싱을 한다.


# 비중구하기
rawW1 = rawstd2/(rawstd1 + rawstd2) # 각각의 시그마 값들을 비슷하게 만들기 위한 비중 
rawW2 = rawstd1/(rawstd1 + rawstd2)  

W1 = rawW1[:].copy().reset_index(drop=True)  # 위에서 구성한 코딩을 했을 시 비중이 59번째 부터 되어있는데 이를 첫 시작으로 바꿈
W2 = rawW2[:].copy().reset_index(drop=True)



# =====================================
# KOSPI vs USDKRW 그림
K200 = rawK200[idx:].copy().reset_index(drop=True)
USDKRW = rawUSD[idx:].copy().reset_index(drop=True)


plt.figure(figsize=(10,5))
plt.plot(rawTime, rawK200, label = 'K200')   # Time으로 해버리면 310개로 안맞음.
plt.plot(rawTime, rawUSD, label = 'USDKRW')
plt.legend()
plt.title('<K200 vs USDKRW>')
plt.xlabel('time')
plt.ylabel('value')
plt.show()

# ==========================================


# Portfolio Value
Rp = pd.Series(np.zeros(numData)) # 수직률 (단위 : %)
Vp = pd.Series(np.zeros(numData)) # Value
Vk200 = pd.Series(np.zeros(numData))
Vusd = pd.Series(np.zeros(numData))
Vp[0] = 100 # 포트폴리오에 투자원금 100%  = 100
Vk200[0] = 100 # 코스피에 투자원금 100% = 100
Vusd[0] = 100 # 환율에 투자원금 100% = 100

# for문 반복 해서 구하기
for t in range(1,numData):   # 포트폴리오 데이터 구하기
    Rp[t] = W1[t-1]*R1[t] + W2[t-1]*R2[t] # HPR
    Vp[t] = Vp[t-1]*(1 + Rp[t]/100) # Value

for t in range(1,numData):   # K200 데이터 구하기
    Vk200[t] = Vk200[t-1]*(1+R1[t]/100)
    
for t in range(1,numData):  # 환율  
    Vusd[t] = Vusd[t-1]*(1+R2[t]/100)
    
    

# Portfolio DD
MAXp = Vp.cummax()
DDp = (Vp/MAXp - 1)*100 # 단위: %



# BM DD, K200  
MAXb = Vk200.cummax()
DDb = (Vk200/MAXb - 1)*100 # 단위: %

# BM DD, USDKRW
MAXc = Vusd.cummax()
DDc = (Vusd/MAXc -1)*100  # 단위: %


# Value MDD
fig = plt.figure(figsize=(10, 7)) # figsize = (가로길이, 세로길이)
gs = gridspec.GridSpec(nrows=2,   # row 개수 
                       ncols=1,   # col 개수
                       height_ratios=[8, 3],
                       width_ratios=[5])   # subplot




ax0 = plt.subplot(gs[0])
ax0.plot(Time, Vp, label='Risk-Parity', color='blue')  
ax0.plot(Time, Vk200 , label='K200', color='red')
ax0.plot(Time, Vusd , label='USDKRW', color='green')
ax0.set_title('<Value>')
ax0.grid(True)
ax0.legend()


ax1 = plt.subplot(gs[1])
ax1.plot(Time, DDp, color='blue')
ax1.plot(Time, DDb, color='red')
ax1.plot(Time, DDc, color='green')
ax1.set_title('<Draw-down>')
ax1.grid(True)

plt.show()










