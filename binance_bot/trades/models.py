from django.contrib import admin
from django.db import models
from django.utils import timezone

from django.utils.translation import gettext_lazy as _


class Pair(models.Model):
    name = models.CharField(_("Pair Name"), max_length=50, unique=True)
    round = models.PositiveIntegerField(_("Round Of Pair"))
    min_price = models.FloatField(_("Min Price"))
    max_price = models.FloatField(_("Max Price"))

    class Meta:
        verbose_name = "Pair"
        verbose_name_plural = "Pairs"

    def __str__(self):
        return f"{self.name}"


class TradingStep(models.Model):
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE, related_name="trading_steps")
    step = models.PositiveIntegerField(_("Step"))
    value = models.FloatField(_("Value"))
    active = models.BooleanField(_("Is Active"), default=False)

    class Meta:
        verbose_name = "Trading Step"
        verbose_name_plural = "Trading Steps"
        unique_together = ["pair", "step"]

    def __str__(self):
        return f"{self.pair.name} - {self.step}"

    @property
    def step_float(self):
        return round(self.step / 100, 2)

    @property
    def count_steps(self):
        min_price = self.pair.min_price
        count_steps = 0
        while min_price < self.pair.max_price:
            min_price *= (1 + self.step_float)
            count_steps += 1
        return count_steps

    def value_tokens_buy(self, price):
        return round(self.value / price, self.pair.round)

    def value_buy(self, price):
        return round(self.value_tokens_buy(price) * price, 6)


class Order(models.Model):
    step = models.ForeignKey(TradingStep, on_delete=models.CASCADE, related_name="orders")
    price_buy = models.FloatField(_("Price Buy"))
    value = models.FloatField(_("Token Value"))
    date_create_buy = models.DateTimeField(_("Date And Time of Create Buy Order"), default=timezone.now)
    date_buy = models.DateTimeField(_("Date And Time Buy"), blank=True, null=True)
    date_sell = models.DateTimeField(_("Date And Time Sell"), blank=True, null=True)
    order_buy = models.PositiveBigIntegerField(_("Buy Order Id"), blank=True, null=True)
    order_sell = models.PositiveBigIntegerField(_("Sell Order Id"), blank=True, null=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"{self.step}"

    @property
    def price_sell(self):
        return round(self.price_buy * (1 + self.step.step_float), 2)

    @property
    def value_buy(self):
        return round(self.value * self.price_buy, 6)

    @property
    def value_sell(self):
        return round(self.value * self.price_sell, 6)

    @property
    def fee_buy(self):
        return round(self.value_buy * 0.0007, 6)

    @property
    def fee_sell(self):
        return round(self.value_sell * 0.0007, 6)

    @property
    def fee(self):
        fee_buy = self.fee_buy if self.order_buy else 0
        fee_sell = self.fee_sell if self.order_sell else 0
        return fee_buy + fee_sell

    @admin.display(description="Value Buy")
    def _value_buy(self):
        return self.value_buy

    @admin.display(description="Value Sell")
    def _value_sell(self):
        return self.value_sell

    @admin.display(description="Price Sell")
    def _price_sell(self):
        return self.price_sell

    _value_buy.admin_order_field = "value"
    _value_sell.admin_order_field = "value"
    _price_sell.admin_order_field = "price_buy"


class Result(models.Model):
    name = models.CharField(_("Name"), max_length=50, unique=True)
    date_from = models.DateTimeField(_("Date From"))
    date_to = models.DateTimeField(_("Date To"))
    steps = models.ManyToManyField("trades.TradingStep", related_name="results", blank=True)

    class Meta:
        verbose_name = "Result"
        verbose_name_plural = "Results"

    def __str__(self):
        return f"{self.name} - {self.date_from} - {self.date_to}"

    @property
    def fee(self):
        fee = 0
        for step in self.steps.all():
            for order in step.orders.exclude(date_sell=None).filter(date_sell__lte=self.date_to,
                                                                    date_sell__gte=self.date_from):
                fee += order.fee
        return fee

    @property
    def income(self):
        income = 0
        for step in self.steps.all():
            for order in step.orders.exclude(date_sell=None).filter(date_sell__lte=self.date_to,
                                                                    date_sell__gte=self.date_from):
                income += (order.value_sell - order.value_buy)
        return income

    @property
    def profit(self):
        return self.income - self.fee

    @admin.display(description="Fee")
    def _fee(self):
        return self.fee

    @admin.display(description="Income")
    def _income(self):
        return self.income

    @admin.display(description="Profit")
    def _profit(self):
        return self.profit
