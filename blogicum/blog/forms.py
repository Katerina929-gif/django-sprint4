"""Формы для приложения blog."""
from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования публикаций."""

    class Meta:
        """Мета-параметры формы публикации."""

        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    """Форма для добавления и изменения комментариев."""

    class Meta:
        """Мета-параметры формы комментария."""

        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder':
                                          'Напишите комментарий...'}),
        }
