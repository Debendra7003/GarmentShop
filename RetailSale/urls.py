from django.urls import path
from . views import CreateOrderView,CalculateTotalPriceView,CalculatePaymentMethod2AmountView,RetrieveOrderByBillNumberView,SalesReportView,CustomerSummaryView,ItemPreviewAPIView
from .views import DailySalesView, MonthlySalesView, YearlySalesView,GetOrderDetailsView,ItemStockSummaryView,SalesTaxView,SaleDiscountSummaryView,GetCustomerDetailsView
urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('create-order/', GetOrderDetailsView.as_view(), name='retrive all order details'),
    path('calculate-total-price/',CalculateTotalPriceView.as_view(),name='total-price'),
    path('calculate-payment-amount2/',CalculatePaymentMethod2AmountView.as_view(),name='payment-amount2'),
    path('orders/<str:bill_number>/', RetrieveOrderByBillNumberView.as_view(), name='retrieve-order-by-bill-number'),
    path('phone/',GetCustomerDetailsView.as_view(),name='retrive customer name and address by passing number'),
    path('item-preview/', ItemPreviewAPIView.as_view(), name='item-preview-api'),
    path('sales-report/', SalesReportView.as_view(), name='sales-report'),
    path('customer-report/', CustomerSummaryView.as_view(), name='customer-report'),

    path('dailysales/', DailySalesView.as_view(), name='daily-sales'),
    path('monthlysales/', MonthlySalesView.as_view(), name='monthly-sales'),
    path('yearlysales/', YearlySalesView.as_view(), name='yearly-sales'),
    path('item-stock-summary/', ItemStockSummaryView.as_view(), name='item-stock-summary'),
    path('saletax-report/', SalesTaxView.as_view(), name='sales-tax'),
    path('salediscount-summary/', SaleDiscountSummaryView.as_view(), name='salediscount_summary'),

]