from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('create_new/', views.create_new, name='home'),
    path('', views.bill_view, name='bill_view'),
    path('card/<int:id>/', views.card, name='card'),
    path('print-bills/<int:pk>', views.print_bills, name='print_bills'),
    path('denomination/', views.denomination_calculator, name='denomination_calculator'),
    path('add-payment/<int:pk>/', views.add_payment, name='add_payment'),
    path('merchant/<int:pk>/transactions/', views.transaction_history, name='transaction_history'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('emi-alerts/', views.emi_alerts, name='emi_alerts'),
    path('customer/<int:pk>/edit/', views.edit_customer, name='edit_customer'),
    path('customer/<int:pk>/delete/', views.delete_customer, name='delete_customer'),
    path('payment-receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
]   