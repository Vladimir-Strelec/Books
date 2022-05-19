import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from books.store.models import Book, UserBookRelation
from books.store.serializers import BookSerializer


class BooksApiTests(APITestCase):
    URL = reverse('book-list')

    def setUp(self):
        self.user = User.objects.create(username='testname')
        self.user2 = User.objects.create(username='Test')
        self.user3 = User.objects.create(username='Testov', is_staff=True)
        self.book1 = Book.objects.create(name='test', price=5, author_name='author1', owner=self.user)
        self.book2 = Book.objects.create(name='test', price=4, author_name='author2', owner=self.user)
        self.book3 = Book.objects.create(name='author1', price=3, author_name='author3', owner=self.user)

    def test_method_get(self):
        books = Book.objects.all().annotate(annotated_like=Count(Case(When(userbookrelation__like=True, then=1))),
                                            mid_rate=(Avg('userbookrelation__rate'))).order_by('id')
        response = self.client.get(self.URL)
        serializer = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer, response.data)

    def test_search(self):
        books = Book.objects.filter(id__in=[self.book1.id, self.book3.id])\
            .annotate(annotated_like=Count(Case(When(userbookrelation__like=True, then=1))),
                      mid_rate=Avg('userbookrelation__rate')).order_by('id')
        response = self.client.get(self.URL, data={'search': 'author1'})
        serializer = BookSerializer(books, many=True).data
        self.assertEqual(serializer, response.data)

    def test_ordering(self):
        books = Book.objects.all().annotate(annotated_like=Count(Case(When(userbookrelation__like=True, then=1))),
                                            mid_rate=Avg('userbookrelation__rate')).order_by('price')
        response = self.client.get(self.URL, data={'ordering': 'price'})
        serializer = BookSerializer(books, many=True).data
        self.assertEqual(serializer, response.data)

    def test_filter(self):
        books = Book.objects.all().annotate(annotated_like=Count(Case(When(userbookrelation__like=True, then=1))),
                                            mid_rate=Avg('userbookrelation__rate')).order_by('price')[::-1]
        response = self.client.get(self.URL, data={'filter': 'price'})
        serializer = BookSerializer(books, many=True).data
        self.assertEqual(serializer, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        data = {
            "name": "test",
            "price": 15,
            "author_name": "testov",

        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(self.URL, data=json_data, content_type='application/json')
        print(response.data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        data = {
            "name": self.book1.name,
            "price": 500,
            "author_name": self.book1.author_name,
            "mid_rate": 0

        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(reverse('book-detail', args=(self.book1.id,)), data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1 = Book.objects.get(id=self.book1.id)
        self.assertEqual(500, self.book1.price)

    def test_delete(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse('book-detail', args=(self.book3.id,)), content_type='application/json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_not_is_authenticated(self):
        response = self.client.delete(reverse('book-detail', args=(self.book3.id,)), content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


    def test_update_not_is_authenticated(self):
        data = {
            "name": self.book1.name,
            "price": 500,
            "author_name": self.book1.author_name
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(reverse('book-detail', args=(self.book2.id,)), data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.book2 = Book.objects.get(id=self.book2.id)
        self.assertEqual(4.00, self.book2.price)

    def test_update_not_is_authenticated_bud_is_staff(self):
        user_staff = User.objects.create(username='user staff', is_staff=True)
        user_not_is_staff = User.objects.create(username='user not_is_staff', is_staff=False)
        data = {
            "id": self.book2.id,
            "name": self.book2.name,
            "price": 5,
            "author_name": self.book2.author_name,
            "mid_rate": 0
        }
        self.client.force_login(user_staff)
        json_data = json.dumps(data)
        response = self.client.put(reverse('book-detail', args=(self.book2.id,)), data=json_data,
                                   content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book2 = Book.objects.get(id=self.book2.id)
        self.assertEqual(5.00, self.book2.price)

        self.client.force_login(user_not_is_staff)
        response = self.client.put(reverse('book-detail', args=(self.book2.id,)), data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class BooksRelationApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='testname')
        self.user2 = User.objects.create(username='Test')
        self.book1 = Book.objects.create(name='test', price=5, author_name='author1', owner=self.user)
        self.book2 = Book.objects.create(name='test', price=4, author_name='author2', owner=self.user)

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        data = {
            'like': True,
        }
        data_json = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=data_json,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertTrue(relation.like)

    def test_in_bookmarks(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        data = {
            'in_bookmarks': True,
        }
        data_json = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=data_json, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        data = {'rate': 5}
        data_json = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=data_json, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertEqual(5, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        data = {'rate': 6}
        data_json = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=data_json, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertIsNone(relation.rate)
