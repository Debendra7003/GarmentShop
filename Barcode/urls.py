# barcode_app/urls.py
from django.urls import path
from .views import BarcodeGenerateAPIView

urlpatterns = [
    path('generate-barcode/', BarcodeGenerateAPIView.as_view(), name='generate-barcode'),
]
