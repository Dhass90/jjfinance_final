from django.db import models
from datetime import timedelta,datetime
from django.utils import timezone
from decimal import Decimal

class Billtable(models.Model):
    customer_id = models.CharField(max_length=4, unique=True, blank=False)
    loan_id = models.CharField(max_length=10, unique=True, editable=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    fullname = models.CharField(max_length=15)
    email = models.EmailField(max_length=40,blank=True, null=True)
    phone1 = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15,blank=True, null=True)
    dateofbirth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    nominee_name = models.CharField(max_length=15)
    nominee_relation = models.CharField(max_length=15)
    nominee_phone = models.CharField(max_length=15)
    nominee_address = models.CharField(max_length=100)
    ornament_image = models.ImageField(upload_to='ornament_images/')
    others_details = models.CharField(max_length=100,blank=True, null=True)
    # Chain    
    chain_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    chain_weight = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)

    # Earing
    
    earing_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    earing_weight = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)

    # Ring
    ring_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    ring_weight = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)

    # Bracelet
    bracelet_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    bracelet_weight = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)

    # Bangle
    bangle_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    bangle_weight = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)

    # Necklace
    necklace_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    necklace_weight = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)

    # Others
   
    others_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    others_weight = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)
    ornament_weight = models.CharField(max_length=15)
    ornament_net_weight = models.CharField(max_length=15)
    initial_intrest = models.CharField(max_length=15)
    current_intrest = models.CharField(max_length=15, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    intrest_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)
    payed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), blank=True, null=True)
    duration = models.CharField(max_length=15)
    emi_due_date = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.loan_id:
            today = datetime.now().strftime('%y%m%d')  
            prefix = f"GL00{today}"
            # Count how many loans already created today
            today_count = Billtable.objects.filter(loan_id__startswith=prefix).count() + 1
            serial = f"{today_count:02d}"  # 2 digits
            self.loan_id = f"{prefix}{serial}"
        super().save(*args, **kwargs)

        if not self.current_intrest:
            self.current_intrest = self.initial_intrest
        if not self.total_amount:
            self.total_amount = self.amount
        if not self.payed_amount:
            self.payed_amount = Decimal('0.00')
        if not self.emi_due_date:
            self.emi_due_date = timezone.now() + timedelta(days=30)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"({self.created}, {self.loan_id}, {self.fullname}, {self.phone1}, {self.status})"

class Paymenttable(models.Model):
    billtable = models.ForeignKey(Billtable, on_delete=models.CASCADE, related_name='payments')
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=25)
    notes = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment for Loan ID: {self.billtable.loan_id} on {self.date}"