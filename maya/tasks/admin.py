from django.contrib import admin
from .models import Task, Comment, Like


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "creator",
        "status",
        "priority",
        "due_date",
    )

    list_filter = (
        "status",
        "priority",
    )

    search_fields = (
        "title",
        "description",
        "creator__username",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "task",
        "created_at",
    )

    search_fields = (
        "text",
        "author__username",
    )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "comment",
        "created_at",
    )