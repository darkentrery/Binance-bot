# Generated by Django 4.1.7 on 2023-03-23 06:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Pair Name')),
                ('round', models.PositiveIntegerField(verbose_name='Round Of Pair')),
                ('min_price', models.FloatField(verbose_name='Min Price')),
                ('max_price', models.FloatField(verbose_name='Max Price')),
            ],
            options={
                'verbose_name': 'Pair',
                'verbose_name_plural': 'Pairs',
            },
        ),
        migrations.CreateModel(
            name='TradingStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step', models.PositiveIntegerField(verbose_name='Step')),
                ('value', models.FloatField(verbose_name='Value')),
                ('pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trading_steps', to='trades.pair')),
            ],
            options={
                'verbose_name': 'Trading Step',
                'verbose_name_plural': 'Trading Steps',
            },
        ),
    ]
