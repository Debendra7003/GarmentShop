from django.db import models

class Order(models.Model):
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

    items = models.ManyToManyField('Item', related_name='order_items')  # Renamed 'items' to 'order_items'

    def calculate_grand_total(self):
        # Calculate grand total based on the items
        total_items_price = sum(item.total_item_price for item in self.items.all())
        return total_items_price

    def calculate_total_price(self):
        # Calculate total price after applying tax and discount
        return self.calculate_grand_total() + self.tax - self.discount


class Item(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)  # Renamed 'items' to 'order_items'
    barcode = models.CharField(max_length=100)
    item_name = models.CharField(max_length=255)
    unit = models.PositiveIntegerField()  # Quantity of the item
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_item_price(self):
        # Calculate total price for the item based on quantity and unit price
        return self.unit * self.unit_price
