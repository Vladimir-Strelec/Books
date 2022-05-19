from django.urls import path

from books.store.views import auth

urlpatterns = (
    path('auth/', auth),
)
