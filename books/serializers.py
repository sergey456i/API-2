from rest_framework import serializers
from .models import Book, Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        write_only=True,
        source='author'
    )

    class Meta:
        model = Book
        fields = '__all__'
        extra_kwargs = {
            'cover_image': {'required': False},
            'file': {'required': False}
        }

    def validate(self, data):
        if data.get('category') == 'textbook':
            existing = Book.objects.filter(
                title=data['title'],
                author=data['author'],
                publisher=data['publisher'],
                year=data['year'],
                category='textbook'
            )
        else:
            existing = Book.objects.filter(
                title=data['title'],
                author=data['author'],
                publisher=data['publisher'],
                category='fiction'
            )

        if existing.exists() and not self.instance:
            raise serializers.ValidationError(
                "Книга с такими параметрами уже существует в соответствии с правилами уникальности."
            )
        return data