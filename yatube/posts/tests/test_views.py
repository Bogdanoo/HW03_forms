import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

name_users = ['TestUser1', 'TestUser2']
name_slugs = ['test_group', 'bag_slug']

name_reverses = {
    'index': reverse('posts:index'),
    'group': reverse('posts:group_list', kwargs={'slug': name_slugs[0]}),
    'profile': reverse('posts:profile', kwargs={'username': name_users[0]}),
    'create_post': reverse('posts:post_create'),
}


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=name_users[0])
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=name_slugs[0],
            description='Описание группы',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовые посты',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)
        cache.clear()

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.image, self.post.image)

    def test_forms_show_correct(self):
        """Проверка коректности формы."""
        context = {
            name_reverses['create_post'],
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        }
        for reverse_page in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.author_client.get(reverse_page)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField
                )
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField
                )
                self.assertIsInstance(
                    response.context['form'].fields['image'],
                    forms.fields.ImageField
                )

    def test_page_show_correct_context(self):
        """Каждые шаблоны сформированы с правильным контекстом."""
        response_list = [
            [name_reverses['index'], '', ''],
            [name_reverses['group'], 'group', self.group],
            [name_reverses['profile'], 'author', self.user]
        ]

        for url, _get, _val in response_list:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.check_post_info(response.context['page_obj'][0])
                if _get and _val:
                    self.assertEqual(response.context[_get], _val)

    def test_detail_page_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.check_post_info(response.context['post'])

    def test_cache_index_page(self):
        """Проверка работы кеша"""
        post = Post.objects.create(
            text='Пост под кеш',
            author=self.user
        )
        page_add = self.author_client.get(
            reverse('posts:index')).content
        post.delete()
        page_delete = self.author_client.get(
            reverse('posts:index')).content
        self.assertEqual(page_add, page_delete)
        cache.clear()
        page_cache_clear = self.author_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(page_add, page_cache_clear)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=name_users[0],
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=name_slugs[0],
            description='Описание группы',
        )
        for i in range(settings.PAGE_SIZE + 1):
            Post.objects.create(
                text=f'Тестовые посты #{i}',
                author=cls.user,
                group=cls.group
            )
