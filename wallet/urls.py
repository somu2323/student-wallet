from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('support/', views.support, name='support'),
    path('settings/', views.settings, name='settings'),
]