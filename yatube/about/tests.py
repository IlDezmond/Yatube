from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutURLTests(TestCase):
    def test_no_login_required_urls_exists_at_desired_location(self):
        urls_path = [
            '/about/author/',
            '/about/tech/',
        ]
        for url in urls_path:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        urls_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'По пути {url} используется не правильный шаблон'
                )


class AboutViewsTests(TestCase):
    def test_views_uses_correct_templates(self):
        reverse_name_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in reverse_name_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'По пути {reverse_name} используется не правильный шаблон'
                )
