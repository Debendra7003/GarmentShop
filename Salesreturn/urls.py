from django.urls import path
from .views import ReturnCreateView

urlpatterns = [
    # Endpoint for creating a return
    path("salesreturn/", ReturnCreateView.as_view(), name="create-return"),
]
