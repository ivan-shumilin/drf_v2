from django.contrib import admin
from store.models import Book, UserBookRelations


admin.site.register(Book)
admin.site.register(UserBookRelations)


