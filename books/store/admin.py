from django.contrib import admin

from books.store.models import Book, UserBookRelation


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(UserBookRelation)
class BookAdmin(admin.ModelAdmin):
    pass
