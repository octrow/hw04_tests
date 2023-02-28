import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings

from ..models import Group, Post, User
from .const import (AUTHOR, GROUP_DESCRIPTION, GROUP_DESCRIPTION_2, GROUP_SLUG,
                    GROUP_SLUG_2, GROUP_TITLE, GROUP_TITLE_2, POST_TEXT,
                    REVERSE_POST_CREATE, REVERSE_POST_EDIT, REVERSE_PROFILE)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.group_2 = Group.objects.create(
            title=GROUP_TITLE_2,
            slug=GROUP_SLUG_2,
            description=GROUP_DESCRIPTION_2,
        )
        Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form_valid_data(self):
        """Форма создает пост в указанном группе."""
        posts_count = Post.objects.count()
        form_data = {
            "text": POST_TEXT,
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            REVERSE_POST_CREATE,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, REVERSE_PROFILE)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=POST_TEXT,
                author=self.user,
                group=self.group,
            ).exists()
        )

    def test_edit_post_correct(self):
        form_data = {
            "text": POST_TEXT + "отредактированный",
            "group": self.group_2.id,
        }
        self.authorized_client.post(
            REVERSE_POST_EDIT,
            data=form_data,
            follow=True,
        )
        self.assertTrue(
            Post.objects.filter(
                text=POST_TEXT + "отредактированный",
                group=self.group_2,
            )
        )
