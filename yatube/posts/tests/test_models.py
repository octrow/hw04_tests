from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(author=cls.user, text="Тестовый пост")

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(str(PostModelTest.post), "Тестовый пост... ")
        self.assertEqual(str(PostModelTest.group), "Тестовая группа")

    def test_models_have_correct_verbose_names(self):
        """Проверяем, что модели имеют верное поле verbose_names."""
        self.assertEqual(
            Post._meta.get_field("text").verbose_name, "Текст поста"
        )
        self.assertEqual(
            Group._meta.get_field("title").verbose_name, "Имя группы"
        )

    def test_models_have_correct_help_texts(self):
        """Проверяем, что моделей имеет верное поле help_text."""
        self.assertEqual(
            Post._meta.get_field("text").help_text, "Введите текст поста"
        )
        self.assertEqual(Group._meta.get_field("title").help_text, "")

    def test_post_creation(self):
        """Проверяем, что модели создаются правильно."""
        self.assertEqual(PostModelTest.post.text, "Тестовый пост")
        self.assertEqual(PostModelTest.post.author, PostModelTest.user)
        self.assertEqual(PostModelTest.group.title, "Тестовая группа")
        self.assertEqual(PostModelTest.group.slug, "test_slug")
        self.assertEqual(PostModelTest.group.description, "Тестовое описание")
        self.assertEqual(PostModelTest.user.username, "auth")

    def test_group_creation(self):
        """Проверяем, что модель Group создается правильно."""
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(
            Group.objects.get(title="Тестовая группа").title, "Тестовая группа"
        )
        self.assertEqual(
            Group.objects.get(title="Тестовая группа").slug, "test_slug"
        )
        self.assertEqual(
            Group.objects.get(title="Тестовая группа").description,
            "Тестовое описание",
        )
