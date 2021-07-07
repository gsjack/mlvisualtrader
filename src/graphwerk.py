from numpy import genfromtxt
import matplotlib.pyplot as plt
import mpl_finance
import numpy as np
import uuid

# Input your csv file here with historical data
def timeConversion(s):
   if s[-2:] == "AM" :
      if s[:2] == '12':
          a = str('00' + s[2:8])
      else:
          a = s[:-2]
   else:
      if s[:2] == '12':
          a = s[:-2]
      else:
          a = str(int(s[:2]) + 12) + s[2:8]
   return a

ad = genfromtxt(r'C:/mlvisualtrader/financial_data/Binance_BTCUSDT_1h.csv', delimiter=',' ,dtype=str)
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
    for x in range(finish-start):

# Below filtering is valid for eurusd.csv file. Other financial data files have different orders so you need to find out
# what means open, high and close in their respective order.

        open.append(float(pd[start][1]))
        high.append(float(pd[start][2]))
        low.append(float(pd[start][3]))
        close.append(float(pd[start][4]))
        volume.append(float(pd[start][5]))
        date.append(pd[start][0])
        start = start + 1

    close_next = float(pd[finish][4])

    sma = convolve_sma(close, 6)
    smb = list(sma)
    diff = sma[-1] - sma[-2]

    for x in range(len(close)-len(smb)):
        smb.append(smb[-1]+diff)

    smalong = convolve_sma(close, 12)
    smblong = list(smalong)
    #difflong = smalong[-1] - smalong[-2]

    #for x in range(len(close)-len(smblong)):
    #    smblong.append(smblong[-1]+difflong)

    fig = plt.figure(num=1, figsize=(3, 3), dpi=50, facecolor='w', edgecolor='k')
    dx = fig.add_subplot(111)
    #mpl_finance.volume_overlay(ax, open, close, volume, width=0.4, colorup='b', colordown='b', alpha=1)
    mpl_finance.candlestick2_ochl(dx,open, close, high, low, width=1.5, colorup='g', colordown='r', alpha=0.5)

    plt.autoscale()
    plt.plot(smb, color="blue", linewidth=10, alpha=0.5)
    #plt.plot(smblong, color="black", linewidth=10, alpha=0.5)
    plt.axis('off')
    comp_ratio = close_next / close[-1]
    print(comp_ratio)

    if close[-3]*1.01 < close_next and close[-2] < close_next and close[-1] < close_next:
            print('last value: ' + str(close[-1]))
            print('next value: ' + str(close_next))
            print('buy')
            plt.savefig(buy_dir + str(uuid.uuid4()) +'.jpg', bbox_inches='tight')
    elif close[-3]*1.01 > close_next and close[-2] > close_next and close[-1] > close_next:
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
    plt.cla()
    plt.clf()



iter_count = int(len(pd)/4)
print(iter_count)
iter = 0


for x in range(len(pd)-4):
   graphwerk(iter, iter+12)
   iter = iter + 2