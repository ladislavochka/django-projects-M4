import csv

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from . import models
from .forms import CommentForm, TaskFilterForm, TaskForm
from .mixins import UserIsOwnerMixin


def build_task_queryset(request):
    queryset = (
        models.Task.objects.select_related("creator")
        .annotate(
            comment_count=Count("comments"),
            priority_rank=Case(
                When(priority="high", then=Value(0)),
                When(priority="average", then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            ),
            status_rank=Case(
                When(status="todo", then=Value(0)),
                When(status="in_progress", then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            ),
            due_missing=Case(
                When(due_date__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
    )
    form = TaskFilterForm(request.GET or None)
    sort = "priority"

    if form.is_valid():
        query = form.cleaned_data.get("q", "").strip()
        status = form.cleaned_data.get("status", "")
        priority = form.cleaned_data.get("priority", "")
        due = form.cleaned_data.get("due", "")
        sort = form.cleaned_data.get("sort", "priority")
        today = timezone.localdate()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(creator__username__icontains=query)
            )
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if due == "overdue":
            queryset = queryset.filter(due_date__lt=today).exclude(status="finish")
        elif due == "today":
            queryset = queryset.filter(due_date=today)
        elif due == "week":
            queryset = queryset.filter(due_date__gte=today, due_date__lte=today + timezone.timedelta(days=7))
        elif due == "no_due":
            queryset = queryset.filter(due_date__isnull=True)

    ordering = {
        "priority": ("status_rank", "priority_rank", "due_missing", "due_date", "title"),
        "due": ("due_missing", "due_date", "priority_rank", "title"),
        "new": ("-id",),
        "title": ("title",),
    }
    return queryset.order_by(*ordering.get(sort, ordering["priority"])), form


class TaskListView(ListView):
    model = models.Task
    context_object_name = "tasks"
    template_name = "tasks/task_list.html"

    def get_filter_form(self):
        if not hasattr(self, "_filter_form"):
            self._task_queryset, self._filter_form = build_task_queryset(self.request)
        return self._filter_form

    def get_queryset(self):
        if not hasattr(self, "_task_queryset"):
            self._task_queryset, self._filter_form = build_task_queryset(self.request)
        return self._task_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_tasks = models.Task.objects.all()
        today = timezone.localdate()
        total_tasks = all_tasks.count()
        finished_tasks = all_tasks.filter(status="finish").count()
        context.update(
            {
                "form": self.get_filter_form(),
                "total_tasks": total_tasks,
                "todo_tasks": all_tasks.filter(status="todo").count(),
                "in_progress_tasks": all_tasks.filter(status="in_progress").count(),
                "finished_tasks": finished_tasks,
                "overdue_tasks": all_tasks.filter(due_date__lt=today).exclude(status="finish").count(),
                "completion_rate": round((finished_tasks / total_tasks) * 100) if total_tasks else 0,
            }
        )
        return context


class TaskExportView(View):
    def get(self, request, *args, **kwargs):
        tasks, _ = build_task_queryset(request)
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="smakoplan-tasks.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow(["Назва", "Опис", "Статус", "Пріоритет", "Дедлайн", "Автор", "Коментарів"])
        for task in tasks:
            writer.writerow(
                [
                    task.title,
                    task.description,
                    task.get_status_display(),
                    task.get_priority_display(),
                    task.due_date.isoformat() if task.due_date else "",
                    task.creator.username,
                    task.comment_count,
                ]
            )
        return response


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = models.Task
    context_object_name = "task"
    template_name = "tasks/task_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = kwargs.get("comment_form", CommentForm())
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.task = self.object
            comment.save()
            messages.success(request, "Коментар додано.")
            return redirect("tasks:task-detail", pk=comment.task.pk)
        return self.render_to_response(self.get_context_data(comment_form=comment_form))


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = models.Task
    template_name = "tasks/task_form.html"
    form_class = TaskForm
    success_url = reverse_lazy("tasks:task-list")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.success(self.request, "Задачу створено.")
        return super().form_valid(form)


class TaskCompleteView(LoginRequiredMixin, UserIsOwnerMixin, View):
    def post(self, request, *args, **kwargs):
        task = self.get_object()
        task.status = "finish"
        task.save(update_fields=["status"])
        messages.success(request, "Задачу позначено виконаною.")
        return HttpResponseRedirect(reverse_lazy("tasks:task-list"))

    def get_object(self):
        task_id = self.kwargs.get("pk")
        return get_object_or_404(models.Task, pk=task_id)


class TaskUpdateView(LoginRequiredMixin, UserIsOwnerMixin, UpdateView):
    model = models.Task
    form_class = TaskForm
    template_name = "tasks/task_update_form.html"
    success_url = reverse_lazy("tasks:task-list")

    def form_valid(self, form):
        messages.success(self.request, "Задачу оновлено.")
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, UserIsOwnerMixin, DeleteView):
    model = models.Task
    success_url = reverse_lazy("tasks:task-list")
    template_name = "tasks/task_delete_confirmation.html"

    def form_valid(self, form):
        messages.success(self.request, "Задачу видалено.")
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Comment
    fields = ["text"]
    template_name = "tasks/edit_comment.html"

    def form_valid(self, form):
        comment = self.get_object()
        if comment.author != self.request.user:
            raise PermissionDenied("У вас немає прав редагувати цей коментар.")
        messages.success(self.request, "Коментар оновлено.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:task-detail", kwargs={"pk": self.object.task.pk})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Comment
    template_name = "tasks/delete_comment.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Коментар видалено.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:task-detail", kwargs={"pk": self.object.task.pk})


class CommentLikeToggle(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(models.Comment, pk=self.kwargs.get("pk"))
        like_qs = models.Like.objects.filter(comment=comment, user=request.user)
        if like_qs.exists():
            like_qs.delete()
        else:
            models.Like.objects.create(comment=comment, user=request.user)
        return redirect("tasks:task-detail", pk=comment.task.pk)


class CustomLoginView(LoginView):
    template_name = "tasks/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = "tasks:login"


class RegisterView(CreateView):
    template_name = "tasks/register.html"
    form_class = UserCreationForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Акаунт створено.")
        return redirect("tasks:task-list")
