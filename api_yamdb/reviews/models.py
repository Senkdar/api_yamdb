from django.contrib.auth.models import AbstractUser
from django.db import models


class User (AbstractUser):
    """Модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    ROLE_CHOICES = [
        (USER, 'User'),
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator')
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    bio = models.CharField(
        max_length=300,
        blank=True,
    )
    role = models.CharField(
        max_length=50,
        default=USER,
        choices=ROLE_CHOICES,
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        ordering = ('username',)

    def __str__(self):
        """Выводит имя пользователя."""
        return self.username


class Category(models.Model):
    """Модель категории."""
    name = models.CharField(
        max_length=256,
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
    )

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        """Выводит наименование категории."""
        return self.name


class Genre(models.Model):
    """Модель жанра."""
    name = models.CharField(
        max_length=256,
    )
    slug = models.SlugField(
        unique=True,
    )

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        """Выводит наименование жанра."""
        return self.name


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(
        max_length=256,
    )
    year = models.IntegerField()
    description = models.CharField(
        blank=True,
        max_length=256,
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
    )

    class Meta:
        ordering = ('-year',)

    def __str__(self):
        """Выводит наименование произведения."""
        return self.name


class TitleGenre(models.Model):
    """Модель для связи произведения и жанра."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """Выводит наименование жанра."""
        return self.genre


class Review(models.Model):
    """Модель отзыва."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField()
    score = models.IntegerField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_review'
            )
        ]

    def __str__(self):
        """Выводит текст отзыва."""
        return self.text


class Comment(models.Model):
    """Модель комментария."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        """Выводит текст комментария."""
        return self.text
