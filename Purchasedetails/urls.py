from django.urls import path
from .views import PurchaseEntryViewSet,PurchaseDetailsViewSet
urlpatterns = [
    path('purchase-details/', PurchaseDetailsViewSet.as_view()),  # List all 
    path('purchase-entry/', PurchaseEntryViewSet.as_view()),  #  create new
    path('purchase-entries/<str:party_name>/', PurchaseEntryViewSet.as_view()),  # Retrieve, update, delete specific entry
    
]
