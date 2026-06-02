"""Вспомогательные утилиты для приложения blog."""
from django.core.paginator import Paginator

from constants import POST_LIMIT


def paginate_page(request, post_list, post_per_page=POST_LIMIT):
    """Разбивает список публикаций на страницы.

    Возвращает текущую страницу.
    """
    paginator = Paginator(post_list, post_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
