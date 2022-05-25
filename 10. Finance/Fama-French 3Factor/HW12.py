# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 12:47:35 2020

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
data_df1 = data_excel.parse(sheet_name='P_m', skiprows = 4) # m = Month, Price inDex에 해당하는 부분. 시장가로 지수를 가중 평균한 것.
rawTime1 = data_df1.iloc[:, 0].copy()
rawKOR1 = data_df1.iloc[:, 1].copy()    # Kospi 200
rawENE1 = data_df1.iloc[:, 2].copy()    # 에너지
rawMAT1 = data_df1.iloc[:, 3].copy()    # 소재
rawIND1 = data_df1.iloc[:, 4].copy()    # 산업재
rawCOD1 = data_df1.iloc[:, 5].copy()    # 경기관련소비재
rawCOS1 = data_df1.iloc[:, 6].copy()    # 필수소비재
rawHEL1 = data_df1.iloc[:, 7].copy()    # 건강관리
rawFIN1 = data_df1.iloc[:, 8].copy()    # 금융
rawINT1 = data_df1.iloc[:, 9].copy()    # 정보통신 
rawCOM1 = data_df1.iloc[:, 10].copy()   # 커뮤니케이션
rawUTI1 = data_df1.iloc[:, 11].copy()   # 유틸리티  

data_df2 = data_excel.parse(sheet_name='TR_m', skiprows = 4) # Total Return으로 배당을 재투자 했다고 가정하고 지수를 재산출한 것.
rawTime2 = data_df2.iloc[:, 0].copy()
rawKOR2 = data_df2.iloc[:, 1].copy()    # Kospi 200
rawENE2 = data_df2.iloc[:, 2].copy()    # 에너지
rawMAT2 = data_df2.iloc[:, 3].copy()    # 소재
rawIND2 = data_df2.iloc[:, 4].copy()    # 산업재
rawCOD2 = data_df2.iloc[:, 5].copy()    # 경기관련소비재
rawCOS2 = data_df2.iloc[:, 6].copy()    # 필수소비재
rawHEL2 = data_df2.iloc[:, 7].copy()    # 건강관리
rawFIN2 = data_df2.iloc[:, 8].copy()    # 금융
rawINT2 = data_df2.iloc[:, 9].copy()    # 정보통신 
rawCOM2 = data_df2.iloc[:, 10].copy()   # 커뮤니케이션
rawUTI2 = data_df2.iloc[:, 11].copy()   # 유틸리티  
rawCD1m = data_df2.iloc[:, 12].copy()   # CD금리 1개월

''' 엑셀 데이터에서 휴일 or Missing 데이터는 직전영업일 데이터로 대체함. 
이는 나중에 HPR에서 0이 나오는 경우가 있을 것.'''
#================================================================= 

'Sector HPR (based on TR Index, %)'
rawRm = rawKOR2.pct_change()*100    # Kospi200 리턴 (rawKOR/rawKOR.shift(1) -1)*100  이하 변수만 다를뿐 동문
rawR1 = rawENE2.pct_change()*100    # 에너지 리턴
rawR2 = rawMAT2.pct_change()*100    # 소재 리턴
rawR3 = rawIND2.pct_change()*100    # 산업재 리턴
rawR4 = rawCOD2.pct_change()*100    # 경기관련소비재 리턴
rawR5 = rawCOS2.pct_change()*100    # 필수소비재 리턴
rawR6 = rawHEL2.pct_change()*100    # 건강관리 리턴
rawR7 = rawFIN2.pct_change()*100    # 금융 리턴
rawR8 = rawINT2.pct_change()*100    # 정보통신 리턴
rawR9 = rawCOM2.pct_change()*100    # 커뮤니케이션 리턴
rawR10 = rawUTI2.pct_change()*100   # 유틸리티 리턴
rawRf = rawCD1m.shift(1)/12    # Risk free rate,  금리의 정의를 고려하여 한달 전 것을 가져와야 하기에 shift(1)


#==================================================================
'Sector Momentum (based on Price Index, %)'
# 시장가만 순수하게 움직인걸 이용한 것이 진정한 모멘텀이라고 생각해서 Price Index를 이용했다. (주관적 철학)
tau1 = 0  # 모멘템에 이용하기 위해서 데이터를 불러온다.
tau2 = 12  # 모멘템에 이용하기 위해서 데이터를 불러온다.
'''이때 기간을 두개로 설정한 이유: 오히려 최근 한달 전의 데이터는 역추세매매 
때문에 다음 한달(목표)과 역의 관계를 갖는 경우가 많다.
그래서 타우를 두개를 설정해 3개월 전부터 11개월 전부터와 같은 데이터를 이용하고자 한다'''

