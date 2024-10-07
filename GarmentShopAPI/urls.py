
from django.urls import path,include
from .views import UserLoginView


urlpatterns = [
    
    # path('register/',UserRegisterView.as_view(),name='register'),
    path('login/',UserLoginView.as_view(),name='login'),
    
]