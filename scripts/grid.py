import json
import copy
from datetime import datetime

from asgiref.sync import sync_to_async
from binance.client import AsyncClient
from django.utils import timezone

from binance_bot.trades.models import Order, TradingStep


class Grid:
    def __init__(self, step, take_profit, value_buy, balance, PAIR, roun, data_path, filled_path, config_path, id):
        self.step = round(step / 100, 2)
        self.take_profit = 1 + round(take_profit / 100, 2)
        self.value_buy = value_buy
        self.balance = balance
        self.PAIR = PAIR
        self.round = roun
        self.count_steps = None
        self.id = id
        #{price: [value_buy, value_token, value_sell, price_sell, activated=False, buy=False, sell=False, time], }
        # {price: [value_buy, value_token, value_sell, price_sell, activated=False, buy=False, sell=False, time], }

    def count_money(self, at_time):
        profit = 0
        with open(self.file_orders_path, 'r') as data_file:
            filled_orders = json.load(data_file)
        if len(filled_orders):
            for f in filled_orders:
                for data in f:
                    if at_time <= datetime.fromisoformat(f[data][8]):
                        profit += (f[data][2] - f[data][0] - f[data][9] - f[data][10])
            print(f"На паре {self.PAIR} с процентом {self.step} заработано {profit}")
        return profit

    def range_determination(self): #определение диапазона открытия ордеров
        self.p = 1
        for n in range(5000):
            if not (self.p <= self.price < self.p * (1 + self.step)):
                self.p *= (1 + self.step)
                self.p = round(self.p, 2)
            else:
                break

    def get_count_steps(self, min_price, max_price):
        for p in range(1000):
            min_price *= (1 + self.step)
            self.count_steps = p
            if min_price >= max_price:
                break
        self.requirement_balance = self.value_buy * self.count_steps

    async def creat_order_sell(self):
        for d in self.data:
            if self.data[d][4] and self.data[d][5] and self.data[d][6] is None:
                order = await self.client.order_limit_sell(symbol=self.PAIR, quantity=self.data[d][1], price=self.data[d][3])
                self.data[d][6] = order['orderId']
                self.data[d][8] = str(datetime.now())
                self.data[d][4] = False  # размещение ордера на продажу
                #print(self.data)
                print("create_sell", self.data[d])
                self.write_data()

    async def creat_order_buy(self, p):
        p_1 = round(p * (1 + self.step), 2)
        if self.balance > self.value_buy_1(p):
            #print("Размещение покупки ордеров", p, self.data, p in self.data)
            if not (p in self.data):
                order = await self.client.order_limit_buy(symbol=self.PAIR, quantity=self.value_token(p), price=p)
                self.data[p] = [self.value_buy_1(p), self.value_token(p), self.value_sell_1(p), self.price_sell(p),
                                False, order['orderId'], None, str(datetime.now()), None, None, None]
                print(self.data)
                print("create_buy_p writed", self.data[p])
                self.write_data()
            if not (p_1 in self.data) and (p_1 * 0.999) <= self.price:
                order = await self.client.order_limit_buy(symbol=self.PAIR, quantity=self.value_token(p_1), price=p_1)
                self.data[p_1] = [self.value_buy_1(p_1), self.value_token(p_1), self.value_sell_1(p_1), self.price_sell(p_1),
                                  False, order['orderId'], None, str(datetime.now()), None, None, None]
                print(self.data)
                print("create_buy_p+1 writed", self.data[round(p * (1 + self.step), 2)])
                self.write_data()


    async def cancel_order_buy(self, p):
        sells = []
        for d in self.data:
            order = await self.client.get_order(symbol=self.PAIR, orderId=self.data[d][5])
            #print(d, p, round((d * (1 + self.step)), 2), round((p * (1 + self.step)), 2))
            if not self.data[d][4] and self.data[d][5] and (d != p or round((d * (1 + self.step)), 2) != round((p * (1 + self.step)), 2)) and order['status'] != 'FILLED':
                sells.append(d)  # отмена ордера на покупку
                cancel = await self.client.cancel_order(symbol=self.PAIR, orderId=self.data[d][5])
                print("cancel_order_buy", cancel['orderId'])

        for pr in sells:
            del self.data[pr]
        self.write_data()

    async def monitoring_buy(self):
        fee = lambda x: round(x * 0.0007, 6)
        for p in self.data:
            #print("Покупка/продажа ордеров", p, self.data, p in self.data)
            order = await self.client.get_order(symbol=self.PAIR, orderId=self.data[p][5])
            if order['status'] == 'FILLED' and not self.data[p][4] and self.data[p][6] is None: #покупка
                self.data[p][4] = True
                self.data[p][7] = str(datetime.now())
                self.data[p][9] = fee(self.data[p][0])
                self.balance -= self.data[p][0]
                print("buy", self.data[p])
                self.write_data()

    async def monitoring_sell(self):
        sells = []
        fee = lambda x: round(x * 0.0007, 6)
        for p in self.data:
            if not self.data[p][4] and self.data[p][6] is not None:#продажа
                order = await self.client.get_order(symbol=self.PAIR, orderId=self.data[p][6])
                if order['status'] == 'FILLED':
                    self.data[p][4] = True
                    self.data[p][8] = str(datetime.now())
                    self.data[p][10] = fee(self.data[p][2])
                    if self.count_steps:
                        self.value_buy += (self.data[p][2] - self.data[p][0] - self.data[p][9] - self.data[p][10]) / self.count_steps
                    self.balance += self.data[p][2]
                    sells.append(p)
                    self.filled_orders.append({p: copy.copy(self.data[p])})
                    print(f"sell {p}:{self.data[p]}")

        for p in sells:
            del self.data[p]
        self.write_data()
        self.write_filled_orders()
        self.set_config(self.PAIR, self.id, self.value_buy)

    async def open(self, price, client, balance):
        self.price = price
        self.client = client
        self.balance = balance
        self.price_0 = 1
        self.value_token = lambda x: round(self.value_buy / x, self.round)#self.price
        self.value_buy_1 = lambda x: round(self.value_token(x) * x, 6)#self.price
        self.value_sell_1 = lambda x: round(self.value_buy_1(x) * self.take_profit, 6)#
        self.price_sell = lambda x: round(self.take_profit * x, 2)#self.price

        self.range_determination()#определение диапазона открытия ордеров

        # await self.creat_order_sell()
        # await self.cancel_order_buy(self.p)
        # await self.creat_order_buy(self.p)
        await self.monitoring_buy()
        await self.monitoring_sell()

        #print("open")
        #for p in self.data:
        #    print(f"{p}: {self.data[p]}")


