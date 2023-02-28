from django import forms
from django.test import Client, TestCase

from ..models import Group, Post, User
from .const import (
    AUTHOR,
    GROUP_DESCRIPTION,
    GROUP_DESCRIPTION_2,
    GROUP_SLUG,
    GROUP_SLUG_2,
    GROUP_TITLE,
    GROUP_TITLE_2,
    POST_TEXT,
    REVERSE_GROUP,
    REVERSE_GROUP_2,
    REVERSE_HOME,
    REVERSE_POST_CREATE,
    REVERSE_POST_DETAIL,
    REVERSE_POST_EDIT,
    REVERSE_PROFILE,
    TEMPLATES_PAGES_NAMES,
)


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE, slug=GROUP_SLUG, description=GROUP_DESCRIPTION
        )
        cls.group_2 = Group.objects.create(
            title=GROUP_TITLE_2,
            slug=GROUP_SLUG_2,
            description=GROUP_DESCRIPTION_2,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT + "testpostcontent",
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            "posts/index.html": REVERSE_HOME,
            "posts/group_list.html": REVERSE_GROUP,
            "posts/profile.html": REVERSE_PROFILE,
            "posts/post_detail.html": REVERSE_POST_DETAIL,
            "posts/create_post.html": REVERSE_POST_CREATE,
            "posts/create_post.html": REVERSE_POST_EDIT,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_three_pages_posts_show_correct_content(self):
        """Шаблоны index, group_list, profile
        сформированы с правильным контекстом."""
        templates_pages_names = [
            REVERSE_HOME,
            REVERSE_GROUP,
            REVERSE_PROFILE,
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context["page_obj"][0]
                self.assertEqual(first_object.id, self.post.pk)
                self.assertEqual(first_object.text, self.post.text)
                self.assertEqual(
                    first_object.author.username, self.user.username
                )
                self.assertEqual(first_object.group.title, self.group.title)

    def test_post_detail_show_correct_content(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(REVERSE_POST_DETAIL)
        self.assertEqual(response.context["post"].text, self.post.text)
        self.assertEqual(
            response.context["post"].author.username, self.user.username
        )
        self.assertEqual(
            response.context["post"].group.title, self.group.title
        )

    def test_create_post_and_post_edit_show_correct_content(self):
        """Шаблон create_post.html сформированы с правильным контекстом."""
        templates_name_pages = [
            REVERSE_POST_CREATE,
            REVERSE_POST_EDIT,
        ]
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for page in templates_name_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                for field, field_type in form_fields.items():
                    with self.subTest(field=field):
                        form_field = response.context["form"].fields[field]
                        self.assertIsInstance(form_field, field_type)

    def test_check_post_correct_group_page(self):
        response = self.authorized_client.get(REVERSE_GROUP)
        self.assertEqual(len(response.context["page_obj"]), 1)
        response = self.authorized_client.get(REVERSE_GROUP_2)
        self.assertEqual(len(response.context["page_obj"]), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text=POST_TEXT + " " + str(i),
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        for reverse_names in TEMPLATES_PAGES_NAMES:
            with self.subTest(reverse_name=reverse_names):
                response = self.guest_client.get(reverse_names)
                self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_page_contains_three_records(self):
        for reverse_names in TEMPLATES_PAGES_NAMES:
            with self.subTest(reverse_name=reverse_names):
                response = self.guest_client.get(reverse_names + "?page=2")
                self.assertEqual(len(response.context["page_obj"]), 3)
