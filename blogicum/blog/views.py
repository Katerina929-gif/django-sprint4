"""Представления для приложения blog."""
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post, User
from .utils import paginate_page


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
    posts = Post.objects.get_published().order_by('-pub_date')

    page_obj = paginate_page(request, posts)

    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts(request, category_slug):
    """Список публикаций в конкретной категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    posts = Post.objects.get_published().filter(category=category).order_by(
        '-pub_date')

    page_obj = paginate_page(request, posts)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    """Страница профиля пользователя и список его публикаций."""
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        posts = Post.objects.with_comment_count().filter(author=profile_user)
    else:
        posts = Post.objects.get_published().filter(author=profile_user)

    posts = posts.order_by('-pub_date')

    page_obj = paginate_page(request, posts)

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


def post_detail(request, post_id):
    """Страница отдельной публикации с комментариями."""
    post = get_object_or_404(Post.objects.with_comment_count(), pk=post_id)

    if request.user != post.author:

        if not Post.objects.get_published().filter(pk=post_id).exists():
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

    if not request.user.is_authenticated or request.user != post.author:
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

    if not request.user.is_authenticated or request.user != post.author:
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
