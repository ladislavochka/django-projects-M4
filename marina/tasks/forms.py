from django import forms
from .models import Task, Comment


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'status',
            'priority',
            'due_date'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })

        self.fields['due_date'].widget.attrs.update({
            'type': 'date'
        })


class TaskFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Пошук',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пошук задач...'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'всі')] + Task.STATUS_CHOICES,
        required=False,
        label='Статус',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    priority = forms.ChoiceField(
        choices=[('', 'всі')] + Task.PRIORITY_CHOICES,
        required=False,
        label='Пріоритет',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'media']

        widgets = {
            'media': forms.FileInput()
        }