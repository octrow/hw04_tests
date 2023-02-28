from django.urls import reverse

AUTHOR = "NewNameUser"
ANOTHERUSER = "AnotherUser"
GROUP_TITLE = "Тестовая группа"
GROUP_SLUG = "test_slug"
GROUP_DESCRIPTION = "Тестовое описание два"
GROUP_TITLE_2 = "Тестовая группа два"
GROUP_SLUG_2 = "test_slug_two"
GROUP_DESCRIPTION_2 = "Тестовое описание два"
POST_TEXT = "Тестовая запись"

INDEX_URL = "/"
ABOUT_AUTHOR_URL = "/about/author/"
ABOUT_TECH_URL = "/about/tech/"
GROUP_URL = "/group/" + GROUP_SLUG + "/"
PROFILE_URL = "/profile/" + AUTHOR + "/"
CREATE_URL = "/create/"
POST_URL = "/posts/"
EDIT_URL = "/edit/"
UNEXISTING_URL = "/unexisting_url/"

REVERSE_HOME = reverse("posts:index")
REVERSE_GROUP = reverse("posts:group_list", kwargs={"slug": GROUP_SLUG})
REVERSE_GROUP_2 = reverse("posts:group_list", kwargs={"slug": GROUP_SLUG_2})
REVERSE_PROFILE = reverse("posts:profile", kwargs={"username": AUTHOR})
REVERSE_POST_DETAIL = reverse("posts:post_detail", kwargs={"post_id": "1"})
REVERSE_POST_CREATE = reverse("posts:post_create")
REVERSE_POST_EDIT = reverse("posts:post_edit", kwargs={"post_id": "1"})
REVERSE_POST_DELETE = reverse("posts:post_delete", kwargs={"post_id": "1"})

TEMPLATES_PAGES_NAMES = {
    REVERSE_HOME,
    REVERSE_GROUP,
    REVERSE_PROFILE,
}
