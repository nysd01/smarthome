from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('toggle-device/<int:device_id>/', views.toggle_device, name='toggle_device'),
    path('add-room/', views.add_room, name='add_room'),
    path('add-device/<int:room_id>/', views.add_device, name='add_device'),
    path('delete-device/<int:device_id>/', views.delete_device, name='delete_device'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'), 
    path('open-door/', views.open_door, name='open_door'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('room/<int:room_id>/update/', views.update_room, name='update_room'),
    path('toggle-all-leds/', views.toggle_all_leds, name='toggle_all_leds'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('set-brightness/<int:device_id>/', views.set_led_brightness, name='set_led_brightness'),

]
