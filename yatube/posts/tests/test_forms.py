from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.models import Post
from .fixtures import FixturesTestCase


class PostFormsTests(FixturesTestCase):
    def test_post_create(self):
        post_counts = Post.objects.count()
        form_data = {'text': 'Тестовый текст'}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        self.assertEqual(post_counts + 1, Post.objects.count())
        self.assertEqual(
            Post.objects.order_by('id').last().text,
            form_data['text']
        )

    def test_post_edit(self):
        form_data = {'text': 'Изменённый тестовый текст'}
        response = self.post_author.post(
            reverse(
                'posts:post_edit',
                args=(self.post.id,)
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).text,
            form_data['text']
        )

    def test_image_post_create(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_counts = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(post_counts + 1, Post.objects.count())


class CommentFormTest(FixturesTestCase):
    def test_comment_login_required(self):
        form_data = {'text': 'Тестовый комментарий'}
        redirect_url = reverse(
            'users:login'
        )
        reverse_url = reverse(
            'posts:add_comment',
            args=(self.post.id,)
        )
        response = self.client.post(
            reverse_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'{redirect_url}?next={reverse_url}'
        )

    def test_comment_create(self):
        form_data = {'text': 'Тестовый комментарий'}
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                args=(self.post.id,)
            ),
            data=form_data,
            follow=True
        )
        response = self.client.get(
            reverse(
                'posts:post_detail',
                args=(self.post.id,)
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            response.context['comments'][0].text,
            form_data['text']
        )
