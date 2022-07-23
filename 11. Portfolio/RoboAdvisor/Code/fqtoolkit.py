import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])

##############################################################

def dgToDf(fileName, sheetName, featureNum):
    
    data = pd.read_excel(fileName, sheet_name=sheetName)

    

    index = data.iloc[13:, 0]


    db = {}

    dataName = []

    for r in range(featureNum):

        dataName.append(data.iloc[11, r+1])

        db[r] = {}
        
        
    if featureNum == 1:


        db[0] = pd.DataFrame(data.iloc[13:, 1:].values,  index=index,columns=data.iloc[8, 1:])
            
    else:
        
        
        for n in range((data.shape[1]-1)//featureNum):

            for n2 in range(featureNum):

                name = data.iloc[8, n*featureNum+n2+1]

                db[n2][name] = data.iloc[13:, n*featureNum+n2+1].values


        for r in range(featureNum):

            db[r] = pd.DataFrame(db[r], index=index)

    
        
    return db

def indFinder(factor, q, n):
    
    factor = factor.dropna().sort_values()
    
    
    return factor.iloc[int(len(factor)*(n-1)/q):int(len(factor)*(n)/q)].index

def portMaker(factor, returns, q, rebalancing):
    
    portDf = {}
    
    
    for r in range(q):
        
        reList = []
    
        for date in returns.iloc[::rebalancing, :].index:

            inds = indFinder(factor.loc[date, :], q=q, n=(r+1))
        
            
            re = returns.loc[date , inds].mean()
            
            reList.append(re)

            
        portDf[r] = reList
        
    return pd.DataFrame(portDf, index=returns.iloc[::rebalancing, :].index)



def cumulateVisualizer(data, figureName, log=True):
    
    data = (data+1).cumprod()
    
    plt.style.use("ggplot")
    plt.figure(figsize=(10, 6))
    plt.title(figureName)
    
    
    if log:

        for col in data.columns:

            plt.plot(np.log(data[col]), label=f"{col+1}th quantile", color=lighten_color("black",   amount=(int(col)+int((data.shape[1])/2))/(int((data.shape[1])/2)+(data.shape[1]))))
            plt.ylabel("Log Cumulative Return")
            
    else:
        
        for col in data.columns:
        
            plt.plot((data[col]), label=f"{col+1}th quantile", color=lighten_color("black",   amount=(int(col)+int((data.shape[1])/2))/(int((data.shape[1])/2)+(data.shape[1]))))
            
            plt.ylabel("Cumulative Return")
            
    plt.legend()
    
    plt.show()