# Generated by Django 4.1.7 on 2023-03-24 01:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0004_remove_order_price_sell'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_create_buy',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date And Time of Create Buy Order'),
        ),
    ]
