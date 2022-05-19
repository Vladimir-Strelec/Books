from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from books.store.models import Book, UserBookRelation


class BookSerializer(ModelSerializer):
    like_count = serializers.SerializerMethodField()
    annotated_like = serializers.IntegerField(read_only=True)
    mid_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name', 'like_count', 'annotated_like', 'mid_rate')

    def get_like_count(self, instance):
        return UserBookRelation.objects.filter(book=instance, like=True).count()


class BookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rate')


