"""
self.book_1.refresh_from_db()
def setUp(self):
response = self.client.get(url)
response = self.client.post(url, data=data_json, content_type="application/json")
self.client.force_login(self.user)
"""

import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from store.models import Book, UserBookRelations
from store.serializers import BookSerializers


class SubscriptionsApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user2 = User.objects.create(username='test_user2')
        self.user_is_staff = User.objects.create(username='test_admin', is_staff=True)
        self.book_1 = Book.objects.create(name='Book One', price='1000',
                                          author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Book One', price='1000',
                                          author_name='Author 2', owner=self.user2)
        UserBookRelations.objects.create(user=self.user, book=self.book_1, like=True, rate=3)
        UserBookRelations.objects.create(user=self.user2, book=self.book_2, like=True, rate=3)


    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1))))
        expended = BookSerializers(books, many=True).data
        self.assertEqual(expended, response.data)
        self.assertEqual(expended[0]['annotated_likes'], 1)
        self.assertEqual(expended[0]['rating'], '3.00')



    def test_get_one_obj(self):
        url = reverse('book-detail', args=(self.book_2.id,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1))))
        book = books.get(id=self.book_2.id)
        expended = BookSerializers(book).data
        self.assertEqual(expended, response.data)

    def test_create(self):
        self.assertEqual(2, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            'name': 'Book 3',
            'price': '1000',
            'author_name': 'Author 3'
        }
        data_json = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)



    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': 'Book 1',
            'price': 2000,
            'author_name': 'Author 1',
        }
        data_json = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(2000, self.book_1.price)


    def test_update_not_owner(self):
        url = reverse('book-detail', args=(self.book_2.id,))
        data = {
            'name': 'Book 2',
            'price': 2000,
            'author_name': 'Author 2',
        }
        data_json = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, response.data)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')}, response.data)
        self.book_1.refresh_from_db()
        self.assertEqual(1000, self.book_1.price)


    def test_updata_is_staff(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': 'Book 1',
            'price': 2000,
            'author_name': 'Author 1',
        }
        data_json = json.dumps(data)
        self.client.force_login(self.user_is_staff)
        response = self.client.put(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(2000, self.book_1.price)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, Book.objects.filter(id=self.book_1.id).count())


    def test_delete_not_owner(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')}, response.data)
        self.assertEqual(1, Book.objects.filter(id=self.book_1.id).count())


    def test_delete_is_staff(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_is_staff)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, Book.objects.filter(id=self.book_1.id).count())


class UserBookRelationsTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='test_user1')
        self.user2 = User.objects.create(username='test_user2')
        # self.user_is_staff = User.objects.create(username='test_admin', is_staff=True)
        self.book_1 = Book.objects.create(name='Book One', price='1000',
                                          author_name='Author 1')
        self.book_2 = Book.objects.create(name='Book One', price='1000',
                                          author_name='Author 2')


    def test_like_and_in_bookmakrs(self):
        url = reverse('userbookrelations-detail', args=(self.book_1.id,))
        self.client.force_login(self.user1)
        data = {
            'like': True
        }
        data_json = json.dumps(data)
        response = self.client.patch(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relations = UserBookRelations.objects.get(user=self.user1, book=self.book_1)
        self.assertTrue(relations.like)
        data = {
            'in_bookmarks': True
        }
        data_json = json.dumps(data)
        response = self.client.patch(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relations = UserBookRelations.objects.get(user=self.user1, book=self.book_1)
        self.assertTrue(relations.in_bookmarks)


    def test_rate(self):
        url = reverse('userbookrelations-detail', args=(self.book_2.id,))
        self.client.force_login(self.user2)
        data = {
            'rate': 4,
        }
        data_json = json.dumps(data)
        response = self.client.patch(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        relations = UserBookRelations.objects.get(user=self.user2, book=self.book_2)
        self.assertEqual(4, relations.rate)


    def test_rate_wrong(self):
        url = reverse('userbookrelations-detail', args=(self.book_2.id,))
        self.client.force_login(self.user2)
        data = {
            'rate': 9,
        }
        data_json = json.dumps(data)
        response = self.client.patch(url, data=data_json, content_type="application/json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
        self.assertEqual({'rate': [ErrorDetail(string='"9" is not a valid choice.', code='invalid_choice')]}, response.data)