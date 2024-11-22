from django.urls import path
from .views import PartyInformationView,CalculatePaymentMethod2AmountView,InvoiceDetailView

urlpatterns = [
    path('bulk-sale/', PartyInformationView.as_view(), name='bulk-sale'),
    path('calculate-payment-amount2/',CalculatePaymentMethod2AmountView.as_view(),name='payment-amount2'),
    path('invoice-detail/<str:invoicenumber>/', InvoiceDetailView.as_view(), name='invoice-detail'),
]