# 모멘텀 tau 1과 tau2 사이의 변화율 (단위:%)
rawMom1 = (rawENE1.shift(tau1)/rawENE1.shift(tau2) - 1)*100  
rawMom2 = (rawMAT1.shift(tau1)/rawMAT1.shift(tau2) - 1)*100  
rawMom3 = (rawIND1.shift(tau1)/rawIND1.shift(tau2) - 1)*100  
rawMom4 = (rawCOD1.shift(tau1)/rawCOD1.shift(tau2) - 1)*100  
rawMom5 = (rawCOS1.shift(tau1)/rawCOS1.shift(tau2) - 1)*100  
rawMom6 = (rawHEL1.shift(tau1)/rawHEL1.shift(tau2) - 1)*100  
rawMom7 = (rawFIN1.shift(tau1)/rawFIN1.shift(tau2) - 1)*100  
rawMom8 = (rawINT1.shift(tau1)/rawINT1.shift(tau2) - 1)*100  
rawMom9 = (rawCOM1.shift(tau1)/rawCOM1.shift(tau2) - 1)*100  
rawMom10 = (rawUTI1.shift(tau1)/rawUTI1.shift(tau2) - 1)*100  

#=====================================================================
'상대적 모멘텀을 이용하기 위해서 위에서 구한 Sector Momentum의 순위를 정한다.'
# rawTime1을 넣음으로써 시간을 확인할 수 있게함.
# rank_bf = pd.concat([rawTime1, rawMom1, rawMom2, rawMom3, rawMom4, rawMom5, rawMom6, rawMom7, rawMom8, rawMom9, rawMom10], axis = 1)
rank_bf = pd.concat([rawTime1, rawMom1, rawMom2, rawMom3, rawMom4, rawMom5, rawMom6, rawMom7, rawMom8, rawMom9, rawMom10], axis = 1)

# 시리즈 rank 매기기
rank1 = rank_bf.rank(ascending = False, method = 'min', axis=1) # 내림차순  엑셀에 나온 값.
rank2 = rank_bf.rank(ascending = True, method = 'min', axis=1)  # 올림차순

rank1_cp = rank1.copy().reset_index(drop=True)
rank2_cp = rank2.copy().reset_index(drop=True)
#================================================================
'순위를 매긴 것을 기준으로 decile portfolio를 만들고자 한다.'
'''Idea: decile portfolio 10%로 하면 내림차순 기준 1등하고 10등을 불러온다. 
   20%로 하면 1등 2등, 9등, 10등을 불러오는데 이때 9등 10등은 올림차순으로 봤을 때 2등, 1등이다.
   즉, decile portfolio 10%를 구성하는 것은 내림차순 1등, 올림차순 1등을 불러오는 것이다.
   이를 통해서 decile portfolio를 일반화하고자 한다.'''

Decile_size1 = 1               # (10%, if, Decile_size = 2 then 20%)
Decile_size2 = 1+10-Decile_size1


for i in range(12,238):
    for j in range(10):
        if rank1_cp.iloc[i][j] == Decile_size1:
            rank1_cp.iloc[i][j] = 1/Decile_size1
        else:
            rank1_cp.iloc[i][j] = 0

for i in range(12,238):
   for j in range(10):
        if rank2_cp.iloc[i][j] == 11 - Decile_size2:
            rank2_cp.iloc[i][j] = 1/(Decile_size2-11)  
        else:
            rank2_cp.iloc[i][j] = 0

ranked = rank1_cp + rank2_cp        # 위에서 짠 weight 둘다 합치기.

# 위 Decile을 구하는 idea를 적용하고자 노력은 해봤으나 Decilㄷ = 10%로 고정했을 때 밖에 못했다.
# rank < Decile_size1 일때에도 1/Decile_size1 이란 값이 나오도록 해야하는데 구현해봤으나 실패했다.



stDateNum = 20021231   # back test 시작일 (투자 시작일)
stDate = pd.to_datetime(str(stDateNum), format = '%Y%m%d')
idx = np.argmin(np.abs(rawTime2 - stDate))    # back test 시작일에 해당하는 index

# ============================================================
'최종 내림차순 기준 1등 asset엔 long, 10등 asset엔 short을 하는 Portfolio 만들기'

