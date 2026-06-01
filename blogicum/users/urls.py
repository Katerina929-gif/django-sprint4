"""Маршруты (URL-адреса) для работы с пользователями в приложении users."""
from django.urls import path

from . import views


urlpatterns = [
    path('registration/', views.SignUp.as_view(), name='registration'),
]
