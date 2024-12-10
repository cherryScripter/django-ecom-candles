from django.core.management.base import BaseCommand
from .models import Product
from django.conf import settings


class Command(BaseCommand):
    help = 'Update product image URLs'

    def handle(self, *args, **kwargs):
        # List of product ids and image names for demonstration
        products = [
            (1, 'seasons_1.jpg'),
            (2, 'meadow_2.jpg'),
            (3, 'amberset_3.jpg'),
            (4, 'marzepan_4.jpg'),
            (5, 'homeset_5.jpg'),
            (6, 'forestset_6.jpg'),
            (7, 'vanillaplatform_7.jpg'),
            (8, 'cedre_8.jpg'),
            (9, 'natureplatform_9.jpg'),
            (10, 'eveningsoy_10.jpg'),
            (11, 'whiteset_11.jpg'),
            (12, 'calmsoy_12.jpg'),
        ]

        for product_id, image_name in products:
            image_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/product_images/{image_name}'
            product = Product.objects.get(id=product_id)
            product.image_url = image_url
            product.save()

            self.stdout.write(self.style.SUCCESS(f'Updated Product ID {product_id} image URL to: {image_url}'))
