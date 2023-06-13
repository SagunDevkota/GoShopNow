# Generated by Django 4.2.1 on 2023-06-04 16:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('p_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('price', models.FloatField()),
                ('threshold', models.IntegerField()),
                ('stock', models.IntegerField()),
                ('rating', models.FloatField(validators=[django.core.validators.MinValueValidator(1.0, 'Minimum value muct be 1'), django.core.validators.MaxValueValidator(5.0, 'Maximum value must be 5')])),
            ],
        ),
    ]