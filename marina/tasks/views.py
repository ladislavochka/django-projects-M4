from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    View,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from . import models
from .mixins import UserIsOwnerMixin
from .forms import TaskForm, TaskFilterForm, CommentForm


class TaskListView(LoginRequiredMixin, ListView):
    model = models.Task
    context_object_name = 'tasks'
    template_name = 'tasks/task_list.html'

    def get_queryset(self):
        queryset = models.Task.objects.filter(
            creator=self.request.user
        )

        search = self.request.GET.get(
            'search',
            ''
        ).strip()

        status = self.request.GET.get(
            'status',
            ''
        ).strip()

        priority = self.request.GET.get(
            'priority',
            ''
        ).strip()

        favorite = self.request.GET.get(
            'favorite',
            ''
        ).strip()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        if status:
            queryset = queryset.filter(
                status=status
            )

        if priority:
            queryset = queryset.filter(
                priority=priority
            )

        if favorite == '1':
            queryset = queryset.filter(
                is_favorite=True
            )

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = TaskFilterForm(
            self.request.GET or None
        )

        user_tasks = models.Task.objects.filter(
            creator=self.request.user
        )

        context['total_tasks'] = user_tasks.count()

        context['completed_tasks'] = user_tasks.filter(
            status='finish'
        ).count()

        context['in_progress_tasks'] = user_tasks.filter(
            status='in_progress'
        ).count()

        context['todo_tasks'] = user_tasks.filter(
            status='todo'
        ).count()

        context['high_priority_tasks'] = user_tasks.filter(
            priority='high'
        ).count()

        context['favorite_tasks'] = user_tasks.filter(
            is_favorite=True
        ).count()

        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = models.Task
    context_object_name = 'task'
    template_name = 'tasks/task_detail.html'

    def get_queryset(self):
        return models.Task.objects.filter(
            creator=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['comment_form'] = CommentForm()

        return context

    def post(self, request, *args, **kwargs):
        comment_form = CommentForm(
            request.POST,
            request.FILES
        )

        if comment_form.is_valid():
            comment = comment_form.save(
                commit=False
            )

            comment.author = request.user
            comment.task = self.get_object()

            comment.save()

            return redirect(
                'tasks:task-detail',
                pk=comment.task.pk
            )

        context = self.get_context_data()

        context['comment_form'] = comment_form

        return self.render_to_response(
            context
        )


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = models.Task
    template_name = 'tasks/task_form.html'
    form_class = TaskForm
    success_url = reverse_lazy(
        'tasks:task-list'
    )

    def form_valid(self, form):
        form.instance.creator = self.request.user

        return super().form_valid(form)


class TaskCompleteView(
    LoginRequiredMixin,
    UserIsOwnerMixin,
    View
):
    def post(self, request, *args, **kwargs):
        task = self.get_object()

        task.status = 'finish'

        task.save()

        return HttpResponseRedirect(
            reverse_lazy(
                'tasks:task-list'
            )
        )

    def get_object(self):
        task_id = self.kwargs.get('pk')

        return get_object_or_404(
            models.Task,
            pk=task_id
        )


class TaskFavoriteToggle(
    LoginRequiredMixin,
    UserIsOwnerMixin,
    View
):
    def post(self, request, *args, **kwargs):
        task = self.get_object()

        task.is_favorite = not task.is_favorite

        task.save()

        return redirect(
            'tasks:task-list'
        )

    def get_object(self):
        task_id = self.kwargs.get('pk')

        return get_object_or_404(
            models.Task,
            pk=task_id
        )


class TaskUpdateView(
    LoginRequiredMixin,
    UserIsOwnerMixin,
    UpdateView
):
    model = models.Task
    form_class = TaskForm
    template_name = 'tasks/task_update_form.html'
    success_url = reverse_lazy(
        'tasks:task-list'
    )


class TaskDeleteView(
    LoginRequiredMixin,
    UserIsOwnerMixin,
    DeleteView
):
    model = models.Task
    success_url = reverse_lazy(
        'tasks:task-list'
    )
    template_name = (
        'tasks/task_delete_confirmation.html'
    )


class CommentUpdateView(
    LoginRequiredMixin,
    UpdateView
):
    model = models.Comment
    fields = ['text']
    template_name = 'tasks/edit_comment.html'

    def form_valid(self, form):
        comment = self.get_object()

        if comment.author != self.request.user:
            raise PermissionDenied(
                'You have no permissions to edit this comment'
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'tasks:task-detail',
            kwargs={
                'pk': self.object.task.pk
            }
        )


class CommentDeleteView(
    LoginRequiredMixin,
    DeleteView
):
    model = models.Comment
    template_name = 'tasks/delete_comment.html'

    def get_queryset(self):
        return super().get_queryset().filter(
            author=self.request.user
        )

    def get_success_url(self):
        return reverse_lazy(
            'tasks:task-detail',
            kwargs={
                'pk': self.object.task.pk
            }
        )


class CommentLikeToggle(
    LoginRequiredMixin,
    View
):
    def post(self, request, *args, **kwargs):

        comment = get_object_or_404(
            models.Comment,
            pk=self.kwargs.get('pk')
        )

        like_qs = models.Like.objects.filter(
            comment=comment,
            user=request.user
        )

        if like_qs.exists():
            like_qs.delete()
        else:
            models.Like.objects.create(
                comment=comment,
                user=request.user
            )

        return redirect(
            'tasks:task-detail',
            pk=comment.task.pk
        )


class CustomLoginView(LoginView):
    template_name = 'tasks/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = 'tasks:login'


class RegisterView(CreateView):
    template_name = 'tasks/register.html'
    form_class = UserCreationForm

    def form_valid(self, form):
        user = form.save()

        login(
            self.request,
            user
        )

        return redirect(
            'tasks:task-list'
        )