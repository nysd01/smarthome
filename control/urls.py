from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('toggle-light/', views.toggle_light, name='toggle_light'),
    path('open-door/', views.open_door, name='open_door'),
    path('register/', views.register, name='register'),
]
