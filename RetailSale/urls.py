from django.urls import path
from . views import CreateOrderView,CalculateTotalPriceView,CalculatePaymentMethod2AmountView,RetrieveOrderByBillNumberView,SalesReportView,CustomerSummaryView
from .views import DailySalesView, MonthlySalesView, YearlySalesView
urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('calculate-total-price/',CalculateTotalPriceView.as_view(),name='total-price'),
    path('calculate-payment-amount2/',CalculatePaymentMethod2AmountView.as_view(),name='payment-amount2'),
    path('orders/<str:bill_number>/', RetrieveOrderByBillNumberView.as_view(), name='retrieve-order-by-bill-number'),
    path('sales-report/', SalesReportView.as_view(), name='sales-report'),
    path('customer-report/', CustomerSummaryView.as_view(), name='customer-report'),

    path('dailysales/', DailySalesView.as_view(), name='daily-sales'),
    path('monthlysales/', MonthlySalesView.as_view(), name='monthly-sales'),
    path('yearlysales/', YearlySalesView.as_view(), name='yearly-sales'),
]