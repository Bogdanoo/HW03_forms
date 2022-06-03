from django import forms
from django.core.exceptions import ValidationError

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': 'текст поста',
            'group': 'группа поста',
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if text == '':
            raise ValidationError('заполните текст поста')
        else:
            return text
