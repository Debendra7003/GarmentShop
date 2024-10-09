from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator, EmailValidator

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self,user_name, password=None,password2=None):
        """
        Creates and saves a User with the given user_name and password.
        """
        if not user_name:
            raise ValueError("Users must have an user_name")

        user = self.model(
            user_name=user_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,user_name, password=None):
        """
        Creates and saves a User with the given user_name and password.
        """
        user = self.create_user(
            user_name=user_name,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser):
    user_name = models.CharField(max_length=100,unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects = UserManager()
    USERNAME_FIELD = "user_name"

    def __str__(self):
        return self.user_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
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

class Catagory(models.Model):
    catagory_name = models.CharField(max_length=255, unique=True)
    catagory_code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.catagory_name
    
    

#Item Creation

class Item(models.Model):
    item_name = models.CharField(max_length=255)
    item_code = models.CharField(max_length=100, unique=True)
    catagory = models.ForeignKey(Catagory, on_delete=models.CASCADE)  # Assuming you have a Category model
    hsn_code = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.item_name
    
#Design Creation
class Design(models.Model):
    design_name = models.CharField(max_length=100)
    design_code = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    associated_items = models.ManyToManyField(Item, related_name='designs')

    def __str__(self):
        return self.design_name