# Generated by Django 4.2.2 on 2023-06-10 14:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_cart_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('total_amount', models.IntegerField()),
                ('status', models.CharField(choices=[('Completed', 'Completed'), ('Pending', 'Pending (Default)'), ('Refunded', 'Refunded')], default='Pending', max_length=9)),
                ('transaction_id', models.CharField(default=None, max_length=25, null=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_payemnt', to='core.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_payment', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
