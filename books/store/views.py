from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from requests import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from books.store.models import Book, UserBookRelation
from books.store.permission import IsOwnerOrIsStaffOrReadOnly
from books.store.serializers import BookSerializer, BookRelationSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(annotated_like=Count(Case(When(userbookrelation__like=True, then=1))),
                                           mid_rate=Avg("userbookrelation__rate")).order_by('id')
    serializer_class = BookSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']

    permission_classes = [IsOwnerOrIsStaffOrReadOnly]


    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


    # authentication_classes = [SessionAuthentication, BasicAuthentication]

class BookRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = BookRelationSerializer
    lookup_field = 'book'


    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(user=self.request.user, book_id=self.kwargs['book'])
        return obj


def auth(request):
    return render(request, 'oauth.html')
