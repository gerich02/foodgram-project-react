from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from djoser.views import UserViewSet
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from recipes.models import Ingredient, Tag, Recipe
from users.models import CustomUser, Follow
from .permissions import IsAdminOrOwner
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeCreateSerializer,
    UserCreateSerializer,
    UserInfoSerializer,
    SubscriptionsSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели пользователя."""
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination
    
    def get_serializer_class(self):
        """Функция получения нужного сериализатора."""
        if self.request.method == 'GET':
            return UserInfoSerializer
        return UserCreateSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
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
            permission_classes=[IsAuthenticated])
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
