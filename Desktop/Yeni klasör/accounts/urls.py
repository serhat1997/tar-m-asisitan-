from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('hakkimizda/', views.about_view, name='about'),
    path('blog/', views.blog_view, name='blog'),
    path('iletisim/', views.contact_view, name='contact'),
    path('kullanicilar/', views.user_list_view, name='user_list'),
    path('kullanicilar/<int:user_id>/askiya-al/', views.user_suspend_view, name='user_suspend'),
    path('kullanicilar/<int:user_id>/sil/', views.user_delete_admin_view, name='user_delete_admin'),
    path('hesabim/sil/', views.account_delete_view, name='account_delete'),
]
