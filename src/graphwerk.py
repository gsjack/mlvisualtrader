from numpy import genfromtxt
import matplotlib.pyplot as plt
import mpl_finance
import numpy as np
import uuid

ad = genfromtxt(r'C:/mlvisualtrader/financial_data/Binance_BTCUSDT_1h_Future.csv', delimiter=',' ,dtype=str)
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
    for x in range(finish-start):

# Below filtering is valid for eurusd.csv file. Other financial data files have different orders so you need to find out
# what means open, high and close in their respective order.

        open.append(float(pd[start][1]))
        high.append(float(pd[start][2]))
        low.append(float(pd[start][3]))
        close.append(float(pd[start][4]))
        volume.append(float(pd[start][5])*100)
        date.append(pd[start][0])
        hlc3temp = (float(pd[start][2]) + float(pd[start][3]) + float(pd[start][4]))/3
        hlc3.append(hlc3temp)
        start = start + 1

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
    plt.plot(smb, color="blue", linewidth=10, alpha=0.5)
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