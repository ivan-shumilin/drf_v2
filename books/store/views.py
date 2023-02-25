from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from store.models import Book
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BookSerializers


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filterset_fields = ['price']
    searhs_fields = ['price']
    ordering_fields = ['price']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


def auth(request):
    return render(request, 'auth.html', context={})