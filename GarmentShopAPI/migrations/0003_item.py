# Generated by Django 5.0.7 on 2024-10-08 06:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("GarmentShopAPI", "0002_category_company"),
    ]

    operations = [
        migrations.CreateModel(
            name="Item",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("item_name", models.CharField(max_length=255)),
                ("item_code", models.CharField(max_length=100, unique=True)),
                ("hsn_code", models.CharField(max_length=50)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("stock_quantity", models.IntegerField()),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="GarmentShopAPI.category",
                    ),
                ),
            ],
        ),
    ]
