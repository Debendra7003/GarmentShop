from django.urls import path
from .views import PurchaseEntryViewSet,PurchaseDetailsViewSet
urlpatterns = [
    path('purchase-details/', PurchaseDetailsViewSet.as_view()),  # List all data for report by date range
    path('purchase-entry/', PurchaseEntryViewSet.as_view()),  #  create new and list retrive
    path('purchase-entries/<str:party_name>/', PurchaseEntryViewSet.as_view()),  # Retrieve, update, delete specific entry
    
]
