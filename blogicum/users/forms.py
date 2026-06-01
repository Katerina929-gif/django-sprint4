"""Формы для работы с пользователями в приложении users."""
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileForm(forms.ModelForm):
    """Форма для редактирования данных профиля пользователя."""

    class Meta:
        """Мета-параметры формы профиля."""

        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
