from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')  
        self.assertEqual(response.status_code, 200)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованного клиента
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем авторизованного пользователя
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем автора
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_slug_url_exists_at_desired_location(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_username_url_exists_at_desired_location(self):
        """Страница /profile/HasNoName/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/HasNoName/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_post_id_url_exists_at_desired_location(self):
        """Страница /posts/post_id/ доступна любому пользователю."""
        response = self.guest_client.get('/posts/post_id/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
