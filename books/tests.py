from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Author, Book

class BookModelTest(TestCase):
    """Тесты на уровне модели."""

    def setUp(self):
        self.author = Author.objects.create(name="Лев Толстой")

    def test_unique_fiction_constraint(self):
        """Художественная книга с одинаковыми названием, автором и издательством не может быть создана дважды."""
        Book.objects.create(
            title="Война и мир",
            author=self.author,
            year=1869,
            genre="Роман",
            category="fiction",
            publisher="Эксмо"
        )
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Война и мир",
                author=self.author,
                year=1870,  # другой год — не важно для fiction
                genre="Роман",
                category="fiction",
                publisher="Эксмо"
            )

    def test_unique_textbook_constraint(self):
        """Учебник с одинаковыми названием, автором, издательством и годом не может быть создан дважды."""
        Book.objects.create(
            title="Алгебра",
            author=self.author,
            year=2020,
            genre="Математика",
            category="textbook",
            publisher="Просвещение"
        )
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Алгебра",
                author=self.author,
                year=2020,
                genre="Математика",
                category="textbook",
                publisher="Просвещение"
            )

    def test_different_textbook_editions_allowed(self):
        """Разные переиздания учебника (разный год) — разрешены."""
        book1 = Book.objects.create(
            title="Алгебра",
            author=self.author,
            year=2020,
            genre="Математика",
            category="textbook",
            publisher="Просвещение"
        )
        book2 = Book.objects.create(
            title="Алгера",
            author=self.author,
            year=2022,
            genre="Математика",
            category="textbook",
            publisher="Просвещение"
        )
        self.assertNotEqual(book1.id, book2.id)


class BookAPITestCase(TestCase):
    """Тесты REST API."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )
        self.author = Author.objects.create(name="Фёдор Достоевский")
        self.author_data = {"name": "Антон Чехов", "biography": "Русский классик"}

    def test_anonymous_can_read_books(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create_book(self):
        response = self.client.post('/api/books/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_create_book(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/books/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_book(self):

        self.client.force_authenticate(user=self.admin)
        data = {
            "title": "Преступление и наказание",
            "author_id": self.author.id,
            "year": 1866,
            "genre": "Роман",
            "category": "fiction",
            "publisher": "Азбука"
        }
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

    def test_admin_can_create_author(self):

        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/authors/', self.author_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 2)  # +1 к Достоевскому

    def test_search_books_by_title(self):

        Book.objects.create(
            title="Идиот",
            author=self.author,
            year=1869,
            genre="Роман",
            category="fiction",
            publisher="Эксмо"
        )
        response = self.client.get('/api/books/?search=Идиот')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_books_by_author(self):

        Book.objects.create(
            title="Братья Карамазовы",
            author=self.author,
            year=1880,
            genre="Роман",
            category="fiction",
            publisher="Азбука"
        )
        response = self.client.get('/api/books/?search=Достоевский')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_fiction_unique_validation_api(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "title": "Анна Каренина",
            "author_id": self.author.id,
            "year": 1877,
            "genre": "Роман",
            "category": "fiction",
            "publisher": "Оникс"
        }
        # Первое добавление — успешно
        response1 = self.client.post('/api/books/', data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Повторное — ошибка
        response2 = self.client.post('/api/books/', data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Книга с такими параметрами уже существует", str(response2.data))

    def test_textbook_unique_validation_api(self):

        self.client.force_authenticate(user=self.admin)
        data = {
            "title": "Физика 10",
            "author_id": self.author.id,
            "year": 2023,
            "genre": "Физика",
            "category": "textbook",
            "publisher": "Дрофа"
        }
        self.client.post('/api/books/', data)
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)