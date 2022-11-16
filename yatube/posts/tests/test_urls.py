from http import HTTPStatus

from django.urls import reverse

from .fixtures import FixturesTestCase


class PostURLTests(FixturesTestCase):
    def test_urls_exists_at_desired_location(self):
        urls_path = [
            reverse('posts:post_create'),
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
        ]
        for url in urls_path:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_author_only_available(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertTemplateUsed(
            response,
            'posts/post_edit_denied.html',
            (
                'Другие пользователи помимо автора поста '
                'могут редактировать пост'
            )
        )
        response = self.post_author.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertTemplateUsed(
            response,
            'posts/create_post.html',
            'Автор поста не может редактировать свой пост'
        )

    def test_login_required_urls_redirects_anonymous(self):
        urls_redirects = {
            reverse('posts:post_create'): (f'{reverse("users:login")}?next='
                                           f'{reverse("posts:post_create")}'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): (
                reverse("users:login") + '?next='
                + reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.id}
                )
            )
        }
        for url, redirect in urls_redirects.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, redirect)

    def test_urls_uses_correct_template(self):
        urls_templates = {
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
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
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.post_author.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'По пути {url} используется не правильный шаблон'
                )

    def test_not_exist_url(self):
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
