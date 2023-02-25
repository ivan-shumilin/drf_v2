"""
self.book_1.refresh_from_db()
def setUp(self):
response = self.client.get(url)
response = self.client.post(url, data=data_json, content_type="application/json")
self.client.force_login(self.user)
"""

import json

from django.contrib.auth.models import User
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from store.models import Book
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


    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        expended = BookSerializers([self.book_1, self.book_2], many=True).data
        self.assertEqual(expended, response.data)


    def test_get_one_obj(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        expended = BookSerializers(self.book_1).data
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

