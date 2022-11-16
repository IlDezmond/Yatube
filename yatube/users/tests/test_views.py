from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CreationForm

User = get_user_model()


class PostVeiwsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='User1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_uses_correct_templates(self):
        reverse_name_templates = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:password_change'): 'users/password_change.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'A', 'token': '1'}
            ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
        }
        for reverse_name, template in reverse_name_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'По пути {reverse_name} используется не правильный шаблон'
                )

    def test_signup_view_use_correct_context(self):
        response = self.client.get(reverse('users:signup'))
        self.assertIsInstance(
            response.context['form'],
            CreationForm
        )
