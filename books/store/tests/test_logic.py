from django.contrib.auth.models import User
from django.test import TestCase

from store.logic import set_rating
from store.models import UserBookRelations, Book


class SetRating(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='test_user1')

        self.book_1 = Book.objects.create(name='Book One', price=1000, author_name='Author 1')

        UserBookRelations.objects.create(user=self.user1, book=self.book_1, like=True, rate=1)
        UserBookRelations.objects.create(user=self.user1, book=self.book_1, like=True, rate=4)
        UserBookRelations.objects.create(user=self.user1, book=self.book_1, like=True, rate=4)

    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual(3.00, self.book_1.rating)
