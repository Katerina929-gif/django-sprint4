"""Представления для работы с пользователями в приложении users."""
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ProfileForm

User = get_user_model()


class SignUp(CreateView):
    """Регистрация нового пользователя."""

    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
    template_name = 'registration/registration_form.html'


@login_required
def edit_profile(request, username):
    """Редактирование профиля конкретного пользователя."""
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        raise PermissionDenied

    form = ProfileForm(request.POST or None, instance=profile_user)

    if form.is_valid():
        updated_user = form.save()
        update_session_auth_hash(request, updated_user)
        return redirect('blog:profile', username=updated_user.username)

    context = {'form': form}
    return render(request, 'users/edit_profile.html', context)
