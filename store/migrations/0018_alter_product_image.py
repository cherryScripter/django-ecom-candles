# Generated by Django 5.1 on 2024-12-10 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='/default.jpg', upload_to='uploads/product/'),
        ),
    ]
