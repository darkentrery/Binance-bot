from asgiref.sync import sync_to_async
from binance.client import AsyncClient
from django.utils import timezone
from loguru import logger

from binance_bot.trades.models import Order, TradingStep


class OrdersManager:
    def __init__(self, step: TradingStep, price: float, client: AsyncClient) -> None:
        self.orders = None
        self.step = step
        self.price = price
        self.client = client

    async def monitoring_orders(self):
        self.orders = await sync_to_async(lambda: self.step.orders.filter(date_sell=None))()
        order_list = await sync_to_async(lambda: list(self.orders))()
        for order in order_list:
            await self.monitoring_buy(order)
            await self.monitoring_sell(order)
        if self.step.active:
            await self.monitoring_creat_order_buy()

    @property
    def open_price(self) -> float:
        price = 1
        while not (price <= self.price < price * (1 + self.step.step_float)):
            price *= (1 + self.step.step_float)
            price = round(price, 2)
        return price

    async def creat_order_sell(self, order: Order) -> None:
        b_order = await self.client.order_limit_sell(
            symbol=order.step.pair.name,
            quantity=order.value,
            price=order.price_sell
        )

        def update_order():
            order.order_sell = b_order['orderId']
            order.date_buy = timezone.now()
            order.save()

        await sync_to_async(update_order)()

    async def cancel_order_buy(self, order: Order) -> None:
        cancel = await self.client.cancel_order(symbol=order.step.pair.name, orderId=order.order_buy)
        await sync_to_async(lambda: order.delete())()

    async def monitoring_creat_order_buy(self) -> None:
        value_buy = self.step.value_buy(self.open_price)
        next_price = round(self.open_price * (1 + self.step.step_float), 2)
        balance = await self.balance()
        if balance > value_buy:
            if not await sync_to_async(lambda: self.orders.filter(price_buy=self.open_price).exists())():
                await self.creat_order_buy(self.open_price)
                logger.info(f"Open order for {self.step.pair.name=}, {self.step.value_tokens_buy(self.open_price)=}, {self.open_price=}")
            if not await sync_to_async(lambda: self.orders.filter(price_buy=next_price).exists())() and (next_price * 0.999) <= self.price:
                await self.creat_order_buy(next_price)
                logger.info(f"Open order for {self.step.pair.name=}, {self.step.value_tokens_buy(next_price)=}, {next_price=}")

    async def creat_order_buy(self, open_price: float) -> None:
        b_order = await self.client.order_limit_buy(
            symbol=self.step.pair.name,
            quantity=self.step.value_tokens_buy(open_price),
            price=open_price
        )
        await sync_to_async(lambda: Order.objects.create(
            step_id=self.step.id,
            price_buy=open_price,
            value=self.step.value_tokens_buy(open_price),
            order_buy=b_order["orderId"]
        ))()

    async def monitoring_buy(self, order: Order) -> None:
        if order.order_buy and not order.order_sell:
            b_order = await self.client.get_order(symbol=order.step.pair.name, orderId=order.order_buy)
            if b_order["status"] == "FILLED" and not order.date_buy:
                await self.creat_order_sell(order)
            elif b_order["status"] != "FILLED" and not order.date_buy and self.open_price != order.price_buy:
                await self.cancel_order_buy(order)

    async def monitoring_sell(self, order: Order) -> None:
        if order.order_sell:
            b_order = await self.client.get_order(symbol=order.step.pair.name, orderId=order.order_sell)
            if b_order["status"] == "FILLED":
                def sell():
                    order.date_sell = timezone.now()
                    order.save()
                await sync_to_async(sell)()

    async def balance(self):
        balance_USDT = await self.client.get_asset_balance(asset="USDT")
        return float(balance_USDT["free"])
