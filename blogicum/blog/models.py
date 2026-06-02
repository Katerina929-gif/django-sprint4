"""Описания моделей для приложения blog."""
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.utils import timezone

from constants import MAX_LENGTH_TITLE

User = get_user_model()


class PublishedModel(models.Model):
    """Абстрактная модель. Добавляет флаг публикации и дату создания."""

    pk: int
    id: int

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        """Мета-параметры абстрактной модели."""

        abstract = True


class BaseModel(models.Model):
    """Абстрактная модель для повторяющихся полей."""

    pk: int
    id: int

    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Мета-параметры базовой модели."""

        abstract = True


class Category(PublishedModel):
    """Модель тематической категории."""

    title = models.CharField('Заголовок', max_length=MAX_LENGTH_TITLE)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; разрешены '
            'символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta(PublishedModel.Meta):
        """Мета-параметры модели категории."""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(PublishedModel):
    """Модель для хранения географических меток."""

    name = models.CharField('Название места', max_length=MAX_LENGTH_TITLE)

    class Meta(PublishedModel.Meta):
        """Мета-параметры модели местоположения."""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class PostManager(models.Manager):
    """Менеджер для управления выборками публикаций."""

    def with_comment_count(self):
        """Возвращает queryset постов с посчитанным колич. комментариев."""
        return self.annotate(comment_count=Count('comments'))

    def get_published(self):
        """Возвращает только опубликованные посты с подсчетом комментариев."""
        return self.with_comment_count().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )


class Post(PublishedModel):
    """Модель для хранения публикаций блога."""

    comments: 'models.BaseManager[Comment]'

    title = models.CharField('Заголовок', max_length=MAX_LENGTH_TITLE)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Фото',
        upload_to='posts/',
        blank=True
    )
    objects: PostManager = PostManager()

    class Meta:
        """Meta-параметры модели публикации."""

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date',)


class Comment(models.Model):
    """Модель для комментариев к публикациям."""

    pk: int
    id: int
    post_id: int

    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация'
    )
    created_at = models.DateTimeField('Дата и время', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )

    class Meta:
        """Мета-параметры модели комментария."""

        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
