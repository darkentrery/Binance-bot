# Generated by Django 4.1.7 on 2023-03-23 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradingstep',
            name='active',
            field=models.BooleanField(default=False, verbose_name='Is Active'),
        ),
    ]
