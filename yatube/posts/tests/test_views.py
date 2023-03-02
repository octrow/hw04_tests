from django import forms
from django.conf import settings
from django.test import Client, TestCase

from ..forms import PostForm
from ..models import Group, Post, User
from .const import (AUTHOR, GROUP_DESCRIPTION, GROUP_DESCRIPTION_2, GROUP_SLUG,
                    GROUP_SLUG_2, GROUP_TITLE, GROUP_TITLE_2, POST_TEXT,
                    PUB_DATE, REVERSE_GROUP, REVERSE_GROUP_2, REVERSE_HOME,
                    REVERSE_POST_CREATE, REVERSE_POST_DETAIL,
                    REVERSE_POST_EDIT, REVERSE_PROFILE, TEMPLATES_PAGES_NAMES,
                    THIRTEEN)


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
            pub_date = PUB_DATE
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def check_context(self, query, is_post=False):
        response = self.authorized_client.get(query)
        if is_post:
            post = response.context["post"]
            self.assertEqual(post.id, self.post.pk)
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author.username, self.user.username)
            self.assertEqual(post.group.title, self.group.title)
            self.assertEqual(post.pub_date, self.post.pub_date)
        else:
            page_obj = response.context["page_obj"][0]
            self.assertEqual(page_obj.id, self.post.pk)
            self.assertEqual(page_obj.text, self.post.text)
            self.assertEqual(page_obj.author.username, self.user.username)
            self.assertEqual(page_obj.group.title, self.group.title)
            self.assertEqual(page_obj.pub_date, self.post.pub_date)


    def test_index_grouplist_profile_show_correct_content(self):
        """Шаблоны index, group_list, profile
        сформированы с правильным контекстом."""
        templates_pages_names = [
            REVERSE_HOME,
            REVERSE_GROUP,
            REVERSE_PROFILE,
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                self.check_context(reverse_name)

    def test_post_detail_show_correct_content(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        self.check_context(REVERSE_POST_DETAIL, True)
        

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
                self.assertIn("form", response.context)
                self.assertIsInstance(response.context["form"], PostForm)
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
        posts13 = []
        for i in range(THIRTEEN):
            post1 = Post(
                text=POST_TEXT + "проверка пагинатора номер " + str(i),
                author=cls.user,
                group=cls.group,
            )
            posts13.append(post1)
        Post.objects.bulk_create(posts13)


    def test_first_page_contains_ten_records(self):
        for reverse_names in TEMPLATES_PAGES_NAMES:
            with self.subTest(reverse_name=reverse_names):
                response = self.client.get(reverse_names)
                self.assertEqual(len(response.context["page_obj"]), settings.PAGINATION_ITEMS_PER_PAGE)

    def test_second_page_contains_three_records(self):
        for reverse_names in TEMPLATES_PAGES_NAMES:
            with self.subTest(reverse_name=reverse_names):
                response = self.client.get(reverse_names + "?page=2")
                self.assertEqual(len(response.context["page_obj"]), THIRTEEN - settings.PAGINATION_ITEMS_PER_PAGE)
