from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django import forms

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'post'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        help_texts = {
            'text': 'текст поста',
            'group': 'группа поста',
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if text == '':
            raise ValidationError('заполните текст поста')
        else:
            return text
