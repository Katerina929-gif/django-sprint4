"""Настройки панели администратора для приложения blog."""
from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели категорий."""

    list_display = (
        'title',
        'slug',
        'is_published',
        'created_at',
    )

    list_editable = ('is_published',)

    search_fields = ('title', 'description')

    list_filter = ('is_published',)

    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели местоположений."""

    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настройка панели администратора для публикаций блога."""

    list_display = (
        'title',
        'pub_date',
        'author',
        'category',
        'location',
        'is_published',
    )

    list_editable = (
        'category',
        'is_published',
    )

    search_fields = (
        'title',
        'text',
        'author__username',
        'category__title'
    )

    list_filter = (
        'is_published',
        'category',
        'author',
        'pub_date',
    )
