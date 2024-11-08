# barcode_app/urls.py
from django.urls import path
from .views import BarcodeGenerateAPIView,GenerateBarcodeView

urlpatterns = [
    path('generate-barcode/', BarcodeGenerateAPIView.as_view(), name='generate-barcode'),
    path("code/", GenerateBarcodeView.as_view(), name="generate_barcode"),
]
