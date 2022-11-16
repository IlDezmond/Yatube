from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User


class FixturesTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=(
                'Lorem ipsum dolor sit amet, consectetur adipiscing '
                'elit, sed do eiusmod tempor incididunt ut labore et '
                'dolore magna aliqua.'
            ),
        )

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='User2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_author = Client()
        self.post_author.force_login(self.__class__.user)
