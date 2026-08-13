from django.urls import path
from .views import IndexView

app_name = "tasks"

urlpatterns = [
    path("", IndexView.as_view(), name="task-list"),
]