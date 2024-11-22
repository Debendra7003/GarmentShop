from django.db import models

# Party Information Model
class PartyInformation(models.Model):
    invoicenumber = models.CharField(max_length=5, unique=True, editable=False)  # Unique invoice number
    partyname = models.CharField(max_length=255)
    mobilenumber = models.CharField(max_length=15)
    address = models.TextField()
    gstnumber = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        if not self.invoicenumber:
            last_invoice = PartyInformation.objects.last()
            next_number = int(last_invoice.invoicenumber) + 1 if last_invoice else 1
            self.invoicenumber = str(next_number).zfill(5)  # Zero-padded invoice number
        super().save(*args, **kwargs)

# Item Information Model
class ItemInformation(models.Model):
    party = models.ForeignKey(PartyInformation, related_name='items', on_delete=models.CASCADE)
    barcodenumber = models.CharField(max_length=255)
    itemname = models.CharField(max_length=255)
    unit = models.PositiveIntegerField()  # Number of units (e.g., 1, 2)
    unitprice = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit
    total_item_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Calculated

# Pricing and Tax Model
class PricingAndTax(models.Model):
    party = models.OneToOneField(PartyInformation, on_delete=models.CASCADE, related_name='pricing_tax')
    tax = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Sum of total_item_price
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # After tax and discount

# Payment and Narration Model
class PaymentAndNarration(models.Model):
    party = models.OneToOneField(PartyInformation, on_delete=models.CASCADE, related_name='payment_narration')
    payment_method1 = models.CharField(max_length=255)
    payment_method2 = models.CharField(max_length=255, null=True, blank=True)
    payment_amount1 = models.DecimalField(max_digits=10, decimal_places=2)
    payment_amount2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

