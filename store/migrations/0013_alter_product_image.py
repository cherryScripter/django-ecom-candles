# Generated by Django 5.1 on 2024-12-08 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='default.jpeg', upload_to='uploads/product/'),
        ),
    ]
