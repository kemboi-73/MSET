# Generated by Django 5.0.7 on 2024-08-05 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posApp', '0011_products_low_quantity_threshold_products_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
    ]
