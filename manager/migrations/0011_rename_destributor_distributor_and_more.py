# Generated by Django 5.0.4 on 2024-04-15 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0010_deliverycompany_order_buyer_platform_order_status_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Destributor',
            new_name='Distributor',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='destributor',
            new_name='distributor',
        ),
        migrations.AddField(
            model_name='deliverycompany',
            name='city',
            field=models.CharField(default='cali', max_length=300),
        ),
    ]
