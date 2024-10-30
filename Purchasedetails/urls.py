from django.urls import path
from .views import PurchaseEntryViewSet
urlpatterns = [
    path('purchase-entries/', PurchaseEntryViewSet.as_view()),  # List all and create new
    path('purchase-entries/<str:party_name>/', PurchaseEntryViewSet.as_view()),  # Retrieve, update, delete specific entry
    
]
