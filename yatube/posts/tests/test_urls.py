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
    POST_1_EDIT_URL,
    POST_1_URL,
    POST_TEXT,
    POST_URL,
    PROFILE_URL,
    REVERSE_GROUP,
    REVERSE_HOME,
    REVERSE_LOGIN,
    REVERSE_POST_CREATE,
    REVERSE_POST_DETAIL,
    REVERSE_POST_EDIT,
    REVERSE_PROFILE,
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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(StaticURLTests.anotheruser)

    def test_direct_urls_equal_reverse_urls(self):
        """URL-адрес соответствует reverse_urls."""
        urls_names = (
            (INDEX_URL, REVERSE_HOME),
            (GROUP_URL, REVERSE_GROUP),
            (PROFILE_URL, REVERSE_PROFILE),
            (POST_1_URL, REVERSE_POST_DETAIL),
            (CREATE_URL, REVERSE_POST_CREATE),
            (POST_1_EDIT_URL, REVERSE_POST_EDIT),
        )
        for url, reverse_url in urls_names:
            with self.subTest(url=url):
                self.assertEqual(url, reverse_url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = (
            (REVERSE_HOME, (), "posts/index.html"),
            (REVERSE_GROUP, (), "posts/group_list.html"),
            (REVERSE_PROFILE, (), "posts/profile.html"),
            (REVERSE_POST_DETAIL, (self.post.id,), "posts/post_detail.html"),
            (REVERSE_POST_CREATE, (), "posts/create_post.html"),
            (REVERSE_POST_EDIT, (self.post.id,), "posts/create_post.html"),
        )
        for url, argument, template in templates_url_names:
            with self.subTest(template=template):
                response = self.authorized_client.get(
                    url, data={"argument": argument}
                )
                self.assertTemplateUsed(response, template)

    def test_urls_404(self):
        """Несуществующий URL-адрес возвращает ошибку 404."""
        response = self.client.get(UNEXISTING_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_all_urls_access_author(self):
        """Все URL-адреса доступны для авторизованного автора пользователя."""
        templates_url_names = (
            (REVERSE_HOME, ()),
            (REVERSE_GROUP, ()),
            (REVERSE_PROFILE, ()),
            (REVERSE_POST_DETAIL, (self.post.id,)),
            (REVERSE_POST_CREATE, ()),
            (REVERSE_POST_EDIT, (self.post.id,)),
        )
        for url, argument in templates_url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(
                    url, data={"argument": argument}
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_access_another_user(self):
        """URL-адреса доступные для другого пользователя."""
        templates_url_names = (
            (REVERSE_HOME, ()),
            (REVERSE_GROUP, ()),
            (REVERSE_PROFILE, ()),
            (REVERSE_POST_DETAIL, (self.post.id)),
            (REVERSE_POST_CREATE, ()),
        )
        for url, argument in templates_url_names:
            with self.subTest(url=url):
                response = self.another_authorized_client.get(
                    url, data={"argument": argument}
                )
                if url == REVERSE_POST_EDIT:
                    self.assertRedirects(response, REVERSE_POST_DETAIL)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_access_guest(self):
        """URL-адреса доступны для неавторизованного пользователя."""
        url_names = (
            (REVERSE_HOME),
            (REVERSE_GROUP),
            (REVERSE_PROFILE),
            (REVERSE_POST_DETAIL),
            (REVERSE_POST_CREATE),
            (REVERSE_POST_EDIT),
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.client.get(url)
                if REVERSE_POST_CREATE == url or REVERSE_POST_EDIT == url:
                    expected_redirect = f"{REVERSE_LOGIN}?next={url}"
                    self.assertRedirects(response, expected_redirect)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
