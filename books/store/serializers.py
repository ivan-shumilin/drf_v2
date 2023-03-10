from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from store.models import Book, UserBookRelations

class BookSerializers(ModelSerializer):
    # likes_count = serializers.SerializerMethodField()
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(source='owner.username', default='',
                                       read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name',
                  'owner', 'annotated_likes', 'rating', 'owner_name')

    # def get_likes_count(self, instance):
    #     return UserBookRelations.objects.filter(book=instance, like=True).count()


class UserBookRelationsSerializers(ModelSerializer):
    class Meta:
        model = UserBookRelations
        fields = '__all__'