# Generated by Django 5.0.4 on 2024-04-09 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='created_date',
            new_name='created_at',
        ),
    ]