from django.urls import path
from . import views


app_name = 'tasks'


urlpatterns = [

    path(
        '',
        views.TaskListView.as_view(),
        name='task-list'
    ),

    path(
        'task/create/',
        views.TaskCreateView.as_view(),
        name='task-create'
    ),

    path(
        'task/<int:pk>/',
        views.TaskDetailView.as_view(),
        name='task-detail'
    ),

    path(
        'task/<int:pk>/update/',
        views.TaskUpdateView.as_view(),
        name='task-update'
    ),

    path(
        'task/<int:pk>/delete/',
        views.TaskDeleteView.as_view(),
        name='task-delete'
    ),

    path(
        'task/<int:pk>/complete/',
        views.TaskCompleteView.as_view(),
        name='task-complete'
    ),

    path(
        'task/<int:pk>/favorite/',
        views.TaskFavoriteToggle.as_view(),
        name='task-favorite'
    ),

    path(
        'comment/<int:pk>/edit/',
        views.CommentUpdateView.as_view(),
        name='comment-update'
    ),

    path(
        'comment/<int:pk>/delete/',
        views.CommentDeleteView.as_view(),
        name='comment-delete'
    ),

    path(
        'comment/<int:pk>/like/',
        views.CommentLikeToggle.as_view(),
        name='comment-like'
    ),

    path(
        'login/',
        views.CustomLoginView.as_view(),
        name='login'
    ),

    path(
        'logout/',
        views.CustomLogoutView.as_view(),
        name='logout'
    ),

    path(
        'register/',
        views.RegisterView.as_view(),
        name='register'
    ),
]