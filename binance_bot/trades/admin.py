from django.contrib import admin

from binance_bot.trades.models import Pair, TradingStep, Order


@admin.register(Pair)
class PairAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "round",
        "min_price",
        "max_price",
    ]


@admin.register(TradingStep)
class TradingStepAdmin(admin.ModelAdmin):
    list_display = [
        "pair",
        "step",
        "value",
        "active",
    ]


@admin.register(Order)
class TradingStepAdmin(admin.ModelAdmin):
    list_display = [
        "step",
        "price_buy",
        "_price_sell",
        "_value_buy",
        "_value_sell",
        "value",
        "date_create_buy",
        "date_buy",
        "date_sell",
    ]
