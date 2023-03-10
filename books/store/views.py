from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from rest_framework import mixins
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from store.models import Book, UserBookRelations
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BookSerializers, UserBookRelationsSerializers


class BookViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1)))
        ).select_related('owner').prefetch_related('readers')
    serializer_class = BookSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filterset_fields = ['price']
    searhs_fields = ['price']
    ordering_fields = ['price']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationsViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelations.objects.all()
    serializer_class = UserBookRelationsSerializers
    lookup_field = 'book'
    def get_object(self):
        obj, _ = UserBookRelations.objects.get_or_create(user=self.request.user,
                                                         book_id=self.kwargs['book'])
        return obj


def auth(request):
    return render(request, 'auth.html', context={})