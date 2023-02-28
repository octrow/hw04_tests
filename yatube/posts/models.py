from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Имя группы", max_length=200)
    slug = models.SlugField("Slug группы", unique=True)
    description = models.TextField("Описание группы")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        if not self.title:
            return "Группа без названия"
        return self.title


class Post(models.Model):
    text = models.TextField("Текст поста", help_text='Введите текст поста')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор поста",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text='Группа, к которой будет относиться пост'
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост",
        verbose_name_plural = "Посты"

    def __str__(self):
        return f"{self.text[:15]}... "
