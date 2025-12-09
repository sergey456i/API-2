from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Author(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Имя автора"
    )
    biography = models.TextField(
        blank=True,
        verbose_name="Биография"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата рождения"
    )

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    CATEGORY_CHOICES = [
        ('fiction', 'Художественная литература'),
        ('textbook', 'Учебник'),
    ]

    title = models.CharField(
        max_length=100,
        verbose_name="Название книги"
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name="Автор"
    )
    year = models.IntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(9999)
        ],
        verbose_name="Год выпуска"
    )
    genre = models.CharField(
        max_length=100,
        verbose_name="Жанр"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="Категория"
    )
    publisher = models.CharField(
        max_length=100,
        verbose_name="Издательство"
    )
    cover_image = models.ImageField(
        upload_to='covers/',
        blank=True,
        null=True,
        verbose_name="Обложка"
    )
    file = models.FileField(
        upload_to='books/',
        blank=True,
        null=True,
        verbose_name="Файл книги"
    )

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['title', 'year']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author', 'year', 'publisher'],
                condition=models.Q(category='textbook'),
                name='unique_textbook_edition'
            ),
            models.UniqueConstraint(
                fields=['title', 'author', 'publisher'],
                condition=models.Q(category='fiction'),
                name='unique_fiction_edition'
            ),
        ]

    def __str__(self):
        return f"{self.title} — {self.author.name} ({self.year})"