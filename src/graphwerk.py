from numpy import genfromtxt
import matplotlib.pyplot as plt
import mpl_finance
import numpy as np
import uuid
import pandas as pd
import ta
from ta import add_all_ta_features
from ta.utils import dropna
from ta.volatility import BollingerBands

# Load datas
df = pd.read_csv(r'C:\mlvisualtrader\financial_data\Binance_BTCUSDT_1h_Backtest.csv', sep=',')
df = df.iloc[: , 1:]
# Clean NaN values
df = dropna(df)

df["ema"] = ta.trend.EMAIndicator(df["Close"], window = 14, fillna = False).ema_indicator()
df["sma"] = ta.trend.SMAIndicator(df["Close"], window = 14, fillna = False).sma_indicator()

# Add bollinger band high indicator filling nans values
df["bb_high_indicator"] = ta.volatility.bollinger_hband_indicator(
    df["Close"], window=20, window_dev=2, fillna=True
).bollinger_hband_indicator()

# Add bollinger band low indicator filling nans values
df["bb_low_indicator"] = ta.volatility.bollinger_lband_indicator(
    df["Close"], window=20, window_dev=2, fillna=True
).bollinger_lband_indicator()

asd  = ta.volatility.bollinger_lband_indicator(
    df["Close"], window=20, window_dev=2, fillna=True
)
df = df.to_csv(r'C:\mlvisualtrader\financial_data\Binance_BTCUSDT_1h_Backtest_with_indicators.csv')

ad = genfromtxt(r'C:/mlvisualtrader/financial_data/Binance_BTCUSDT_1h_Backtest_with_indicators.csv', delimiter=',' ,dtype=str, skip_header=1)
ad = np.delete(ad,0,1)
pd = np.flipud(ad)

buy_dir = 'C://mlvisualtrader//data//train//buy//'
sell_dir = 'C://mlvisualtrader//data//train//sell//'
neutral_dir = 'C://mlvisualtrader//data//train//neutral//'

def convolve_sma(array, period):
    return np.convolve(array, np.ones((period,))/period, mode='valid')

def graphwerk(start, finish):
    open = []
    high = []
    low = []
    close = []
    volume = []
    date = []
    hlc3 = []
    bbupper = []
    bblower = []
    mySMA = []
    myEMA = []


    for x in range(finish-start):

# Below filtering is valid for eurusd.csv file. Other financial data files have different orders so you need to find out
# what means open, high and close in their respective order.
        start = start + 1
        open.append(float(pd[start][1]))
        high.append(float(pd[start][2]))
        low.append(float(pd[start][3]))
        close.append(float(pd[start][4]))
        volume.append(float(pd[start][5])*100)
        date.append(pd[start][0])
        hlc3temp = (float(pd[start][2]) + float(pd[start][3]) + float(pd[start][4]))/3
        hlc3.append(hlc3temp)
        myEMA.append(float(pd[start][6]))
        mySMA.append(float(pd[start][7]))
        bbupper.append(float(pd[start][8]))
        bblower.append(float(pd[start][9]))
        
    close_next = float(pd[finish][4])
   
    sma = convolve_sma(hlc3, 7)
    smb = list(sma)
    diff = sma[-1] - sma[-2]

    for x in range(len(close)-len(smb)):
        smb.append(smb[-1]+diff)

    fig = plt.figure(num=1, figsize=(3, 3), dpi=50, facecolor='w', edgecolor='k')
    dx = fig.add_subplot(111)
    dx.grid(False)
    dx.set_xticklabels([])
    dx.set_yticklabels([])
    dx.xaxis.set_visible(False)
    dx.yaxis.set_visible(False)
    dx.axis('off')
    ax2 = dx.twinx()
    a = mpl_finance.volume_overlay(ax2, open, close, volume, width=0.4, colorup='b', colordown='b', alpha=0)
    ax2.add_collection(a)
    ax2.grid(False)
    ax2.set_xticklabels([])
    ax2.set_yticklabels([])
    ax2.xaxis.set_visible(False)
    ax2.yaxis.set_visible(False)
    ax2.axis('off')
    mpl_finance.candlestick2_ochl(dx,open, close, high, low, width=1.5, colorup='g', colordown='r', alpha=0.5)

    plt.autoscale()
    plt.autoscale(ax2)
    plt.plot(smb, color="blue", linewidth=10, alpha=0.25)
    plt.plot(bbupper, color="black", linewidth=10, alpha=0.25)
    plt.plot(bblower, color="orange", linewidth=10, alpha=0.25)
    plt.plot(myEMA, color="green", linewidth=10, alpha=0.25)
    plt.plot(mySMA, color="yellow", linewidth=10, alpha=0.25)
    
    #plt.plot(smblong, color="black", linewidth=10, alpha=0.5)
    plt.axis('off')
    comp_ratio = close_next / close[-1]
    print(comp_ratio)

    if close_next/close[-1] > 1.01:
            print('last value: ' + str(close[-1]))
            print('next value: ' + str(close_next))
            print('buy')
            plt.savefig(buy_dir + str(uuid.uuid4()) +'.jpg', bbox_inches='tight')
    elif close_next/close[-1]<0.99:
            print('last value: '+ str(close[-1]))
            print('next value: ' + str(close_next))
            print('sell')
            plt.savefig(sell_dir + str(uuid.uuid4())+'.jpg', bbox_inches='tight')
    else:
            print('close value is smaller')
            print('last value: '+ str(close[-1]))
            print('next value: ' + str(close_next))
            print('neutral')
            plt.savefig(neutral_dir + str(uuid.uuid4())+'.jpg', bbox_inches='tight')


    #plt.show()
    open.clear()
    close.clear()
    volume.clear()
    high.clear()
    low.clear()
    hlc3.clear()
    plt.cla()
    plt.clf()



iter_count = int(len(pd)/4)
print(iter_count)
iter = 0


for x in range(len(pd)-4):
   graphwerk(iter, iter+12) #eigentlich nur 12. 13 zum check
   iter = iter + 2