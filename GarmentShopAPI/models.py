from django.db import models

# Create your models here.
# models.py

from django.db import models
from django.core.validators import RegexValidator, EmailValidator
#Company Creation
class Company(models.Model):
    company_name = models.CharField(max_length=255)
    gst = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$', message="Enter a valid GST number")]
    )
    pan = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^[A-Z]{5}\d{4}[A-Z]{1}$', message="Enter a valid PAN number")]
    )
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Enter a valid 10-digit phone number")]
    )
    email = models.EmailField(
        validators=[EmailValidator(message="Enter a valid email address")]
    )
    address = models.TextField()

    def __str__(self):
        return self.company_name

#Catagory Creation

class Category(models.Model):
    category_name = models.CharField(max_length=255, unique=True)
    category_code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.category_name
    
    