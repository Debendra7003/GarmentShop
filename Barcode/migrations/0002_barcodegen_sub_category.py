# Generated by Django 5.0.7 on 2025-01-12 05:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Barcode", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="barcodegen",
            name="sub_category",
            field=models.CharField(default="na", max_length=100),
        ),
    ]
