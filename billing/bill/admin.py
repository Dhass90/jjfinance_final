from django.contrib import admin,messages
from .models import Billtable,Paymenttable
import os
@admin.action(description="Delete selected customers and their images")
def delete_customers_and_images(modeladmin, request, queryset):
    count = 0
    for obj in queryset:
        # Delete customer image
        if obj.image and os.path.isfile(obj.image.path):
            os.remove(obj.image.path)
        # Delete ornament image
        if obj.ornament_image and os.path.isfile(obj.ornament_image.path):
            os.remove(obj.ornament_image.path)
        obj.delete()
        count += 1
    messages.success(request, f"Deleted {count} customer(s) and their images.")
@admin.register(Billtable)
class BilltableAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Billtable._meta.fields]
    readonly_fields = ('customer_id', 'loan_id')
    actions = [delete_customers_and_images]
# Register your models here.
@admin.register(Paymenttable)
class PaymenttableAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Paymenttable._meta.fields] + ['loan_id', 'customer_name']
    def loan_id(self, obj):
        return obj.billtable.loan_id
    loan_id.short_description = 'Loan ID'
    def customer_name(self, obj):
        return obj.billtable.fullname
    customer_name.short_description = 'Customer Name'
    
