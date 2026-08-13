from django.db import models
from django.contrib.auth.models import User


class Furniture(models.Model):
    CATEGORY = [
        ("bed", "Кровать"),
        ("sofa", "Диван"),
        ("chair", "Стул"),
        ("table", "Стол"),
        ("wardrobe", "Шкаф"),
        ("lamp", "Лампа"),
    ]

    name = models.CharField(max_length=150)

    category = models.CharField(
        max_length=30,
        choices=CATEGORY
    )

    width = models.FloatField(help_text="см")

    height = models.FloatField(help_text="см")

    depth = models.FloatField(help_text="см")

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to="furniture/"
    )

    def __str__(self):
        return self.name

class RoomProject(models.Model):

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=100
    )

    room_width = models.FloatField()

    room_height = models.FloatField()

    created = models.DateTimeField(
        auto_now_add=True
    )

    updated = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title

class FurniturePlacement(models.Model):
    project = models.ForeignKey(
        RoomProject,
        on_delete=models.CASCADE,
        related_name="placements"
    )

    furniture = models.ForeignKey(
        Furniture,
        on_delete=models.CASCADE
    )

    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)

    rotation = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.project.title} - {self.furniture.name}"