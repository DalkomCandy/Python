# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os     # F9 누르면 실행
os.getcwd()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

data_excel = pd.ExcelFile('C:/Users/RadarJ/Desktop/CLASSES/2nd Grade/2학기/Trading by 양기성/수업/HW09_편재원.xlsx')
data_df = data_excel.parse(sheet_name='data_m')
rawTime = data_df.iloc[:, 0].copy()
rawRisky = data_df.iloc[:, 1].copy()
rawRf = data_df.iloc[:, 3].copy()

rawR1 = rawRisky.pct_change()*100
rawR2 = rawRf.shift(1)/12

tau = 12
rawMom = rawRisky.pct_change(tau)*100
rawSignal = 1*(rawMom >0)

stDateNum = 19941228
stDate = pd.to_datetime(str(stDateNum), format = '%Y%m%d')
idx = np.argmin(np.abs(rawTime - stDate))

Time = rawTime[idx:].copy().reset_index(drop=True)
R1 = rawR1[idx:].copy().reset_index(drop=True)
R2 = rawR2[idx:].copy().reset_index(drop=True)
Signal = rawSignal.iloc[idx:].copy().reset_index(drop=True)
numData = Time.shape[0]

W1 = Signal
W2 = 1 - W1

Rp = pd.Series(np.zeros(numData))
Vp = pd.Series(np.zeros(numData))    # value
Vp[0] = 100   # 투자원금
for t in range(1,numData):
    Rp[t] = W1[t-1]*R1[t] + W2[t-1]*R2[t]
    Vp[t] = Vp[t-1]*(1+Rp[t]/100)   
    
MAXp = Vp.cummax()
DDp = (Vp/MAXp -1)*100

Risky = rawRisky[idx:].copy().reset_index(drop=True)

Vb = (rawRisky[idx:]/rawRisky[idx]).reset_index(drop=True)*100

MAXb = Vb.cummax()
DDb = (Vb/MAXb -1)*100


plt.figure(figsize=(10,5))
plt.plot(Time, Vp, Label = 'Mom_12m')
plt.plot(Time, Vb, label = 'K200')
plt.legend()
plt.title('<Time-series Momentum Strategy>')
plt.xlabel('time')
plt.ylabel('value')
plt.show()

fig = plt.figure(figsize=(10, 7)) 
gs = gridspec.GridSpec(nrows=2,
                       ncols=1,
                       height_ratios=[8, 3],
                       width_ratios=[5])

ax0 = plt.subplot(gs[0])
ax0.plot(Time, Vp, label='Mom_12m')
ax0.plot(Time, Vb, label = 'K200')
ax0.set_title('<Value>')
ax0.grid(True)
ax0.legend()

ax1 = plt.subplot(gs[1])
ax1.plot(Time, DDp, label='Mom_12')
ax1.plot(Time, DDb, label='K200')
ax1.set_title('<Draw-down>')
ax1.grid(True)
ax1.legend()

plt.show
    
    

 




