# Generated by Django 4.2.2 on 2023-06-10 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_payment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='total_amount',
            new_name='quantity',
        ),
    ]