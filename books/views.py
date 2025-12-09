from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['genre', 'category']
    search_fields = ['title', 'author__name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [ReadOnly]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [ReadOnly]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]