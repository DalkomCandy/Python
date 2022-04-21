import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
from regex import R

import yfinance as yf
from datetime import datetime as dt
yf.pdr_override()

import warnings
warnings.filterwarnings("ignore")

def market_risk():
    return