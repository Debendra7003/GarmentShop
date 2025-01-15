from django.urls import path
from .views import ModuleListView,ModulePostView,ModuleDeleteView
urlpatterns = [
    path('modules/', ModuleListView.as_view(), name='module-list'),
    path('modules-post/', ModulePostView.as_view(), name='module-list'),
    path('modules/delete/<int:pk>/', ModuleDeleteView.as_view(), name='module-delete'), 

]