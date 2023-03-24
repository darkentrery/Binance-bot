# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import asyncio
import os
import json
from datetime import datetime

from binance.client import AsyncClient
from loguru import logger
from grid import Grid

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")
directory = os.getcwd()
config = 'config_a.json'
data = 'config_data.json'


#DATA = [
#    {'pair': 'ETHUSDT', 'roun': 4, 'steps': [{'step': 2, 'value': 25}, {'step': 10, 'value': 100}]},
#    {'pair': 'BTCUSDT', 'roun': 5, 'steps': [{'step': 2, 'value': 25}, {'step': 10, 'value': 100}]},
#    {'pair': 'RUNEUSDT', 'roun': 1, 'steps': [{'step': 20, 'value': 50}]}
#]

def get_keys(config):
    file_keys_path = f"{directory}/{config}"
    with open(file_keys_path, 'r') as data_file:
        data = json.load(data_file)
        API_KEY = [chr(k) for k in data['API_KEY']]
        API_KEY = "".join(API_KEY)
        API_SECRET = [chr(k) for k in data['API_SECRET']]
        API_SECRET = "".join(API_SECRET)
    return API_KEY, API_SECRET

def get_data(data):
    file_keys_path = f"{directory}/{data}"
    with open(file_keys_path, 'r') as data_file:
        data = json.load(data_file)
    return data

def set_data(file_name, data):
    file_path = f"{directory}/{file_name}"
    with open(file_path, 'w') as data_file:
        json.dump(data, data_file)

def get_grids(DATA):
    grids = []
    config_path = f"{directory}/{data}"
    for p in DATA:
        for id, step in enumerate(p['steps']):
            data_path = f"{directory}/orders_test/data_{p['pair']}_{step['step']}.json"
            filled_path = f"{directory}/orders_test/filled_orders_{p['pair']}_{step['step']}.json"
            if not os.path.isfile(data_path):
                with open(data_path, 'w') as data_file:
                    json.dump({}, data_file)
            if not os.path.isfile(filled_path):
                with open(filled_path, 'w') as data_file:
                    json.dump([], data_file)
            grid = Grid(step=step['step'], take_profit=step['step'], value_buy=step['value'], balance=50, PAIR=p['pair'], roun=p['roun'], data_path=data_path, filled_path=filled_path, config_path=config_path, id=id)
            grid.get_count_steps(p['min_price'], p['max_price'])
            grids.append({'pair': p['pair'], 'grid': grid})
    return grids

@logger.catch
async def balance(API_KEY, API_SECRET, PAIR):
    client = await AsyncClient.create(API_KEY, API_SECRET)
    #prices = await client.get_exchange_info()
    info = await client.get_all_tickers()
    price = [i for i in info if i['symbol'] == PAIR]
    balances = await client.get_account()
    #balance = await client.get_asset_balance(asset='BTC')
    await client.close_connection()
    return price, balances['balances']

@logger.catch
async def trade(API_KEY, API_SECRET, grids, DATA):
    #client = await AsyncClient.create(API_KEY, API_SECRET)
    at_time = datetime(year=2022, month=3, day=1, hour=0)
    profit = 0
    for grid in grids:
        profit += grid['grid'].count_money(at_time)
    print(profit)
    input()

    """while True:
        await asyncio.sleep(4)
        balance_BNB = await client.get_asset_balance(asset='BNB')
        balance_ETH = await client.get_asset_balance(asset='ETH')
        balance_BTC = await client.get_asset_balance(asset='BTC')
        #balance_BUSD = await client.get_asset_balance(asset='BUSD')
        balance_USDT = await client.get_asset_balance(asset='USDT')
        print(balance_BNB, balance_ETH, balance_BTC, balance_USDT)
        for grid in grids:
            price = float((await client.get_symbol_ticker(symbol=grid['pair']))['price'])
            await grid['grid'].open(price, client, float(balance_USDT['free']))
    await client.close_connection()"""



@logger.catch
def start():
    DATA = get_data(data)
    grids = get_grids(DATA)
    API_KEY, API_SECRET = get_keys(config)
    while True:
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(trade(API_KEY, API_SECRET, grids, DATA))
        except:
            print(f"Произошла ошибка {Exception}")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
