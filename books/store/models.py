from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models


def valid_name(value):
    for i in range(len(value)):
        if not value[i].isalnum():
            if not i > 1 and not ord(value[i]) == 32:
                raise ValidationError('Value must contain only letters and')


def valid_price(value):
    if value <= 0:
        raise ValidationError('Value cannot be less than or equal to 0')


class Book(models.Model):
    NAME_MIN_LEN = 2
    name = models.CharField(max_length=100, validators=(MinLengthValidator(NAME_MIN_LEN), valid_name),)
    price = models.DecimalField(max_digits=5, decimal_places=2, validators=(valid_price,))
    author_name = models.CharField(max_length=100, validators=(MinLengthValidator(NAME_MIN_LEN), valid_name),)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='readers_books')

    def __str__(self):
        return f"{self.name}"


class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 'OK'),
        (2, 'FINE'),
        (3, 'GOOD'),
        (4, 'AMAZING'),
        (5, 'INCREDIBLE'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f"{self.user.id} {self.user} {self.book} {self.rate}"
