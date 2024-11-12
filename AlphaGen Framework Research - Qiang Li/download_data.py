import requests
import time
import datetime
import csv
import argparse
import os
import pandas as pd
from data_collection.qlib_dump_bin import DumpDataAll


BASE_URL = 'https://api.binance.com'
KLINE_ENDPOINT = '/api/v3/klines'
INTERVALS = ['15m', '1h']
LIMIT = 1000  # Maximum allowed by Binance API
data_path = './my_data/original/'
new_data_path = './my_data/basic/'

def fetch_klines(symbol, interval, start_ts, end_ts, limit=1000):
    url = BASE_URL + KLINE_ENDPOINT
    while start_ts < end_ts:
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_ts,
            'limit': limit
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code} {response.text}")
            break
        data = response.json()
        if not data:
            break
        yield from data
        # Update start_ts to last kline's close time
        last_kline = data[-1]
        start_ts = last_kline[6]  # kline[6] is closeTime
        # Add 1 millisecond to avoid overlapping
        start_ts += 1
        # To prevent hitting rate limits
        time.sleep(0.5)

def convert_qlib():
    for file in os.listdir(data_path):
        data = pd.read_csv(data_path+file)
        data['Open time'] = pd.to_datetime(data['Open time'], unit='ms')
        data['Close time'] = pd.to_datetime(data['Close time'], unit='ms')
        data['code'] = file[:-9]
        data.columns = data.columns.str.replace(' ', '_')
        data.to_csv(new_data_path+file, index=None)

    DumpDataAll(
            csv_path='./my_data/basic',
            qlib_dir='./my_data/qlib',
            max_workers=50,
            exclude_fields="Open_time,code,Close_time,Ignore",
            symbol_field_name="code",
            date_field_name='Open_time',
            freq='min'
    ).dump()

def main():
    parser = argparse.ArgumentParser(description='Download Binance kline data.')
    parser.add_argument('--symbols', nargs='+', default=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'], help='Symbols to fetch data for (e.g., BTCUSDT ETHUSDT)')
    args = parser.parse_args()
    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(days=365*2)
    start_ts = int(start_time.timestamp() * 1000)  # Convert to milliseconds
    end_ts = int(now.timestamp() * 1000)
    for symbol in args.symbols:
        for interval in INTERVALS:
            print(f"Fetching data for {symbol} interval {interval}")
            start_ts_interval = start_ts  # Reset start_ts for each interval
            filename = f"./my_data/original/{symbol}_{interval}_data.csv"
            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                # Write header
                csvwriter.writerow(['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 
                                    'Quote asset volume', 'Number of trades', 
                                    'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
                # Fetch and write data
                for kline in fetch_klines(symbol, interval, start_ts_interval, end_ts):
                    csvwriter.writerow(kline)
            print(f"Saved data to {filename}")
    convert_qlib()

if __name__ == "__main__":
    main()