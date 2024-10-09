<<<<<<< HEAD
# urls.py

from django.urls import path
from .views import CompanyViewSet, CategoryViewSet

urlpatterns = [
    path('api/companies/', CompanyViewSet.as_view(), name='company-list'),
    path('api/companies/<int:pk>/', CompanyViewSet.as_view(), name='company-detail'),

    path('api/categories/', CategoryViewSet.as_view(), name='category-list'),
    path('api/categories/<int:pk>/', CategoryViewSet.as_view(), name='category-detail'),
]
=======

from django.urls import path,include
from .views import UserLoginView,CatagoryViewSet,CompanyViewSet,ItemViewSet,ItemCodeViewSet,TokenRefreshView,DesignViewSet


urlpatterns = [
    
    # path('register/',UserRegisterView.as_view(),name='register'),
    path('login/',UserLoginView.as_view(),name='login'),
    path('token/',TokenRefreshView.as_view(),name='getacceesstoken'),
    path('companies/', CompanyViewSet.as_view(), name='company-list'),
    path('companies/<int:pk>/', CompanyViewSet.as_view(), name='company-detail'),

    # Path for full category details
    path('catagories/', CatagoryViewSet.as_view(), name='category-list'),
    
    # Path for minimal category details
    path('catagories/minimal/', CatagoryViewSet.as_view(), name='category-minimal'),

    # Path for category detail by ID
    path('catagories/<int:pk>/', CatagoryViewSet.as_view(), name='category-detail'),

    # Item URLs
    path('items/', ItemViewSet.as_view(), name='item-list'),  # List items and create a new item
    path('items/<int:pk>/', ItemViewSet.as_view(), name='item-detail'),  # Retrieve, update, or delete an item by ID
    path('items/codes/', ItemCodeViewSet.as_view(), name='item-code-name-list'),  # New endpoint
    
    #Design URLs
    path('designs/', DesignViewSet.as_view()),  # List all designs
    path('designs/<int:pk>/', DesignViewSet.as_view()),  # Get, update, delete specific design
    
]
>>>>>>> 41f2a9330573d80436a6055c951abcd1418c0c58
