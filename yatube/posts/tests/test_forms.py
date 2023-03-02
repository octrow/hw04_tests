from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User
from .const import (AUTHOR, GROUP_DESCRIPTION, GROUP_DESCRIPTION_2, GROUP_SLUG,
                    GROUP_SLUG_2, GROUP_TITLE, GROUP_TITLE_2, POST_TEXT,
                    REVERSE_GROUP, REVERSE_POST_CREATE, REVERSE_POST_EDIT,
                    REVERSE_PROFILE)


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


    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def test_create_post_form_valid_data(self):
        """Форма создает пост в указанном группе."""
        form_data = {
            "text": POST_TEXT,
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            REVERSE_POST_CREATE,
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=Post.objects.latest("id").id)
        self.assertRedirects(response, REVERSE_PROFILE)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.text, POST_TEXT)

    def test_edit_post_correct(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": POST_TEXT + "отредактированный",
            "group": self.group_2.id,
        }
        self.authorized_client.post(
            REVERSE_POST_EDIT,
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=Post.objects.latest("id").id)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, self.group_2.id)
        self.assertEqual(post.text, POST_TEXT + "отредактированный")
        self.assertEqual(Post.objects.count(), posts_count)
        response = self.authorized_client.get(REVERSE_GROUP)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_access_post_create(self):
        """Не доступно для гостевого пользователя."""
        posts_count = Post.objects.count()
        form_data = {
            "text": POST_TEXT,
            "group": self.group.id,
        }
        response = self.guest_client.post(
            REVERSE_POST_CREATE, data=form_data, follow=True
        )
        # self.assertNotEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_access_post_edit(self):
        """Не доступно для гостевого пользователя."""
        form_data = {
            "text": POST_TEXT + "невозможный",
            "group": self.group_2.id,
        }
        self.guest_client.post(
            REVERSE_POST_EDIT,
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=Post.objects.latest("id").id)
        self.assertNotEqual(post.text, POST_TEXT + "невозможный")
