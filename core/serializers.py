# from rest_framework import serializers
# from core.models import Book

# class BookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Book
#         fields = ["slug", "title", "author", "genre", "description", "rating", "cover_image"]

# core/serializers.py
from rest_framework import serializers
from core.models import Book

class BookSerializer(serializers.ModelSerializer):
    genre = serializers.StringRelatedField()  # 👈 important fix

    class Meta:
        model = Book
        fields = [
            "slug", "title", "author", "rating", "genre", "description",
            "price", "available", "publisher", "language", "pages",
            "stock", "cover_image", "published_date", "isbn"
        ]
