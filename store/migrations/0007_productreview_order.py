# Generated by Django 5.1 on 2024-10-24 11:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_order_invoice_order_paid'),
        ('store', '0006_remove_productreview_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='productreview',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='payment.order'),
        ),
    ]
