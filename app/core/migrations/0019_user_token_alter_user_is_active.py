# Generated by Django 4.2.5 on 2023-09-10 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_paymentproduct_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='token',
            field=models.CharField(default='none', max_length=36),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]