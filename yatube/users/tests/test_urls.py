from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='User2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_no_login_required_urls_exists_at_desired_location(self):
        urls_path = [
            '/auth/logout/',
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/A/1/',
            '/auth/reset/done/',
        ]
        for url in urls_path:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_required_urls_exists_at_desired_location(self):
        urls_path = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]
        for url in urls_path:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_required_urls_redirects_anonymous(self):
        urls_redirects = {
            '/auth/password_change/': ('/auth/login/?next='
                                       '/auth/password_change/'),

        }
        for url, redirect in urls_redirects.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, redirect)

    def test_urls_uses_correct_template(self):
        urls_templates = {
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/': 'users/password_change.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/A/1/': 'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'По пути {url} используется не правильный шаблон'
                )
