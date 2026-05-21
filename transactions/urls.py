from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.transaction_create, name='transaction_create'),
]