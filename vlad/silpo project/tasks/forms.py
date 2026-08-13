from django import forms

from .models import Comment, Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "priority", "due_date"]
        labels = {
            "title": "Назва",
            "description": "Опис",
            "status": "Статус",
            "priority": "Пріоритет",
            "due_date": "Дедлайн",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "title": "Наприклад: підготувати презентацію",
            "description": "Деталі задачі, очікуваний результат, важливі нотатки",
        }
        for name, field in self.fields.items():
            css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs.update({"class": css_class})
            if name in placeholders:
                field.widget.attrs.setdefault("placeholder", placeholders[name])


class TaskFilterForm(forms.Form):
    PRIORITY_CHOICES = [("", "Усі"), *Task.PRIORITY_CHOICES]
    DUE_CHOICES = [
        ("", "Будь-який"),
        ("overdue", "Прострочені"),
        ("today", "На сьогодні"),
        ("week", "7 днів"),
        ("no_due", "Без дати"),
    ]
    SORT_CHOICES = [
        ("priority", "Пріоритет"),
        ("due", "Дедлайн"),
        ("new", "Нові спочатку"),
        ("title", "Назва"),
    ]

    q = forms.CharField(
        required=False,
        label="Пошук",
        widget=forms.SearchInput(
            attrs={
                "class": "form-control",
                "placeholder": "Назва, опис або автор",
                "data-live-search": "true",
                "autocomplete": "off",
            }
        ),
    )
    status = forms.ChoiceField(
        choices=[("", "Усі"), *Task.STATUS_CHOICES],
        required=False,
        label="Статус",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        label="Пріоритет",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    due = forms.ChoiceField(
        choices=DUE_CHOICES,
        required=False,
        label="Дедлайн",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        label="Сортування",
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text", "media"]
        labels = {
            "text": "Коментар",
            "media": "Файл",
        }
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "placeholder": "Додайте короткий коментар"}),
            "media": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].widget.attrs.update({"class": "form-control"})
