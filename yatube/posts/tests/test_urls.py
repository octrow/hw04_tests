from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User
from .const import (
    ANOTHERUSER,
    AUTHOR,
    CREATE_URL,
    EDIT_URL,
    GROUP_DESCRIPTION,
    GROUP_SLUG,
    GROUP_TITLE,
    GROUP_URL,
    INDEX_URL,
    POST_TEXT,
    POST_URL,
    PROFILE_URL,
    UNEXISTING_URL,
)


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.anotheruser = User.objects.create_user(username=ANOTHERUSER)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )
        cls.templates_url_names = {
            INDEX_URL: "posts/index.html",
            GROUP_URL: "posts/group_list.html",
            PROFILE_URL: "posts/profile.html",
            POST_URL
            + str(StaticURLTests.post.pk)
            + "/": "posts/post_detail.html",
            # Далее адреса без общего доступа
            POST_URL
            + str(StaticURLTests.post.pk)
            + EDIT_URL: "posts/create_post.html",
            CREATE_URL: "posts/create_post.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(StaticURLTests.anotheruser)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_404(self):
        """Несуществующий URL-адрес возвращает ошибку 404."""
        response = self.guest_client.get(UNEXISTING_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_public_access(self):
        """URL-адреса доступны для любого пользователя."""
        for url in list(self.templates_url_names.keys())[:4]:
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_denied_access(self):
        """URL-адреса запрещены для неавторизованного пользователя."""
        for url in list(self.templates_url_names.keys())[4:]:
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_authorized_access(self):
        """URL-адрес доступен для авторизованного пользователя."""
        response = self.authorized_client.get(CREATE_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_access_edit(self):
        """URL-адрес доступен для авторизованного автора пользователя."""
        response = self.authorized_client.get(
            POST_URL + str(StaticURLTests.post.pk) + EDIT_URL
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_denied_access_edit(self):
        """URL-адрес запрещён для другого авторизованного пользователя."""
        response = self.another_authorized_client.get(
            POST_URL + str(StaticURLTests.post.pk) + EDIT_URL
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
