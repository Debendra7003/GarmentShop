 
from django.urls import path,include
from .views import UserLoginView,CategoryView,CompanyViewSet,ItemViewSet,ItemCodeViewSet,TokenRefreshView,DesignViewSet,PartyViewSet,TaxViewSet,UserRegisterView,FinancialYearViewSet,CategorySubCategoryView,ItemReportViewSet,ItemCreateOrUpdateView


urlpatterns = [
    
    path('register/',UserRegisterView.as_view(),name='register'),
    path('userdetails/',UserRegisterView.as_view(),name='register'),
    path('userdetails/<str:user_name>/',UserRegisterView.as_view(),name='user details'),
    path('login/',UserLoginView.as_view(),name='login'),
    
    path('token/',TokenRefreshView.as_view(),name='getacceesstoken'),
    path('companies/', CompanyViewSet.as_view(), name='company-list'),
    path('companies/<str:gst>/', CompanyViewSet.as_view(), name='company-detail'),

    # Path for full category details
    path('categories/', CategoryView.as_view(), name='category-list'),
    path('categories/<str:category_name>/', CategoryView.as_view(), name='category-delete'),
    
    # Path for Sub Category category details
    path('subcategories/<str:category_name>/', CategorySubCategoryView.as_view(), name='get-subcategory-by-category'),

    # Path for category detail by ID
    path('categories/<str:category_code>/', CategoryView.as_view(), name='category-detail'),

    # Item URLs
    path('items/', ItemViewSet.as_view(), name='item-list'),  # List items and create a new item
    path('items-post/', ItemCreateOrUpdateView.as_view(), name='item-list'),  # List items and create a new item
    path('items/<str:item_code>/', ItemViewSet.as_view(), name='item-detail'),  # Retrieve, update, or delete an item by ID
    path('items/codes/', ItemCodeViewSet.as_view(), name='item-code-name-list'),  # New endpoint
    path('item-report/',ItemReportViewSet.as_view(),name='item-report'),
    
    #Design URLs
    path('designs/', DesignViewSet.as_view()),  # List all designs
    path('designs/<str:design_code>/', DesignViewSet.as_view()),  # Get, update, delete specific design

    #Party URLs
    path('party/', PartyViewSet.as_view()),  # For creating and listing parties
    path('party/<str:party_name>/', PartyViewSet.as_view()),  # For retrieving, updating, and deleting a specific party
    
    #Tax URLs
    path('taxes/', TaxViewSet.as_view(), name='tax-list'),
    path('taxes/<int:pk>/', TaxViewSet.as_view(), name='tax-detail'),

    #Financial Year URLs
    path('financial-years/', FinancialYearViewSet.as_view()),  # List and Create
    path('financial-years/<int:pk>/', FinancialYearViewSet.as_view()),  # Retrieve, Update, Delete
    
]