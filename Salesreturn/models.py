from django.db import models

class Bill(models.Model):
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"

class Return(models.Model):
    return_id = models.CharField(max_length=5, unique=True, editable=False)  # Serial format (00001, 00002, etc.)
    bill_number = models.OneToOneField(Bill, on_delete=models.CASCADE, related_name="return_record")

    def save(self, *args, **kwargs):
        if not self.return_id:
            # Generate return_id serially
            last_return = Return.objects.order_by("-id").first()
            if last_return:
                new_id = int(last_return.return_id) + 1
            else:
                new_id = 1
            self.return_id = f"{new_id:05}"  # Format as 5-digit string
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Return ID: {self.return_id}"

class Item(models.Model):
    return_record = models.ForeignKey(Return, on_delete=models.CASCADE, related_name="items")
    barcode = models.CharField(max_length=50)
    category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    item_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.item_name} ({self.barcode})"
