from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class PostVeiwsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_user_create(self):
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Testfn',
            'last_name': 'Testln',
            'username': 'Testun',
            'email': 'test@example.com',
            'password1': 'TestPass1587',
            'password2': 'TestPass1587',
        }
        self.client.post(
            reverse('users:signup'),
            data=form_data,
        )
        self.assertEqual(User.objects.count(), users_count + 1)
