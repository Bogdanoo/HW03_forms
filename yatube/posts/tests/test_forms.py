import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        picture = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='picture.gif',
            content=picture,
            content_type='image/gif'
        )
        cls.author = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Группа',
            description='Описание поста',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Текст поста',
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):

        # Создаем автора поста
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()

        form_data = {
            'group': self.group.pk,
            'text': self.post.text,
            'image': self.post.image,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={
                'username': PostCreateFormTests.post.author
            })
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text=self.post.text,
                image=self.post.image,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        tasks_count = Post.objects.count()
        form_data = {
            'group': self.group.pk,
            'text': 'Отредактированный текст',
            'image': self.post.image
        }
        response = self.author_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[self.post.id])
        )
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTests.group,
                text='Отредактированный текст',
                image=self.post.image
            ).exists()
        )
        self.assertEqual(Post.objects.count(), tasks_count)
