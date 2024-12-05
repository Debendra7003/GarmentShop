from django.db import models
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
class Order(models.Model):
    bill_number = models.CharField(max_length=10, unique=True, blank=True)  # For the serial bill number
    fullname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_method1 = models.CharField(max_length=100,default='cash')
    payment_method2 = models.CharField(max_length=100,default='upi')
    narration = models.TextField(max_length=200,blank=True,null=True)
    payment_method1_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method2_amount = models.DecimalField(max_digits=10, decimal_places=2)
<<<<<<< HEAD
=======
    saletype = models.CharField(max_length=50, blank=True, null=True)  # New saletype field
>>>>>>> 4c6f027d975c0bde1f89337833085b2494dfbc7a
    items = models.ManyToManyField('Item', related_name='order_items')  # Renamed 'items' to 'order_items'

    def calculate_grand_total(self):
        # Calculate grand total based on the items
        total_items_price = sum(item.total_item_price for item in self.items.all())
        return total_items_price

    def calculate_total_price(self):
        # Calculate total price after applying tax and discount
        return self.calculate_grand_total() + self.tax - self.discount
    def save(self, *args, **kwargs):
        if not self.bill_number:
            try:
                # Get the last order by bill_number
                last_order = Order.objects.order_by('-bill_number').first()
                if last_order and last_order.bill_number:
                    # Increment the last bill number
                    self.bill_number = f"{int(last_order.bill_number) + 1:05d}"
                else:
                    # Start from '00001' if no orders exist
                    self.bill_number = "00001"
            except Order.DoesNotExist:
                # No orders exist yet
                self.bill_number = "00001"

        super().save(*args, **kwargs)

        
    
       
    
    def save(self, *args, **kwargs):
     if not self.bill_number:
        try:
            # Get the last order by bill_number
            last_order = Order.objects.order_by('-bill_number').first()
            if last_order and last_order.bill_number:
                # Increment the last bill number
                self.bill_number = f"{int(last_order.bill_number) + 1:05d}"
            else:
                # Start from '00001' if no orders exist
                self.bill_number = "00001"
        except Order.DoesNotExist:
            # No orders exist yet
            self.bill_number = "00001"

     super().save(*args, **kwargs)

    






class Item(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)  # Renamed 'items' to 'order_items'
    barcode = models.CharField(max_length=100)
    category = models.CharField(max_length=100,blank=True,null=True)  # Added category field
    sub_category = models.CharField(max_length=100, blank=True, null=True)  # Added sub-category field
    size = models.CharField(max_length=50, blank=True, null=True)  # Added size field
    item_name = models.CharField(max_length=255)
    unit = models.PositiveIntegerField()  # Quantity of the item
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_item_price(self):
        # Calculate total price for the item based on quantity and unit price
        return self.unit * self.unit_price
    def __str__(self):
        return f"{self.item_name} ({self.category}) - {self.unit} x {self.unit_price}"