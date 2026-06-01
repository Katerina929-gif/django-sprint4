"""Представления для статичных страниц и обработки ошибок приложения pages."""
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Отображение статичной страницы 'О проекте'."""

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Отображение статичной страницы 'Правила'."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Кастомный обработчик ошибки 404."""
    _ = exception
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Кастомный обработчик ошибки 500."""
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    """Кастомный обработчик ошибки 403 (Ошибка проверки токена CSRF)."""
    _ = reason
    return render(request, 'pages/403csrf.html', status=403)
