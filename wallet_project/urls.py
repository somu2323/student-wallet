from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from wallet import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('wallet/', include('wallet.urls')),
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='wallet/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('transfer/', views.transfer_money, name='transfer_money'),
    path('history/', views.transaction_history, name='transaction_history'),
]
