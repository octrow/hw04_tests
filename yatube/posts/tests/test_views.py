import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post, User
from .const import (AUTHOR, COMMENT_TEXT, GROUP_DESCRIPTION,
                    GROUP_DESCRIPTION_2, GROUP_SLUG, GROUP_SLUG_2, GROUP_TITLE,
                    GROUP_TITLE_2, POST_TEXT, PUB_DATE, THIRTEEN)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE, slug=GROUP_SLUG, description=GROUP_DESCRIPTION
        )
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.image_upload = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
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
            pub_date=PUB_DATE,
            image=cls.image_upload,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=COMMENT_TEXT,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_context(self, query, is_post=False):
        if is_post:
            post = query.context["post"]
        else:
            post = query.context["page_obj"][0]
        self.assertEqual(post.id, self.post.pk)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author.id, self.user.id)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.image, f"posts/{self.image_upload}")

    def test_index_grouplist_profile_show_correct_content(self):
        """Шаблоны index, group_list, profile
        сформированы с правильным контекстом."""
        pages_name = (
            ("posts:index", None),
            ("posts:group_list", (self.group.slug,)),
            ("posts:profile", (self.user.username,)),
        )
        for reverse_name, argument in pages_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse(reverse_name, args=argument)
                )
                self.check_context(response)
                if reverse_name == "posts:group_list":
                    self.assertEqual(response.context["group"], self.group)
                if reverse_name == "posts:profile":
                    self.assertEqual(response.context["author"], self.user)

    def test_post_detail_show_correct_content(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", args=(self.post.id,))
        )
        # form_fields = {
        #     "text": forms.fields.CharField,
        # }
        self.check_context(response, True)
        self.assertEqual(response.context["comments"][0], self.comment)

    def test_create_post_and_post_edit_show_correct_content(self):
        """Шаблон create_post.html сформированы с правильным контекстом."""
        templates_name_pages = (
            ("posts:post_create", None),
            ("posts:post_edit", (self.post.id,)),
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for page, argument in templates_name_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(
                    reverse(page, args=argument)
                )
                self.assertIn("form", response.context)
                self.assertIsInstance(response.context["form"], PostForm)
                for field, field_type in form_fields.items():
                    with self.subTest(field=field):
                        form_field = response.context["form"].fields[field]
                        self.assertIsInstance(form_field, field_type)

    def test_check_post_correct_group_page(self):
        response = self.authorized_client.get(
            reverse("posts:group_list", args=(self.group.slug,))
        )
        self.assertEqual(len(response.context["page_obj"]), 1)
        response = self.authorized_client.get(
            reverse("posts:group_list", args=(self.group_2.slug,))
        )
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
        for postnumer in range(THIRTEEN):
            post1 = Post(
                text=POST_TEXT + "проверка пагинатора номер " + str(postnumer),
                author=cls.user,
                group=cls.group,
            )
            posts13.append(post1)
        Post.objects.bulk_create(posts13)

    def test_first_page_contains_ten_records(self):
        pages_name = (
            ("posts:index", None),
            ("posts:group_list", (self.group.slug,)),
            ("posts:profile", (self.user.username,)),
        )
        number_posts = (
            ("?page=1", settings.PAGINATION_ITEMS_PER_PAGE),
            ("?page=2", THIRTEEN - settings.PAGINATION_ITEMS_PER_PAGE),
        )
        for reverse_names, argument in pages_name:
            with self.subTest(reverse_names=reverse_names):
                url_with_arg = reverse(reverse_names, args=argument)
                for last_part_url, number in number_posts:
                    with self.subTest(last_part_url=last_part_url):
                        response = self.client.get(
                            url_with_arg + last_part_url
                        )
                        self.assertEqual(
                            len(response.context["page_obj"]), number
                        )
