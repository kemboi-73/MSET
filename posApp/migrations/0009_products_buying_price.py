# Generated by Django 5.0.7 on 2024-08-02 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posApp', '0008_alter_salesitems_sale_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='buying_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]