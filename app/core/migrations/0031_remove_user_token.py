# Generated by Django 4.2.5 on 2023-09-28 06:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_discountcoupon_used'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='token',
        ),
    ]
