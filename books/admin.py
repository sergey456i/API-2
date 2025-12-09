from django.contrib import admin
from .models import Author, Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'biography', 'birth_date')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'genre', 'publisher', 'year')
    list_filter = ('category', 'genre', 'year', 'publisher')
    search_fields = ('title', 'author__name', 'genre')
    ordering = ('title', 'year')
    fields = (
        'title',
        'author',
        'year',
        'genre',
        'category',
        'publisher',
        'cover_image',
        'file'
    )
    raw_id_fields = ('author',)