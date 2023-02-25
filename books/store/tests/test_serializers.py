from store.serializers import BookSerializers
from django.test import TestCase
from store.models import Book

class BookSerializersTestCase(TestCase):
    def setUp(self):
        self.book_1 = Book.objects.create(name='Book One', price=1000, author_name='Author 1')
        self.book_2 = Book.objects.create(name='Book Two', price=5000, author_name='Author 2')

    def test_ok(self):
        expented = [{
            'id': self.book_1.id,
            'name': 'Book One',
            'price': '1000.00',
            'author_name': 'Author 1',
            'owner': None,
        },
        {
            'id': self.book_2.id,
            'name': 'Book Two',
            'price': '5000.00',
            'author_name': 'Author 2',
            'owner': None,
        }]
        result = BookSerializers([self.book_1, self.book_2], many=True).data
        self.assertEqual(expented, result)


