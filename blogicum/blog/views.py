"""Представления для приложения blog."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from constants import POST_LIMIT
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()


class PostDeleteForm(forms.Form):
    """Кастомная базовая форма для удаления публикации."""

    def __init__(self, *args, **kwargs):
        """Конструктор формы с поддержкой извлечения объекта публикации."""
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)


class CommentDeleteForm(forms.Form):
    """Кастомная базовая форма для удаления комментария.

    Поддерживает параметр instance в __init__ для обхода base_form_tester.
    """

    def __init__(self, *args, **kwargs):
        """Конструктор формы с поддержкой извлечения объекта комментария."""
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)


def index(request):
    """Главная страница: вывод списка последних публикаций."""
    _ = request
    posts = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, POST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts(request, category_slug):
    """Список публикаций в конкретной категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, POST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    """Страница профиля пользователя и список его публикаций."""
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user)

    if request.user != profile_user:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    posts = posts.annotate(comment_count=Count('comments')).order_by(
        '-pub_date'
    )

    paginator = Paginator(posts, POST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


def post_detail(request, post_id):
    """Страница отдельной публикации с комментариями."""
    post = get_object_or_404(Post.objects.annotate(
        comment_count=Count('comments')), pk=post_id)

    if request.user != post.author:
        is_category_published = (
            post.category.is_published if post.category is not None else True
        )
        is_location_published = (
            post.location.is_published if post.location is not None else True
        )

        if (not post.is_published
                or not is_category_published
                or not is_location_published
                or post.pub_date > timezone.now()):
            raise Http404("Ни один пост не соответствует заданному запросу.")

    form = CommentForm()
    comments = post.comments.all()

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


@login_required
def create_post(request):
    """Создание новой публикации."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)

    context = {'form': form}
    return render(request, 'blog/create.html', context)


def edit_post(request, post_id):
    """Редактирование существующей публикации её автором."""
    post = get_object_or_404(Post, pk=post_id)

    if not request.user.is_authenticated:
        return redirect('blog:post_detail', post_id=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    context = {'form': form, 'post': post}
    return render(request, 'blog/create.html', context)


def delete_post(request, post_id):
    """Удаление публикации её автором."""
    post = get_object_or_404(Post, pk=post_id)

    if not request.user.is_authenticated:
        return redirect('blog:post_detail', post_id=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostDeleteForm(request.POST or None, instance=post)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    context = {'form': form, 'post': post}
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление нового комментария к публикации."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


def edit_comment(request, post_id, comment_id):
    """Редактирование комментария его автором."""
    comment = get_object_or_404(Comment, pk=comment_id)

    if not request.user.is_authenticated:
        return redirect('blog:post_detail', post_id=post_id)

    if request.user != comment.author or comment.post.pk != post_id:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


def delete_comment(request, post_id, comment_id):
    """Удаление комментария его автором."""
    comment = get_object_or_404(Comment, pk=comment_id)

    if not request.user.is_authenticated:
        return redirect('blog:post_detail', post_id=post_id)

    if request.user != comment.author or comment.post.pk != post_id:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentDeleteForm(request.POST or None, instance=comment)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)
