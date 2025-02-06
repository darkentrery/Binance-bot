import asyncio

from django.contrib import admin
from django.db import models
from django.db.models import QuerySet
from django.forms import CheckboxSelectMultiple

from binance_bot.trades.models import Pair, TradingStep, Order, Result, Range
from scripts.trades import set_sell_orders


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
    actions = ["set_sell_orders", "activate", "inactivate"]

    @admin.action(description="Set exists sell orders")
    def set_sell_orders(self, request, queryset):
        asyncio.run(set_sell_orders())

    @admin.action(description="Activate trading steps")
    def activate(self, request, queryset: QuerySet):
        queryset.update(active=True)

    @admin.action(description="Inactivate trading steps")
    def inactivate(self, request, queryset: QuerySet):
        queryset.update(active=False)


@admin.register(Range)
class RangeAdmin(admin.ModelAdmin):
    list_display = [
        "pair",
        "min_value",
        "max_value",
        "active",
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
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
    list_filter = ["step__pair", "step__step"]


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
