from django.db import models

class PurchaseEntry(models.Model):
    party_name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    item = models.CharField(max_length=255)
    voucher_number = models.CharField(max_length=50)  # Manually entered by user
    voucher_date = models.DateField()
    quantity = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Auto-calculated fields
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    # Automatically generated alphanumeric reference voucher number
    reference_voucher_number = models.CharField(max_length=20, unique=True, editable=False)

    def save(self, *args, **kwargs):
        # Calculate discount amount directly on the rate
        self.discount_amount = (self.discount_percentage / 100) * self.rate
        
        # Calculate taxable amount after applying the discount
        self.taxable_amount = self.rate - self.discount_amount
        
        # Calculate GST amount based on the taxable amount
        self.gst_amount = (self.gst_percentage / 100) * self.taxable_amount
        
        # Final purchase amount including GST
        self.purchase_amount = self.taxable_amount + self.gst_amount

        # Auto-generate the alphanumeric reference voucher number if it doesn't exist
        if not self.reference_voucher_number:
            self.reference_voucher_number = self.generate_alphanumeric_reference()

        super().save(*args, **kwargs)

    def generate_alphanumeric_reference(self):
        # Generate a unique alphanumeric reference voucher number
        prefix = "REF"
        last_entry = PurchaseEntry.objects.all().order_by('id').last()
        if last_entry:
            last_id = int(last_entry.reference_voucher_number[len(prefix):])  # Extract the numeric part
            new_id = last_id + 1
        else:
            new_id = 1

        # Create alphanumeric code with a fixed prefix and a serial number (e.g., REF001, REF002)
        return f"{prefix}{new_id:03d}"

    def __str__(self):
        return f"Purchase Entry {self.reference_voucher_number} - {self.party_name}"
