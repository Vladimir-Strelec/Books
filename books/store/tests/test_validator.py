from django.db.models import Count, Case, When, Avg
from django.test.testcases import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from books.store.models import valid_name, Book, valid_price
from books.store.serializers import BookSerializer


class ValidatorTestCase(TestCase):
    value = 'Test gf'

    def test_validator_valid_name(self):
        self.assertIsNone(valid_name(self.value))


class ValidatorNameTestCase(APITestCase):
    def test_api_valid_name(self):
        book = Book.objects.create(name='test', price=10, author_name='lol')
        url = reverse('book-list')
        response = self.client.get(url).data

        books = Book.objects.all().annotate(annotated_like=Count(Case(When(userbookrelation__book=book, then=1))),
                                            mid_rate=Avg('userbookrelation__rate'))
        serializer = BookSerializer(books, many=True).data
        self.assertEqual(serializer, response)


    def test_validator_valid_rase(self):
        value = '0- '
        with self.assertRaises(Exception) as ex:
            valid_name(value)
        self.assertEqual(str(['Value must contain only letters and']), str(ex.exception))


class PriceValidator(TestCase):
    VALUE1 = 0.4
    VALUE2 = -1.4

    def test_valid_positive_price(self):
        self.assertIsNone(valid_price(self.VALUE1))

    def test_valid_negative_price(self):
        with self.assertRaises(Exception) as ex:
            valid_price(self.VALUE2)
        self.assertEqual(str(['Value cannot be less than or equal to 0']), str(ex.exception))
