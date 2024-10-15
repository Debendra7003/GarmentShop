# Generated by Django 5.0.7 on 2024-10-09 07:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("GarmentShopAPI", "0009_party_created_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tax",
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
                (
                    "tax_name",
                    models.CharField(
                        choices=[
                            ("CGST", "Central GST"),
                            ("SGST", "State GST"),
                            ("IGST", "Integrated GST"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "tax_percentage",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Enter the tax percentage (0-100%)",
                        max_digits=5,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
            ],
        ),
    ]