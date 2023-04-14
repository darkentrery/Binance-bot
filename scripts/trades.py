import asyncio
import datetime

from asgiref.sync import sync_to_async
from binance.client import AsyncClient
from loguru import logger

from binance_bot.trades.models import TradingStep, Order, Pair
from config.settings.base import BINANCE_API_KEY, BINANCE_API_SECRET
from scripts.grid import OrdersManager


async def set_sell_orders_for_symbol(client: AsyncClient, symbol: str) -> None:
    b_orders = await client.get_all_orders(symbol=symbol)
    orders = list(filter(lambda x: x["side"] == "SELL" and x["status"] == "NEW", b_orders))
    for order in orders:
        volume = float(order["origQty"])
        if symbol == "RUNEUSDT":
            step = 20
        else:
            step = 2 if float(order["price"]) * volume < 90 else 10
        price_buy = round(float(order["price"]) / (1 + round(step / 100, 2)), 2)
        time = datetime.datetime.fromtimestamp(order["time"] // 1000)
        trading_step = await sync_to_async(lambda: TradingStep.objects.get(step=step, pair__name=order["symbol"]))()
        await sync_to_async(lambda: Order.objects.create(
            step_id=trading_step.id,
            price_buy=price_buy,
            value=volume,
            date_buy=time,
            order_sell=order["orderId"]
        ))()


async def set_sell_orders():
    client = await AsyncClient.create(BINANCE_API_KEY, BINANCE_API_SECRET)
    symbols = await sync_to_async(lambda: list(Pair.objects.all().values_list("name", flat=True)))()
    for symbol in symbols:
        await set_sell_orders_for_symbol(client, symbol)
    await client.close_connection()


@logger.catch
async def trade() -> None:
    client = await AsyncClient.create(BINANCE_API_KEY, BINANCE_API_SECRET)
    try:
        while True:
            await asyncio.sleep(4)
            steps = await sync_to_async(lambda: [step for step in TradingStep.objects.all()])()
            for step in steps:
                symbol = await sync_to_async(lambda: step.pair.name)()
                price = float((await client.get_symbol_ticker(symbol=symbol))["price"])
                manager = OrdersManager(step, price, client)
                await manager.monitoring_orders()
    except Exception as e:
        logger.error(e)
        await client.close_connection()


def trade_loop() -> None:
    while True:
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(trade())
        except Exception as e:
            logger.error(e)
