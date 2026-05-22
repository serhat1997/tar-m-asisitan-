from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ekstre/', views.statement, name='statement'),
    path('odemeler/', views.payments, name='payments'),
    path('odemeler/ekle/', views.payment_create, name='payment_create'),
]