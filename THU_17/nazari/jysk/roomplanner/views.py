import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
)

from .models import RoomProject, Furniture, FurniturePlacement

@csrf_exempt
@require_POST
def save_layout(request, pk):

    project = RoomProject.objects.get(
        pk=pk,
        owner=request.user
    )

    data = json.loads(request.body)

    FurniturePlacement.objects.filter(
        project=project
    ).delete()

    for item in data:

        furniture = Furniture.objects.get(
            id=item["furniture_id"]
        )

        FurniturePlacement.objects.create(
            project=project,
            furniture=furniture,
            x=item["x"],
            y=item["y"],
            rotation=item.get("rotation", 0)
        )

    return JsonResponse({"status": "ok"})

# Список проектов
class ProjectListView(LoginRequiredMixin, ListView):
    model = RoomProject
    template_name = "roomplanner/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return RoomProject.objects.filter(owner=self.request.user)


# Создание проекта
class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = RoomProject

    fields = [
        "title",
        "room_width",
        "room_height",
    ]

    template_name = "roomplanner/project_form.html"

    success_url = reverse_lazy("roomplanner:project-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# Открытие конструктора комнаты
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = RoomProject
    template_name = "roomplanner/planner.html"
    context_object_name = "project"

    def get_queryset(self):
        return RoomProject.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["furniture"] = Furniture.objects.all()
        return context


# Удаление проекта
class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = RoomProject
    template_name = "roomplanner/project_delete.html"
    success_url = reverse_lazy("roomplanner:project-list")

    def get_queryset(self):
        return RoomProject.objects.filter(owner=self.request.user)