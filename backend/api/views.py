from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from djoser.views import UserViewSet

from recipes.models import Ingredient, Tag, Recipe
from users.models import CustomUser, Follow
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeCreateSerializer,
    UserInfoSerializer,
    SubscriptionsSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели пользователя."""

    queryset = CustomUser.objects.all()
    serializer_class = UserInfoSerializer
    pagination_class = LimitOffsetPagination

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Функция подписки на пользователя."""
        user = request.user
        author = get_object_or_404(CustomUser, id=self.kwargs.get('id'))
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, following=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = get_object_or_404(Follow,
                                         user=user,
                                         following=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        """Функция выдачи пользователей, на которых подписан автор запроса."""
        user = request.user
        subscribers = CustomUser.objects.filter(follower__user=user)
        pages = self.paginate_queryset(subscribers)
        serializer = SubscriptionsSerializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)
