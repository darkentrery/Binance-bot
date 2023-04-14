from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from binance_bot.trades.models import Pair, TradingStep, Order, Result


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


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "date_from",
        "date_to",
        "_income",
        "_fee",
        "_profit",
    ]
    fieldsets = (
        (None, {"fields": (
            "name",
            "date_from",
            "date_to",
            "steps",
            "_income",
            "_fee",
            "_profit",
        )}),
    )
    readonly_fields = [
        "_income",
        "_fee",
        "_profit",
    ]
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
