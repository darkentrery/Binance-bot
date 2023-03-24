# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import asyncio
import datetime
import os
import json

from binance.client import AsyncClient
from loguru import logger
import matplotlib.pyplot as plt
from test import Grid


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")

#myapi
API_KEY='muiG8uwqq4E01AcZWITtRfpBnU2zbpPrvv2pGtJh9o7CLgWNC37br4MqxGTk3KTy'
API_SECRET='Hy6TideNYNLFGwUIbqcUvIzDTTV5jYgTuheVFmkriL2a8A6CjmoxjXnPz8pg7Sqn'

directory = os.getcwd()
config = 'config_a.json'
data = 'config_data_test.json'

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


def set_data(file_name, data):
    file_path = f"{directory}/{file_name}"
    with open(file_path, 'w') as data_file:
        json.dump(data, data_file)

def get_statistic(DATA):
    for p in DATA:
        for id, step in enumerate(p['steps']):
            data_path = f"{directory}/statistic/statistic_{p['pair']}_{step['step']}.json"
            if not os.path.isfile(data_path):
                with open(data_path, 'w') as data_file:
                    json.dump('', data_file)

def set_statistic(pair, step, time, statistic):
    data_path = f"{directory}/statistic/statistic_{pair}_{int(step)}.json"
    with open(data_path, 'a') as data_file:
        json.dump({time: statistic}, data_file)
        data_file.write('\n')

def create_grafic(pair, step):
    fig, ax = plt.subplots(2, 2)
    ax[1, 1].set_ylim([0, 150])
    color = {0: 'b', 1: 'g', 2: 'r', 3: 'c', 4: 'm', 5: 'y', 6: 'k', 7: 'w'}
    price = []
    balance = []
    full_balance = []
    profit = []
    date = []
    percent = []
    percent_full = []
    data_path = f"{directory}/statistic/statistic_{pair}_{int(step)}.json"
    with open(data_path, 'r') as data_file:
        for line in data_file.readlines():
            y = json.loads(line.strip())
            for d in y:
                date.append(d)
                price.append(y[d]['price'])
                balance.append(y[d]['balance'])
                full_balance.append(y[d]['full_balance'])
                profit.append(y[d]['profit'])
                percent.append(y[d]['percent'])
                percent_full.append(y[d]['percent_full'])

        #price = [json.loads(line.strip())['price']for line in data_file.readlines()]
        #balance = [json.loads(line.strip())['balance'] for line in data_file.readlines()]
        #full_balance = [json.loads(line.strip())['full_balance'] for line in data_file.readlines()]
        #profit = [json.loads(line.strip())['profit'] for line in data_file.readlines()]
        #date = [json.loads(line.strip())['profit'] for line in data_file.readlines()]

    ax[0, 0].plot(date, price, color=color[0], linewidth=1)
    ax[0, 1].plot(date, profit, color=color[1], linewidth=1)
    ax[1, 0].plot(date, full_balance, color=color[2], linewidth=1)
    ax[1, 0].plot(date, balance, color=color[3], linewidth=1)
    ax[1, 1].plot(date, percent, color=color[4], linewidth=1)
    ax[1, 1].plot(date, percent_full, color=color[5], linewidth=1)


    plt.show()







@logger.catch
async def main():
    API_KEY, API_SECRET = get_keys(config)
    DATA = get_data(data)
    grids = get_grids(DATA)
    print(f"{DATA=}")
    print(f"{grids=}")

    #get_statistic(DATA)

    client = await AsyncClient.create(API_KEY, API_SECRET)
    info = await client.get_symbol_ticker(symbol=DATA[0]["pair"])
    print(info)
    time = await client.get_server_time()
    print(time)
    day = 360
    i = 0
    iss = 1440 * day / 5
    per = 0
    for d in DATA:
        async for kline in await client.get_historical_klines_generator(d["pair"], AsyncClient.KLINE_INTERVAL_5MINUTE, f"{day} day ago UTC"):
            #print(kline)
            t = datetime.datetime.fromtimestamp(kline[0] // 1000).strftime('%d.%m.%Y %H:%M')
            days = day - (time['serverTime'] - kline[0]) / (864 * 10 ** 5)
            price = float(kline[1])
            for grid in grids:
                if d["pair"] == grid['pair']:
                    grid['grid'].open(price)
                    statistic = grid['grid'].statistic(days)
                    set_statistic(grid['grid'].PAIR, grid['grid'].step * 100, t, statistic)


                    #y[grid['grid'].id].append(statistic['profit'])



            i += 1
            if iss // 20 == i:
                i = 0
                per += 5
                print(per, "%")
        i = 0
        per = 0
        print(f"{d['pair']} completed")

        for grid in grids:
            #print(grid['grid'].requirement_balance, grid['grid'].min_balance)
            parametrs = grid['grid'].show(day)
            print(parametrs)



    #price = float(info['price'])

    #print(price)
    #balance = await client.get_asset_balance(asset='BNB')
    #print(balance)

    #order = await client.order_limit_buy(symbol=PAIR, quantity=0.0044, price=2394.98)
    #print(order['orderId'])
    #order = await client.order_limit_sell(symbol='BNBBUSD', quantity=0.025, price=400)

    #print(order)
    #balance = await client.get_asset_balance(asset='BUSD')
    #print(balance)
    #order = await client.get_open_orders(symbol=PAIR)
    #print(order)
    #cancel = await client.cancel_order(symbol=PAIR, orderId=order['orderId'])
    #print(cancel, cancel['orderId'])


    #cancel = await client.cancel_order(symbol='BNBBUSD', orderId=order['orderId'])
    #print(cancel)
    await client.close_connection()

@logger.catch
def start_test():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start_test()
    #create_grafic('ETHUSDT', 10)
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