class OrdersManager:
    def __init__(self, step: TradingStep, price: float, client: AsyncClient) -> None:
        self.orders = None
        self.step = step
        # self.orders = step.orders.filter(date_sell=None)
        self.price = price
        self.client = client

    async def monitoring_orders(self):
        self.orders = await sync_to_async(lambda: self.step.orders.filter(date_sell=None))()
        order_list = await sync_to_async(lambda: [order for order in self.orders])()
        for order in order_list:
            await self.monitoring_buy(order)
            await self.monitoring_sell(order)
        await self.creat_order_buy()

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

    async def creat_order_buy(self) -> None:
        value_buy = self.step.value_buy(self.open_price)
        next_price = round(self.open_price * (1 + self.step.step_float), 2)
        balance = await self.balance
        if balance > value_buy:
            if not await sync_to_async(lambda: self.orders.filter(price_buy=self.open_price).exists())():
                # b_order = await self.client.order_limit_buy(
                #     symbol=self.step.pair.name,
                #     quantity=self.step.value_tokens_buy(self.open_price),
                #     price=self.open_price
                # )
                # await sync_to_async(lambda: Order.objects.create(
                #     step_id=self.step.id,
                #     price_buy=self.open_price,
                #     value=self.step.value_tokens_buy(self.open_price),
                #     order_buy=b_order["orderId"]
                # ))()
                pass
            if not await sync_to_async(lambda: self.orders.filter(price_buy=next_price).exists())() and (next_price * 0.999) <= self.price:
                # b_order = await self.client.order_limit_buy(
                #     symbol=self.step.pair.name,
                #     quantity=self.step.value_tokens_buy(next_price),
                #     price=next_price
                # )
                # await sync_to_async(lambda: Order.objects.create(
                #     step_id=self.step.id,
                #     price_buy=next_price,
                #     value=self.step.value_tokens_buy(next_price),
                #     order_buy=b_order["orderId"]
                # ))()
                pass

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

    @property
    async def balance(self):
        balance_USDT = await self.client.get_asset_balance(asset="USDT")
        return float(balance_USDT["free"])
