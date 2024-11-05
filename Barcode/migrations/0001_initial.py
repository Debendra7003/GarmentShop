# Generated by Django 5.0.6 on 2024-11-04 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BarcodeItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('size', models.CharField(max_length=50)),
                ('mrp', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]