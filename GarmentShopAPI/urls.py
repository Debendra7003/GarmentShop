# urls.py

from django.urls import path
from .views import CompanyViewSet, CategoryViewSet

urlpatterns = [
    path('api/companies/', CompanyViewSet.as_view(), name='company-list'),
    path('api/companies/<int:pk>/', CompanyViewSet.as_view(), name='company-detail'),

    path('api/categories/', CategoryViewSet.as_view(), name='category-list'),
    path('api/categories/<int:pk>/', CategoryViewSet.as_view(), name='category-detail'),
]
