from django import forms
from .models import Task, Comment


class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        input_formats=["%d.%m.%Y", "%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control"
            }
        ),
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "due_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

class TaskFilterForm(forms.Form):
    STATUS_CHOICES = [('','всі'), ('todo', 'виконати'), ('in_progress', 'в процесі'), ('finish', 'виконана')]
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label="status")
    def __init__(self, *args, **kwargs):
        super(TaskFilterForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class':'form-control'})

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'media']
        widgets = {'media': forms.FileInput()}