import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User
from posts.views import POSTS_SHOWN_AMOUNT

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
print(settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostVeiwsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='User1')
        cls.user2 = User.objects.create_user(username='User2')
        cls.user3 = User.objects.create_user(username='User3')
        cls.group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug1',
            description='Тестовое описание1',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        for i in range(26):
            Post.objects.create(
                author=(cls.user1 if i % 2 == 0 else cls.user2),
                group=(cls.group1 if i % 2 == 0 else cls.group2),
                text=(
                    'Lorem ipsum dolor sit amet, consectetur adipiscing '
                    'elit, sed do eiusmod tempor incididunt ut labore et '
                    'dolore magna aliqua.'
                )
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
        cls.image_post = Post.objects.create(
            author=cls.user1,
            group=cls.group1,
            text='Lorem ipsum dolor sit amet, consectetur adipiscing',
            image=cls.uploaded
        )

        cls.posts = Post.objects.all()
        cls.post = cls.posts[0]
        cls.paginator_obj_name = 'page_obj'

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostVeiwsTests.user3)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(PostVeiwsTests.user1)
        self.post_author = Client()
        self.post_author.force_login(PostVeiwsTests.post.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_views_uses_correct_templates(self):
        reverse_name_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group1.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user1.username}
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in reverse_name_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'По пути {reverse_name} используется не правильный шаблон'
                )

    def paginator_test(self,
                       reverse_name,
                       paginator_obj_name,
                       posts_number=POSTS_SHOWN_AMOUNT,
                       reverse_kwargs=None,
                       view_queryset=Post.objects.all(),
                       ):
        cache.clear()
        response = self.authorized_client.get(
            reverse(reverse_name, kwargs=reverse_kwargs)
        )
        self.assertEqual(
            len(response.context[paginator_obj_name]),
            posts_number,
            'На страницу выводится неверное количество постов'
        )
        last_page_number = (view_queryset.count() // posts_number) + 1
        posts_number_on_last_page = view_queryset.count() % posts_number
        response = self.authorized_client.get(
            reverse(reverse_name, kwargs=reverse_kwargs)
            + f'?page={last_page_number}'
        )
        self.assertEqual(
            len(response.context[paginator_obj_name]),
            posts_number_on_last_page,
            'На последнюю страницу выводится неверное количество постов'
        )

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        for post in response.context['page_obj']:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)
        post = response.context['page_obj'][0]
        self.assertEqual(post, PostVeiwsTests.post)
        self.assertEqual(post.group, PostVeiwsTests.post.group)
        self.paginator_test('posts:index',
                            paginator_obj_name=self.paginator_obj_name)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group1.slug})
        )
        for post in response.context['page_obj']:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)
                self.assertEqual(post.group, PostVeiwsTests.group1)
        group = response.context['group']
        self.assertEqual(group, PostVeiwsTests.group1)
        self.paginator_test(
            'posts:group_list',
            paginator_obj_name=self.paginator_obj_name,
            reverse_kwargs={'slug': 'test-slug1'},
            view_queryset=group.posts.all(),
        )

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostVeiwsTests.user1.username}
            )
        )
        for post in response.context['page_obj']:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)
                self.assertEqual(post.author, PostVeiwsTests.user1)
        user = response.context['profile_user']
        self.assertEqual(user, PostVeiwsTests.user1)
        self.paginator_test(
            'posts:profile',
            paginator_obj_name=self.paginator_obj_name,
            reverse_kwargs={'username': PostVeiwsTests.user1.username},
            view_queryset=user.posts.all()
        )

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostVeiwsTests.post.id})
        )
        self.assertEqual(response.context['post'], PostVeiwsTests.post)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context['form']
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.post_author.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostVeiwsTests.post.id})
        )
        self.assertEqual(
            response.context['form'].instance,
            PostVeiwsTests.post
        )

    def test_post_with_group_correct_displaying(self):
        responses = {
            'response_home': self.authorized_client.get(
                reverse('posts:index')),
            'response_group': self.authorized_client.get(
                reverse('posts:group_list',
                        kwargs={'slug': PostVeiwsTests.post.group.slug})
            ),
            'response_profile': self.authorized_client.get(
                reverse('posts:profile',
                        kwargs={
                            'username': PostVeiwsTests.post.author.username})
            ),
        }
        for response_name, response in responses.items():
            with self.subTest(response_name=response_name):
                self.assertIn(
                    PostVeiwsTests.post,
                    response.context['page_obj']
                )
        anothergroup = (
            PostVeiwsTests.group2 if PostVeiwsTests.post.group
            == PostVeiwsTests.group1 else PostVeiwsTests.group1
        )
        response_another_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': anothergroup.slug}))
        self.assertNotIn(
            PostVeiwsTests.post,
            response_another_group.context['page_obj']
        )

    def test_post_image(self):
        urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group1.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user1.username}
            ),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                img_post = (response.context.get('page_obj').
                            paginator.object_list.get(id=self.image_post.id))
                self.assertEqual(img_post.image.name, 'posts/small.gif')

        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.image_post.id}
            )
        )
        self.assertEqual(
            response.context.get('post').image.name,
            'posts/small.gif'
        )

    def test_cache(self):
        response1 = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(
            author=self.user1,
            text='Lorem ipsum dolor sit amet, consectetur adipiscing',
        )
        response2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response1.content,
            response2.content
        )
        cache.clear()
        response3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(
            response1.content,
            response3.content
        )

    def test_follow(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.user1.username
                },
            ),
            follow=True
        )
        self.assertTrue(
            Follow.objects.filter(
                user=response.context['request'].user,
                author=self.user1
            ).exists()
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={
                    'username': self.user1.username
                },
            ),
            follow=True
        )
        self.assertFalse(
            Follow.objects.filter(
                user=response.context['request'].user,
                author=self.user1
            ).exists()
        )

    def test_follow_index(self):
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.user1.username
                },
            ),
            follow=True
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        response2 = self.authorized_client2.get(
            reverse('posts:follow_index')
        )
        self.assertNotEqual(
            len(response.context['page_obj'].object_list),
            0,
            'Посты автора не отображаются в избранных'
        )
        self.assertEqual(
            response2.context['page_obj'].object_list.count(),
            0,
            'В избранных отображаются посты которых быть не должно'
        )
