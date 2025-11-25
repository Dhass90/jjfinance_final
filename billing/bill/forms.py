from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Billtable,Paymenttable

class addbillform(forms.ModelForm):
    class Meta:
        model = Billtable
        fields = [
            'customer_id',
            'fullname',
            'email',
            'phone1',
            'phone2',
            'dateofbirth',
            'address',
            'image',
            'nominee_name',
            'nominee_address',
            'nominee_relation',
            'nominee_phone',
            'ornament_image',
            'chain_count',
            'chain_weight',
            'earing_count',
            'earing_weight',
            'ring_count',
            'ring_weight',
            'bracelet_count',
            'bracelet_weight',
            'bangle_count',
            'bangle_weight',
            'necklace_count',
            'necklace_weight',
            'others_details',
            'others_count',
            'others_weight',
            'ornament_weight',
            'ornament_net_weight',
            'initial_intrest',
            'amount',
            'duration',
        ]
        widgets = {
            'dateofbirth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'style': 'resize:vertical;'}),
            'nominee_address': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'style': 'resize:vertical;'}),
        }

    def clean_customer_id(self):
        customer_id = self.cleaned_data['customer_id']
        qs = Billtable.objects.filter(customer_id=customer_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This Customer ID already exists. Please enter a unique ID.")
        return customer_id

class paymentform(forms.ModelForm):
    class Meta:
        model = Paymenttable
        fields = '__all__'  
        exclude = ['billtable'] 
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)     
