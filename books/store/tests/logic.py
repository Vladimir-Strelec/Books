import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test.testcases import TestCase

from books.store.models import Book, UserBookRelation
from books.store.serializers import BookSerializer, BookRelationSerializer


class BookSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='User test')
        self.book_1 = Book.objects.create(name='Test1', price=5, author_name='Testov')
        self.book_2 = Book.objects.create(name='Test2', price=5, author_name='Testov2')

    def test_serializer(self):
        books = Book.objects.all().annotate(annotated_like=Count(Case(When(userbookrelation__like=True, then=1))),
                                            mid_rate=Avg('userbookrelation__rate')).order_by('id')
        serializer = BookSerializer(books, many=True).data
        data = [
            {
                'id': self.book_1.id,
                'name': 'Test1',
                'price': '5.00',
                'author_name': 'Testov',
                'like_count': 0,
                'annotated_like': 0,
                'mid_rate': None

            },
            {
                'id': self.book_2.id,
                'name': 'Test2',
                'price': '5.00',
                'author_name': 'Testov2',
                'like_count': 0,
                'annotated_like': 0,
                'mid_rate': None
            },
        ]

        self.assertEqual(data, serializer)


class BookRelationSerializerTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='User1')
        self.user2 = User.objects.create(username='User2')

        self.book_1 = Book.objects.create(name='Test1', price=5, author_name='Testov1')
        self.book_2 = Book.objects.create(name='Test2', price=5, author_name='Testov2')

        UserBookRelation.objects.create(user=self.user1, book=self.book_1, like=True)
        UserBookRelation.objects.create(user=self.user2, book=self.book_1, like=True)

        UserBookRelation.objects.create(user=self.user1, book=self.book_2, like=True)
        UserBookRelation.objects.create(user=self.user2, book=self.book_2, like=False)

    def test_like_and_annotated(self):
        books = Book.objects.all().annotate(annotated_like=Count(Case(When(userbookrelation__like=True, then=1))),
                                            mid_rate=Avg('userbookrelation__rate')).order_by('id')
        serializer = BookSerializer(books, many=True).data

        data = [
            {
                'id': self.book_1.id,
                'name': 'Test1',
                'price': '5.00',
                'author_name': 'Testov1',
                'like_count': 2,
                'annotated_like': 2,
                'mid_rate': None
            },
            {
                'id': self.book_2.id,
                'name': 'Test2',
                'price': '5.00',
                'author_name': 'Testov2',
                'like_count': 1,
                'annotated_like': 1,
                'mid_rate': None
            },
        ]

        self.assertEqual(data, serializer)


class MidRateBookRelationSerializerTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='User1')
        self.user2 = User.objects.create(username='User2')

        self.book_1 = Book.objects.create(name='Test1', price=5, author_name='Testov1')
        self.book_2 = Book.objects.create(name='Test2', price=5, author_name='Testov2')

        UserBookRelation.objects.create(user=self.user1, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user2, book=self.book_1, like=True, rate=5)

        UserBookRelation.objects.create(user=self.user1, book=self.book_2, like=True, rate=2)
        UserBookRelation.objects.create(user=self.user2, book=self.book_2, like=False, rate=2)

    def test_mid_rate(self):
        books = Book.objects.all().annotate(annotated_like=Count(Case(When(userbookrelation__like=True, then=1))),
                                            mid_rate=Avg('userbookrelation__rate')).order_by('id')


        serializer = BookSerializer(books, many=True).data
        data = [
            {
                'id': self.book_1.id,
                'name': 'Test1',
                'price': '5.00',
                'author_name': 'Testov1',
                'like_count': 2,
                'annotated_like': 2,
                'mid_rate': '5.00'
            },
            {
                'id': self.book_2.id,
                'name': 'Test2',
                'price': '5.00',
                'author_name': 'Testov2',
                'like_count': 1,
                'annotated_like': 1,
                'mid_rate': '2.00'
            }
        ]

        self.assertEqual(data, serializer)