# Generated by Django 4.2.3 on 2023-07-17 04:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_productimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='p_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_id_image', to='core.product'),
        ),
    ]
