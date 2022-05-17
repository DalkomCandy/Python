# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 11:41:06 2020

@author: RadarJ
"""

import os     # F9 누르면 실행
os.getcwd()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

'Data'
data_excel = pd.ExcelFile('C:/Users/RadarJ/Desktop/CLASSES/2nd Grade/2학기/Trading by 양기성 교수님/과제/과제에서 쓰인 자료/data_Sector_m.xlsx')
price_df = data_excel.parse(sheet_name = 'P_m', header=4) # Price Data d / w(Fri) / m(EoM)
total_df = data_excel.parse(sheet_name = 'TR_m', header=4) # Total Return Data d / w(Fri) / m(EoM)
rawPrice = price_df.iloc[:,2:].copy()  # Price dataframe K200 빼고 가져오기
rawTime = total_df.iloc[:, 0].copy()     # Date
rawMarket = total_df.iloc[:, 1].copy()   # K200 (이하 Market)
rawSector = total_df.iloc[:, 2:-1].copy()    # Scetor price   (-1 함으로써 CD1m 안가져옴)
rawRf = total_df.iloc[:, -1].copy()       # Risk-free rate (CD1m, %)
numRaw = len(rawTime)


'Rm & Sector HPR'
rawRm = rawMarket.pct_change()*100    # Market return   (rawMarket/rawMarket.shift(1) -1)*100  이하 동문
rawRs = rawSector.pct_change()*100    # Sector들의 return   (dataframe도No d pct chagnge 무리없이 쓸 수 있다!)
rawRf1 = rawRf.shift(1)/12    # Risk free rate,  금리의 정의를 고려하여 한달 전 것을 가져와야 하기에 shift(1)
rawRf2 = 1+rawRf1*0.01        # Threshold를 계산하기 위해서 준비하는 과정. 하지만 이번엔 Threshold=0으로 간주함.

# ==================================================================================================

'Mom Horizon 설정하기'
tau1=0      # 옛날   (Intermediate Momentum, 이번 과제에선 이것을 0으로 고정) 
tau=12      # 더 옛날    
rawMom = (rawPrice.shift(tau1)/rawPrice.shift(tau)- 1)*100   # Sector Mom
Threshold = 0    # Threshod = 0 or Risk-free 여기선 0으로 고정


'Rank, 단 Threshold를 기준으로 큰 값들만 ranking을 매기고 나머지 값은 0이 되도록 한다.'
rawRank = rawMom.rank(axis=1, ascending=False)*(rawMom > Threshold)      # 현재 이 랭킹은 1~10등까지 내림차순
   

# ====================================================================================================
'Back test 시작일'
stDateNum = 20021231   # back test 시작일 (투자 시작일)
stDate = pd.to_datetime(str(stDateNum), format = '%Y%m%d')
idx = np.argmin(np.abs(rawTime - stDate))    # back test 시작일에 해당하는 index


'시간 [t] 시점 맞추고자 값 깊은 복사'
Time = rawTime[idx:].copy().reset_index(drop=True)   # 깊은 복사, index 초기화
Rm = rawRm[idx:].copy().reset_index(drop=True)
Rs = rawRs[idx:].copy().reset_index(drop=True)
Rf = rawRf1[idx:].copy().reset_index(drop=True)
Mom = rawMom[idx:].copy().reset_index(drop=True)
Rank = rawRank.iloc[idx:].copy().reset_index(drop=True)
numData = Time.shape[0]




# =======================================================================================================
'Weight 설정하기'
Decile = 3  # (단위:*10%   즉, Decile =3은 30% 라는 의미  2는 20%) 



# ================================================
rawWeight1 = 1*(Rank < Decile+1)  # Decile+1 보다 작은 값은 다 1로 만든다. 
rawWeight2 = -1*(Rank == 0)
rawWeight3 = rawWeight1 + rawWeight2    # Decile등수 이하의 값들은 모두 숫자 1로 만든다.

rawWeight = rawWeight3/Decile
Weight = rawWeight.copy()

Weight['W11'] = 1       # weight를 만들기 위해서 Rf를 붙이는데 일단 다 1로 만든다.
Weight[Weight == 1] = 1/Decile    # 모든 숫자들 (1)을 1/Decile로 만든다. == 같다.    != 다르다.

'진짜 Weight 만들기'
for i in range(len(Time)):
    if sum(Weight.iloc[i]) != 1+1/Decile:    # 현재 가로행 다 더했을 시 1+1/Decile 값이 나온다. 왜냐하면 W11도 포함했기 때문.
        Weight.iloc[i] = 0
        Weight.loc[[i],['W11']] = 1    
    else:
        Weight.loc[[i],['W11']] = 0
        
# 가로행 다 더했을 시 1 + 1/Decile이 아니면 W1~W10까진 0으로, W11=1 맞으면 W11=0, 나머지 값들엔 1/Decile 값이 나오게 했습니다.

# ===============================================================================================

'Portfolio 리턴과 100만큼 투자했을 시 리턴 알기'
Rp = pd.Series(np.zeros(numData))
Vp = pd.Series(np.zeros(numData))
Vp[0] = 100

Rs['Rf'] = Rf    # 기존 Rs에다가 Rf 추가함. 


# ==================================================================
rawENE = Weight.iloc[:, 0].copy()    # 에너지 WEIGHT 
rawMAT = Weight.iloc[:, 1].copy()    # 소재 WEIGHT  
rawIND = Weight.iloc[:, 2].copy()    # 산업재 WEIGHT  
rawCOD = Weight.iloc[:, 3].copy()    # 경기관련소비재 WEIGHT 
rawCOS = Weight.iloc[:, 4].copy()    # 필수소비재 WEIGHT  
rawHEL = Weight.iloc[:, 5].copy()    # 건강관리 WEIGHT  
rawFIN = Weight.iloc[:, 6].copy()    # 금융 WIGHT  
rawINT = Weight.iloc[:, 7].copy()    # 정보통신 WEIGHT  
rawCOM = Weight.iloc[:, 8].copy()   # 커뮤니케이션 WEIGHT   
rawUTI = Weight.iloc[:, 9].copy()   # 유틸리티 WEIGHT 
rawRF  = Weight.iloc[:,10].copy()  # Rf Weight

RawENE = Rs.iloc[:, 0].copy()    # 에너지 RETURN
RawMAT = Rs.iloc[:, 1].copy()    # 소재 RETURN
RawIND = Rs.iloc[:, 2].copy()    # 산업재 RETURN
RawCOD = Rs.iloc[:, 3].copy()    # 경기관련소비재 RETURN
RawCOS = Rs.iloc[:, 4].copy()    # 필수소비재 RETURN
RawHEL = Rs.iloc[:, 5].copy()    # 건강관리 RETURN
RawFIN = Rs.iloc[:, 6].copy()    # 금융 RETURN
RawINT = Rs.iloc[:, 7].copy()    # 정보통신 RETURN
RawCOM = Rs.iloc[:, 8].copy()   # 커뮤니케이션 RETURN
RawUTI = Rs.iloc[:, 9].copy()   # 유틸리티 RETURN
RawRF =  Rs.iloc[:,10].copy()   # Rf RETURN

'내적함수를 쓰고자 노력했으나 여러가지 고려해서 불편하지만 이렇게 했습니다.'
# 지난번 과제에서의 내적함수: series * dataframe   vs 이번 과제에서의 내적함수: dataframe * dataframe
# =====================================================================


for t in range(1, numData):
    Rp[t] = rawENE[t-1]*RawENE[t] + rawMAT[t-1]*RawMAT[t] + rawIND[t-1]*RawIND[t] + rawCOD[t-1]*RawCOD[t] + rawCOS[t-1]*RawCOS[t] + rawHEL[t-1]*RawHEL[t] + rawFIN[t-1]*RawFIN[t] + rawINT[t-1]*RawINT[t] + rawCOM[t-1]*RawCOM[t] + rawUTI[t-1]*RawUTI[t] + rawRF[t-1]*RawRF[t]
    Vp. iloc[t] = Vp.iloc[t-1]*(1 + Rp.iloc[t]/100)

# 이때 Rp는 Back test 기준일로 해서 산출했습니다.



'Portfolio DD'
MAXp = Vp.cummax()
DDp = (Vp/MAXp - 1)*100 # 단위: %



# BM Portfolio 
Rb = pd.Series(np.zeros(numData))  # Rm
Vb = pd.Series(np.zeros(numData))  
Vb[0] = 100  # 투자원금

for t in range(1, numData):
    Rb[t] = Rm[t]
    Vb[t] = Vb[t-1]*(1+Rb[t]*0.01)


# Portfolio BM DD
MAXb = Vb.cummax()
DDb = (Vb/MAXb - 1)*100 # 단위: %

# ===============================================================================
'그래프'

# Value MDD
fig = plt.figure(figsize=(10, 7)) # figsize = (가로길이, 세로길이)
gs = gridspec.GridSpec(nrows=2,   # row 개수 
                       ncols=1,   # col 개수
                       height_ratios=[8, 3],
                       width_ratios=[5])   # subplot



ax0 = plt.subplot(gs[0])
ax0.plot(Time, Vp, label='Dual Momentum', color='blue')  
ax0.plot(Time, Vb , label='VBM', color='red')
ax0.set_title('<Value>')
ax0.grid(True)
ax0.legend()


ax1 = plt.subplot(gs[1])
ax1.plot(Time, DDp, color='blue')
ax1.plot(Time, DDb, color='red')
ax1.set_title('<Draw-down>')
ax1.grid(True)

plt.show()





















