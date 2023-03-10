from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg

from store.serializers import BookSerializers
from django.test import TestCase
from store.models import Book, UserBookRelations


class BookSerializersTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='test_user1')
        self.user2 = User.objects.create(username='test_user2')

        self.book_1 = Book.objects.create(name='Book One', price=1000, author_name='Author 1')
        self.book_2 = Book.objects.create(name='Book Two', price=5000, author_name='Author 2')

        UserBookRelations.objects.create(user=self.user1, book=self.book_1, like=True, rate=4)
        user_book_3 = UserBookRelations.objects.create(user=self.user2, book=self.book_1, like=True)
        user_book_3.rate = 4
        user_book_3.save()


        UserBookRelations.objects.create(user=self.user2, book=self.book_2, like=True, rate=4)
        UserBookRelations.objects.create(user=self.user2, book=self.book_2, like=True, rate=3)
        UserBookRelations.objects.create(user=self.user2, book=self.book_2, like=False)

    def test_ok(self):
        expented = [{
            'id': self.book_1.id,
            'name': 'Book One',
            'price': '1000.00',
            'author_name': 'Author 1',
            'owner': None,
            'annotated_likes': 2,
            'rating': '4.00',
            'owner_name': ''
        },
        {
            'id': self.book_2.id,
            'name': 'Book Two',
            'price': '5000.00',
            'author_name': 'Author 2',
            'owner': None,
            'annotated_likes': 2,
            'rating': '3.50',
            'owner_name': ''
        }]
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1)))).order_by('id')

        result = BookSerializers(books, many=True).data

        self.assertEqual(expented, result, result)

