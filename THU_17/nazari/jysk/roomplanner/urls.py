from django.urls import path
from . import views

app_name = "roomplanner"

urlpatterns = [

    path("", views.ProjectListView.as_view(), name="project-list"),

    path(
        "create/",
        views.ProjectCreateView.as_view(),
        name="project-create",
    ),

    path(
        "<int:pk>/",
        views.ProjectDetailView.as_view(),
        name="project-detail",
    ),

    path(
        "<int:pk>/delete/",
        views.ProjectDeleteView.as_view(),
        name="project-delete",
    ),
    path(
        "<int:pk>/save/",
        views.save_layout,
        name="save-layout"
    ),
]
