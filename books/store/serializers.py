from rest_framework.serializers import ModelSerializer
from store.models import Book


class BookSerializers(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'