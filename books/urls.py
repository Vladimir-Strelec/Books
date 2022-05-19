from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from books.store.views import BookViewSet, BookRelationView

router = SimpleRouter()
router.register(r'book', BookViewSet)
router.register(r'book/relation', BookRelationView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
    path('api-auth/', include('rest_framework.urls')),
    path('api-auth/github/', include('books.store.urls')),

]

urlpatterns += router.urls
