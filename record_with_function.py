from datetime import datetime
import ccxt
import time
from configparser import ConfigParser
import csv
import pandas as pd
import json
import pytz

#Read Config
config = ConfigParser()
config.read('config.ini')

apiKey = config['access']['apiKey']
secret = config['access']['secret']
account_name = config['access']['account_name']
product = config['product_parameter']['product']
rb_asset = config['product_parameter']['asset']
rb_buffer = config['product_parameter']['buffer']

#Account Access
exchange = ccxt.ftx({'apiKey' : apiKey ,'secret' : secret ,'enableRateLimit': True})
exchange.headers = {'FTX-SUBACCOUNT': account_name,}


#Port initial value
initial_price = float(config['initial_value']['initial_price']) #AP(0)
initial_port_value = float(config['initial_value']['initial_port_value']) #PV(0)

def get_balance():
    balance = exchange.fetchBalance()
    return balance

def get_product(product):
    product = exchange.fetchTicker(product)
    return product

def get_asset(asset):
    asset = get_balance()[rb_asset]['total']
    return asset

def get_cash(buffer):
    buffer = get_balance()[rb_buffer]['total']
    return buffer

def get_last_price():
    last_price = get_product(product)['last']
    return last_price

def get_asset_value():
    asset_value = get_asset(product) * get_last_price()
    return asset_value

def get_current_balance():
    current_value = get_asset_value() + get_cash(rb_buffer)
    return current_value

#Trading Record
def trading_record():
    price_diff = (get_last_price() - initial_price) / initial_price
    ini_hold_balance = initial_port_value + (initial_port_value * price_diff)
    port_diff = (get_current_balance() - initial_port_value) / initial_port_value
    cashflow = get_current_balance() - ini_hold_balance

    #Create dataframe
    try:
      read_log = pd.read_csv('test.csv')
    except:
      trading_log = pd.DataFrame(columns=['datetime', 'current_price', 'price_diff_percent', 'balance_diff_percent', 'initial_balance', 'current_balance', 'hold_balance', 'cashflow'])
      trading_log.to_csv('test.csv', index=False)
      print('Trading Log has been created.')

    #date_time
    get_datetime = datetime.now() 
    d = get_datetime.strptime(str(get_datetime), '%Y-%m-%d %H:%M:%S.%f')
    dt = d.strftime("%Y/%m/%d - %H:%M:%S")

    data = [dt, get_last_price(), price_diff * 100, port_diff * 100, initial_port_value, get_current_balance(), ini_hold_balance, cashflow]

    print(f'AP(0) {initial_price}, AP(1) {get_last_price()}')
    print(f'PV(0) {initial_port_value}, PV(1) {get_current_balance()}')
    print(f'Port Diff {port_diff * 100} % : Asset Price Diff {price_diff * 100} %')
    print(f'Cashflow is {cashflow}')


    with open('test.csv', "a+", newline='') as r:
      wr = csv.writer(r, dialect='excel')
      wr.writerow(data)
      print('Trading Log has been record.')

while True:
   try:    
     #time sequence
     time_seq = [1]
     time_mul = 60
     for i in time_seq:
       trading_record()
       print('\n''Time Sequence is : {}'.format(int(i)))
       print('----------------------------------------''\n')
       time.sleep(int(i) * time_mul)
   except Exception as e:
      print(f'Error : {e}')
      print('Try to run again...')
      time.sleep(600)




