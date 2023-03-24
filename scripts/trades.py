import asyncio
import datetime

from asgiref.sync import sync_to_async
from binance.client import AsyncClient
from loguru import logger

from binance_bot.trades.models import TradingStep, Order
from config.settings.base import BINANCE_API_KEY, BINANCE_API_SECRET
from scripts.grid import OrdersManager


@logger.catch
async def balance(PAIR):
    client = await AsyncClient.create(BINANCE_API_KEY, BINANCE_API_SECRET)
    #prices = await client.get_exchange_info()
    info = await client.get_all_tickers()
    price = [i for i in info if i['symbol'] == PAIR]
    balances = await client.get_account()
    #balance = await client.get_asset_balance(asset='BTC')
    await client.close_connection()
    return price, balances['balances']


async def set_sell_orders(client: AsyncClient, symbol: str) -> None:
    b_orders = await client.get_all_orders(symbol=symbol)
    orders = list(filter(lambda x: x["side"] == "SELL" and x["status"] == "NEW", b_orders))
    for order in orders:
        volume = float(order["origQty"])
        # step = 2 if float(order["price"]) * volume < 90 else 10
        step = 20
        price_buy = round(float(order["price"]) / (1 + round(step / 100, 2)), 6)
        time = datetime.datetime.fromtimestamp(order["time"] // 1000)
        trading_step = await sync_to_async(lambda: TradingStep.objects.get(step=step, pair__name=order["symbol"]))()
        await sync_to_async(lambda: Order.objects.create(step_id=trading_step.id, price_buy=price_buy, value=volume, date_buy=time))()

@logger.catch
async def trade() -> None:
    client = await AsyncClient.create(BINANCE_API_KEY, BINANCE_API_SECRET)
    at_time = datetime.datetime(year=2022, month=3, day=1, hour=0)
    # profit = 0
    # for grid in grids:
    #     profit += grid['grid'].count_money(at_time)
    # print(profit)
    # input()

    while True:
        await asyncio.sleep(4)
        steps = await sync_to_async(lambda: TradingStep.objects.filter(active=True))()
        steps = await sync_to_async(lambda: [step for step in steps])()
        for step in steps:
            symbol = await sync_to_async(lambda: step.pair.name)()
            price = float((await client.get_symbol_ticker(symbol=symbol))["price"])
            manager = OrdersManager(step, price, client)
            await manager.monitoring_orders()
        # balance_BNB = await client.get_asset_balance(asset='BNB')
        # balance_ETH = await client.get_asset_balance(asset='ETH')
        # balance_BTC = await client.get_asset_balance(asset='BTC')
        # #balance_BUSD = await client.get_asset_balance(asset='BUSD')
        # balance_USDT = await client.get_asset_balance(asset='USDT')
        # print(balance_BNB, balance_ETH, balance_BTC, balance_USDT)
        # for grid in grids:
        #     price = float((await client.get_symbol_ticker(symbol=grid['pair']))['price'])
        #     await grid['grid'].open(price, client, float(balance_USDT['free']))
    await client.close_connection()


def trade_loop() -> None:
    while True:
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(trade())
        except Exception as e:
            print(f"Произошла ошибка {e}")
