from django.urls import path
from chat import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.chats_list, name='chats'),
    path('another_profile/<str:username>/', views.another_user_profile_view, name='profile-another'),
    path('another/<int:pk>/', views.another_profile, name='another-profile-view'),
    path('join/', views.join, name='join'),
    path('<str:room_name>/<str:username>/', views.room, name='room'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
]