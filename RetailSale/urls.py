from django.urls import path
from . views import CreateOrderView,CalculateTotalPriceView,CalculatePaymentMethod2AmountView

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('calculate-total-price/',CalculateTotalPriceView.as_view(),name='total-price'),
    path('calculate-payment-amount2/',CalculatePaymentMethod2AmountView.as_view(),name='payment-amount2')
]