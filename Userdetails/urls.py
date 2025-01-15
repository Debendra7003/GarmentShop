from django.urls import path
from .views import RoleBasedUserCreateView,RoleBasedUserDetailView

urlpatterns = [
    path('role-based-user/', RoleBasedUserCreateView.as_view(), name='role_based_user_create'),
    path('moduledetails/<str:username>/', RoleBasedUserDetailView.as_view(), name='role-based-user-detail'),

]
