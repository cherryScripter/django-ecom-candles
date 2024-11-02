# Generated by Django 5.1 on 2024-10-23 12:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_order_invoice_order_paid'),
        ('store', '0004_remove_order_full_name_remove_order_invoice_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productreview',
            name='order',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='payment.order'),
            preserve_default=False,
        ),
    ]
