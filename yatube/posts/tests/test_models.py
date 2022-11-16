from .fixtures import FixturesTestCase


CHARS = 15


class PostModelTest(FixturesTestCase):
    def test_models_have_correct_object_names(self):
        post_name = PostModelTest.post
        expected_post_name = self.post.text[:CHARS]
        self.assertEqual(str(post_name), expected_post_name)
        group_title = PostModelTest.group
        expected_group_title = self.group.title
        self.assertEqual(str(group_title), expected_group_title)

    def test_post_model_objects_have_correct_verbose_name(self):
        post = PostModelTest.post
        verbose_name_fields = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in verbose_name_fields.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value
                )
