# Generated by Django 4.2.5 on 2023-09-15 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_remove_category_parent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='tmp_id',
        ),
    ]
