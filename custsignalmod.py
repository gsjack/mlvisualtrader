# Available indicators here: https://python-tradingview-ta.readthedocs.io/en/latest/usage.html#retrieving-the-analysis

from tradingview_ta import TA_Handler, Interval, Exchange
# use for environment variables
import os
# use if needed to pass args to external modules
import sys
# used for directory handling
import glob
import time
import threading

from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tensorflow.keras.models import Sequential, load_model
import matplotlib.pyplot as plt
import mpl_finance
import numpy as np
#os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"
# needed for the binance API and websockets
from binance.client import Client
from datetime import datetime

OSC_INDICATORS = ['MACD', 'Stoch.RSI', 'Mom'] # Indicators to use in Oscillator analysis
OSC_THRESHOLD = 2 # Must be less or equal to number of items in OSC_INDICATORS 
MA_INDICATORS = ['EMA10', 'EMA20'] # Indicators to use in Moving averages analysis
MA_THRESHOLD = 2 # Must be less or equal to number of items in MA_INDICATORS 
INTERVAL = Interval.INTERVAL_1_HOUR #Timeframe for analysis

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
PAIR_WITH = 'USDT'
TICKERS = 'signalsample.txt'
TIME_TO_WAIT = 4 # Minutes to wait between analysis
FULL_LOG = True # List analysis result to console

from helpers.parameters import (
    parse_args, load_config
)
# Load creds modules
from helpers.handle_creds import (
    load_correct_creds
)
args = parse_args()
DEFAULT_CREDS_FILE = 'creds.yml'
creds_file = args.creds if args.creds else DEFAULT_CREDS_FILE
parsed_creds = load_config(creds_file)
# Load creds for correct environment
access_key, secret_key = load_correct_creds(parsed_creds)

# Authenticate with the client
client = Client(access_key, secret_key)

img_width, img_height = 150, 150
model_path = '../src/models/model.h5'
weights_path = '../src/models/weights'
model = load_model('C://mlvisualtrader//src//models//model.h5')
#test_path = '../data/validation'

def predict(file):
  x = load_img(file, target_size=(img_width,img_height))
  x = img_to_array(x)
  x = np.expand_dims(x, axis=0)
  array = model.predict(x)
  result = array[0]
  if result[0] > result[1]:
    if result[0] > 0.1:
      print("Predicted answer: Buy")
      answer = 'buy'
      print(result)
      print(array)
    else:
      print("Predicted answer: Not confident")
      answer = 'n/a'
      print(result)
  else:
    if result[1] > 0.1:
      print("Predicted answer: Sell")
      answer = 'sell'
      print(result)
    else:
      print("Predicted answer: Not confident")
      answer = 'sell'
      print(result)

  return answer

def convolve_sma(array, period):
    return np.convolve(array, np.ones((period,))/period, mode='valid')

def analyze(pairs):
    open_val = []
    high_val = []
    low_val = []
    close_val = []
    volume2 = []    
    hlc3 = []      
    x = 0                                                 #KLINE_INTERVAL_1DAY
                                                                              #KLINE_INTERVAL_4HOUR
    for kline in client.get_historical_klines_generator("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "12 hours ago UTC"):


        if (x < 12):
            ts = int(kline[0]/1000)
            # if you encounter a "year is out of range" error the timestamp
            # may be in milliseconds, try `ts /= 1000` in that case
            print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
            #Adds ohlc values to lists
            open_val.append(float(kline[1]))
            high_val.append(float(kline[2]))
            low_val.append(float(kline[3]))
            close_val.append(float(kline[4]))
            volume2.append(float(kline[5])*100)
            hlc3temp = (float(kline[2]) + float(kline[3]) + float(kline[4]))/3
            hlc3.append(hlc3temp)
        x = x+1

    sma = convolve_sma(hlc3, 7)
    smb = list(sma)
    diff = sma[-1] - sma[-2]

    for x in range(len(close_val)-len(smb)):
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
    a = mpl_finance.volume_overlay(ax2, open_val, close_val, volume2, width=0.4, colorup='b', colordown='b', alpha=0)
    ax2.add_collection(a)
    ax2.grid(False)
    ax2.set_xticklabels([])
    ax2.set_yticklabels([])
    ax2.xaxis.set_visible(False)
    ax2.yaxis.set_visible(False)
    ax2.axis('off')
    mpl_finance.candlestick2_ochl(dx,open_val, close_val, high_val, low_val, width=1.5, colorup='g', colordown='r', alpha=0.5)

    plt.autoscale()
    plt.autoscale(ax2)
    plt.plot(smb, color="blue", linewidth=10, alpha=0.5)
    #plt.plot(smblong, color="black", linewidth=10, alpha=0.5)
    plt.axis('off')
    plt.savefig('live' +'.jpg', bbox_inches='tight')

    open_val.clear()
    close_val.clear()
    volume2.clear()
    high_val.clear()
    low_val.clear()
    hlc3.clear()
    plt.cla()
    plt.clf()


    signal_coins = {}
    analysis = {}
    handler = {}
    
    if os.path.exists('signals/custsignalmod.exs'):
        os.remove('signals/custsignalmod.exs')

    for pair in pairs:
        handler[pair] = TA_Handler(
            symbol=pair,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL,
            timeout= 10)
       
    for pair in pairs:
        try:
            analysis = handler[pair].get_analysis()
        except Exception as e:
            print("Signalsample:")
            print("Exception:")
            print(e)
            print (f'Coin: {pair}')
            print (f'handler: {handler[pair]}')

        oscCheck=0
        maCheck=0
        for indicator in OSC_INDICATORS:
            if analysis.oscillators ['COMPUTE'][indicator] == 'BUY': oscCheck +=1
      	
        for indicator in MA_INDICATORS:
            if analysis.moving_averages ['COMPUTE'][indicator] == 'BUY': maCheck +=1		

        if FULL_LOG:
            print(f'Custsignalmod:{pair} Oscillators:{oscCheck}/{len(OSC_INDICATORS)} Moving averages:{maCheck}/{len(MA_INDICATORS)}')
        
        #if oscCheck >= OSC_THRESHOLD and maCheck >= MA_THRESHOLD:
        result = predict('live.jpg')
        if result == "buy":
                signal_coins[pair] = pair
                print(f'Custsignalmod: Signal detected on {pair} at {oscCheck}/{len(OSC_INDICATORS)} oscillators and {maCheck}/{len(MA_INDICATORS)} moving averages.')
                with open('signals/custsignalmod.exs','a+') as f:
                    f.write(pair + '\n')
    
    return signal_coins

def do_work():
    signal_coins = {}
    pairs = {}

    pairs=[line.strip() for line in open(TICKERS)]
    for line in open(TICKERS):
        pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)] 
    
    while True:
        if not threading.main_thread().is_alive(): exit()
        print(f'Custsignalmod: Analyzing {len(pairs)} coins')
        signal_coins = analyze(pairs)
        print(f'Custsignalmod: {len(signal_coins)} coins above {OSC_THRESHOLD}/{len(OSC_INDICATORS)} oscillators and {MA_THRESHOLD}/{len(MA_INDICATORS)} moving averages Waiting {TIME_TO_WAIT} minutes for next analysis.')
        time.sleep((TIME_TO_WAIT*60))
