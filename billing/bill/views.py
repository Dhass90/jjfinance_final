from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Billtable, Paymenttable
from .forms import addbillform, paymentform
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from django.db.models import Q, Sum
from decimal import Decimal
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
import os


@login_required
def create_new(request):
    if request.method == 'POST':
        form = addbillform(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer Added successfully!")
            return redirect('bill_view')  
    else:
        form = addbillform()
    return render(request, 'create_new.html', {'form': form})

@login_required
def bill_view(request):
    query = request.GET.get('q')
    if query:
        bills = Billtable.objects.filter(
            Q(fullname__icontains=query) |
            Q(email__icontains=query) |
            Q(phone1__icontains=query) |
            Q(phone2__icontains=query)
        )
    else:
        bills = Billtable.objects.all()
    return render(request, 'bill_list.html', {'bill': bills, 'query': query})

@login_required
def card(request, id):
    client = get_object_or_404(Billtable, id=id)
    try:
        total = Decimal(client.total_amount)
    except:
        total = Decimal('0')
    try:
        paid = Decimal(client.payed_amount)
    except:
        paid = Decimal('0')
    remaining = total - paid
    return render(request, 'card.html', {'bill': client, 'remaining': remaining})

@login_required
def print_bills(request,pk):
    
    bill = get_object_or_404(Billtable, pk=pk)
    printed_time = timezone.now()
    return render(request, 'print_bills.html', {
        'bill': bill,
        'printed_time': printed_time,
    })

@login_required
def denomination_calculator(request):
    denominations = [2000, 500, 200, 100, 50, 10, 5, 2, 1]
    return render(request, 'denomination_calculator.html', {'denominations': denominations})

@login_required
def add_payment(request, pk):
    bill = get_object_or_404(Billtable, pk=pk)
    if request.method == 'POST' and 'add_interest' in request.POST:
        interest_to_add = Decimal(request.POST.get('interest_to_add', '0'))
        bill.intrest_amount=interest_to_add
        bill.total_amount += interest_to_add
        bill.save()
        messages.success(request, f"Interest amount {interest_to_add} added to remaining!")
        return redirect('add_payment', pk=bill.pk)
    if request.method == 'POST':
        if 'change_intrest' in request.POST:
            new_intrest = request.POST.get('new_intrest')
            if new_intrest:
                bill.current_intrest = new_intrest
                bill.save()
                messages.success(request, f"Interest rate changed to {new_intrest}!")
            return redirect('add_payment', pk=bill.pk)
    
    
    if request.method == 'POST':
        if 'status_update' in request.POST:
            new_status = request.POST.get('status') == 'True'
            bill.status = new_status
            bill.save()
            messages.success(request, "Status updated successfully!")
            return redirect('add_payment', pk=bill.pk)
        else:
            form = paymentform(request.POST)
            if form.is_valid():
                payment = form.save(commit=False)
                payment.billtable = bill
                payment.save()
                try:
                    payed = Decimal(bill.payed_amount)
                except:
                    payed = Decimal('0')
                try:
                    to_add = Decimal(payment.amount)
                except:
                    to_add = Decimal('0')
                bill.payed_amount = str(payed + to_add)
                
                # Extend EMI due date by 30 days from current due date
                bill.emi_due_date = bill.emi_due_date + timedelta(days=30)
                bill.save()
                messages.success(request, "Payment added successfully!")
                return redirect('payment_receipt', payment_id=payment.id)
    else:
        try:
            total = Decimal(bill.total_amount)
        except:
            total = Decimal('0')
        try:
            paid = Decimal(bill.payed_amount)
        except:
            paid = Decimal('0')
        remaining = total - paid
        form = paymentform()
    return render(request, 'addpayment.html', {'form': form, 'bill': bill, 'remaining': remaining})

@login_required
def transaction_history(request, pk):
    bill = get_object_or_404(Billtable, pk=pk)
    payments = bill.payments.all().order_by('-date')
    try:
        total = Decimal(bill.total_amount)
    except:
        total = Decimal('0')
    try:
        paid = Decimal(bill.payed_amount)
    except:
        paid = Decimal('0')
    remaining = total - paid
    return render(request, 'transaction_history.html', {
        'bill': bill,
        'payments': payments,
        'remaining': remaining,
    })
    
@login_required
def admin_dashboard(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    show = request.GET.get('show', 'payments')
    customers = []
    payments = []
    customer_count = 0
    payment_count = 0
    total_payment_amount = 0
    total_loaned_amount = 0
    if start_date and end_date:
        start = parse_date(start_date)
        end = parse_date(end_date)
        customers = Billtable.objects.filter(created__date__gte=start, created__date__lte=end).order_by('-created')
        payments = Paymenttable.objects.filter(date__date__gte=start, date__date__lte=end).order_by('-date')
        total_payment_amount = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_loaned_amount = customers.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        customer_count = customers.count()
        payment_count = payments.count()
    return render(request, 'dashboard.html', {
        'customers': customers,
        'payments': payments,
        'customer_count': customer_count,
        'payment_count': payment_count,
        'start_date': start_date,
        'end_date': end_date,
        'total_payment_amount': total_payment_amount,
        'total_loaned_amount': total_loaned_amount,
        'show': show
    })

@login_required
def emi_alerts(request):
    today = timezone.now()
    customers = Billtable.objects.filter(status=True)
    emi_list = []
    for c in customers:
        days_left = (c.emi_due_date - today).days
        status = ''
        if days_left <= 0:
            status = 'overdue'
        elif days_left <= 1:
            status = 'due_1'
        elif days_left <= 2:
            status = 'due_2'
        elif days_left <= 3:
            status = 'due_3'
        elif days_left <= 7:
            status = 'due_7'
        else:
            status = 'clear'
        emi_list.append({
            'customer': c,
            'emi_due_date': c.emi_due_date,
            'status': status,
        })
    return render(request, 'emi_alerts.html', {'emi_list': emi_list})
####newww

    
@login_required
def edit_customer(request, pk):
    customer = get_object_or_404(Billtable, pk=pk)
    if request.method == 'POST':
        form = addbillform(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer details updated successfully!")
            return redirect('bill_view')
    else:
        form = addbillform(instance=customer)
    return render(request, 'edit_customer.html', {'form': form, 'customer': customer})



@login_required
def delete_customer(request, pk):
    customer = get_object_or_404(Billtable, pk=pk)
    if request.method == 'POST':
        if customer.image and os.path.isfile(customer.image.path):
            os.remove(customer.image.path)
        if customer.ornament_image and os.path.isfile(customer.ornament_image.path):
            os.remove(customer.ornament_image.path)
        customer.delete()  # This will call your model's delete() and remove images
        messages.success(request, "Customer and images deleted successfully!")
        return redirect('bill_view')
    


@login_required
def payment_receipt(request, payment_id):
    payment = get_object_or_404(Paymenttable, id=payment_id)
    bill = payment.billtable
    printed_time = timezone.now()
    return render(request, 'payment_receipt.html', {
        'payment': payment,
        'bill': bill,
        'user': request.user,
        'printed_time': printed_time,
    })
    