# asset 값 dataframe 만들기.
Rp_bf1 = pd.concat([rawR1, rawR2, rawR3, rawR4, rawR5, rawR6, rawR7, rawR8, rawR9, rawR10], axis = 1)

'시간 [t] 시점 맞추고자 값 깊은 복사'
Time = rawTime2[idx:].copy().reset_index(drop=True)   # 깊은 복사, index 초기화
Rp_bf = Rp_bf1[idx:].copy().reset_index(drop=True)
weight = ranked[idx:].copy().reset_index(drop=True)
numData = Time.shape[0]

Rp = pd.Series(np.zeros(numData))
Vp = pd.Series(np.zeros(numData))
Vp[0] = 100  # 투자원금

# ============================================
rawENE = weight.iloc[:, 0].copy()    # 에너지 WEIGHT 
rawMAT = weight.iloc[:, 1].copy()    # 소재 WEIGHT  
rawIND = weight.iloc[:, 2].copy()    # 산업재 WEIGHT  
rawCOD = weight.iloc[:, 3].copy()    # 경기관련소비재 WEIGHT 
rawCOS = weight.iloc[:, 4].copy()    # 필수소비재 WEIGHT  
rawHEL = weight.iloc[:, 5].copy()    # 건강관리 WEIGHT  
rawFIN = weight.iloc[:, 6].copy()    # 금융 WIGHT  
rawINT = weight.iloc[:, 7].copy()    # 정보통신 WEIGHT  
rawCOM = weight.iloc[:, 8].copy()   # 커뮤니케이션 WEIGHT   
rawUTI = weight.iloc[:, 9].copy()   # 유틸리티 WEIGHT 

RawENE = Rp_bf.iloc[:, 0].copy()    # 에너지 RETURN
RawMAT = Rp_bf.iloc[:, 1].copy()    # 소재 RETURN
RawIND = Rp_bf.iloc[:, 2].copy()    # 산업재 RETURN
RawCOD = Rp_bf.iloc[:, 3].copy()    # 경기관련소비재 RETURN
RawCOS = Rp_bf.iloc[:, 4].copy()    # 필수소비재 RETURN
RawHEL = Rp_bf.iloc[:, 5].copy()    # 건강관리 RETURN
RawFIN = Rp_bf.iloc[:, 6].copy()    # 금융 RETURN
RawINT = Rp_bf.iloc[:, 7].copy()    # 정보통신 RETURN
RawCOM = Rp_bf.iloc[:, 8].copy()   # 커뮤니케이션 RETURN
RawUTI = Rp_bf.iloc[:, 9].copy()   # 유틸리티 RETURN
#====================================================
'Portfolio의 Rp와 CSMom(Vp) 구하기.'
for t in range(1,numData):
    Rp[t] = rawENE[t-1]*RawENE[t] + rawMAT[t-1]*RawMAT[t] + rawIND[t-1]*RawIND[t] + rawCOD[t-1]*RawCOD[t] + rawCOS[t-1]*RawCOS[t] + rawHEL[t-1]*RawHEL[t] + rawFIN[t-1]*RawFIN[t] + rawINT[t-1]*RawINT[t] + rawCOM[t-1]*RawCOM[t] + rawUTI[t-1]*RawUTI[t]
    Vp[t] = Vp[t-1]*(1+Rp[t]/100)   


# Portfolio DD
MAXp = Vp.cummax()
DDp = (Vp/MAXp - 1)*100 # 단위: %

rawRm1 = rawRm[idx:].copy().reset_index(drop=True) 
RawRf = rawRf[idx:].copy().reset_index(drop=True)

# BM Portfolio 
Rb = pd.Series(np.zeros(numData))  # Rb = Rm-Rf, 마켓리턴 - 안전자산리턴(달러)
Vb = pd.Series(np.zeros(numData))  
Vb[0] = 100  # 투자원금

for t in range(1,numData):
    Rb[t] = rawRm1[t] - RawRf[t]
    Vb[t] = Vb[t-1]*(1+Rb[t]/100)

# Portfolio BM DD
MAXb = Vb.cummax()
DDb = (Vb/MAXb - 1)*100 # 단위: %


# Value MDD
fig = plt.figure(figsize=(10, 7)) # figsize = (가로길이, 세로길이)
gs = gridspec.GridSpec(nrows=2,   # row 개수 
                       ncols=1,   # col 개수
                       height_ratios=[8, 3],
                       width_ratios=[5])   # subplot



ax0 = plt.subplot(gs[0])
ax0.plot(Time, Vp, label='CS-Sector Momentum', color='blue')  
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