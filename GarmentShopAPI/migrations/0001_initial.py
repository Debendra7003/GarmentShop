

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Company",
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
                ("company_name", models.CharField(max_length=255)),
                (
                    "gst",
                    models.CharField(
                        max_length=15,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid GST number",
                                regex="^\\d{2}[A-Z]{5}\\d{4}[A-Z]{1}[A-Z\\d]{1}[Z]{1}[A-Z\\d]{1}$",
                            )
                        ],
                    ),
                ),
                (
                    "pan",
                    models.CharField(
                        max_length=10,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid PAN number",
                                regex="^[A-Z]{5}\\d{4}[A-Z]{1}$",
                            )
                        ],
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        max_length=10,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid 10-digit phone number",
                                regex="^\\d{10}$",
                            )
                        ],
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254,
                        validators=[
                            django.core.validators.EmailValidator(
                                message="Enter a valid email address"
                            )
                        ],
                    ),
                ),
                ("address", models.TextField()),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="Design",
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
                ("design_name", models.CharField(max_length=100)),
                ("design_code", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField()),
                ("associated_items", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="FinancialYear",
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
                ("financial_year_name", models.CharField(max_length=100)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("status", models.BooleanField(default=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
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
                (
                    "item_code",
                    models.CharField(
                        blank=True, max_length=100, null=True, unique=True
                    ),
                ),
                (
                    "category_item",
                    models.CharField(default="default_category", max_length=255),
                ),
                (
                    "sub_category",
                    models.CharField(blank=True, max_length=70, null=True),
                ),
                ("hsn_code", models.CharField(max_length=50)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="Party",
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
                ("party_name", models.CharField(max_length=255, unique=True)),
                (
                    "party_type",
                    models.CharField(
                        choices=[
                            ("Vendor", "Vendor"),
                            ("Supplier", "Supplier"),
                            ("Customer", "Customer"),
                        ],
                        max_length=20,
                    ),
                ),
                ("phone", models.CharField(blank=True, max_length=15, null=True)),
                ("email", models.EmailField(blank=True, max_length=100, null=True)),
                ("address", models.TextField(blank=True, null=True)),
                (
                    "registration_number",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("gst_number", models.CharField(blank=True, max_length=100, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="SubCategory",
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
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
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("user_name", models.CharField(max_length=100, unique=True)),
                ("fullname", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=100, unique=True)),
                ("contact_number", models.CharField(max_length=20, unique=True)),
                ("role", models.CharField(max_length=100)),
                ("description", models.CharField(max_length=100, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_admin", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ItemSize",
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_code', models.CharField(max_length=20, unique=True)),
                ('category_name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField()),
                ('sub_category_name', models.ManyToManyField(to='GarmentShopAPI.subcategory')),
            ],
        ),
    ]
