# barcode_app/models.py
from django.db import models

class BarcodeItem(models.Model):
    item_name = models.CharField(max_length=255)
    description = models.TextField()
    size = models.CharField(max_length=50)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    # barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True)

    def __str__(self):
        return self.item_name

