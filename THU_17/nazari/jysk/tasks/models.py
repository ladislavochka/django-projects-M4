#tasks\models.py
from tkinter.constants import CASCADE

from django.db import models
from django.contrib.auth.models import User
from django.db.models import ForeignKey
from django.urls import reverse
# Create your models here.
class Task(models.Model):
    STATUS_CHOICES = [('todo', 'виконати'), ('in_progress', 'в процесі'), ('finish', 'виконана')]
    PRIORITY_CHOICES = [('low', 'низький'), ('average','середній'), ('high', 'високий')]
    title = models.CharField(max_length=256)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='low')
    due_date = models.DateField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('tasks:task-detail', kwargs={'pk': self.pk})

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to='comments_media/', blank=True, null=True)
    def __str__(self):
        return self.text

class Like(models.Model):
    comment = ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = ForeignKey(User, on_delete=models.CASCADE, related_name='liked_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('comment', 'user')



