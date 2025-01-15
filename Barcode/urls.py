# barcode_app/urls.py
from django.urls import path
from .views import GenerateBarcodeView,GetBarcodeDetailsView,BarcodeFetchView

urlpatterns = [
    #path('generate-barcode/', BarcodeGenerateAPIView.as_view(), name='generate-barcode'),
    path("code/", GenerateBarcodeView.as_view(), name="generate_barcode"),
    path('get-barcode-details/<str:barcode>/', GetBarcodeDetailsView.as_view(), name='get-barcode-details'),
    path('barcode-fetch/', BarcodeFetchView.as_view(), name='barcode-fetch'),
]
