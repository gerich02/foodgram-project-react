from api.filters import IngredientFilter, RecipeFilter
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from users.models import CustomUser, Follow

from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SpecialRecipeSerializer, SubscriptionDataSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserInfoSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели пользователя."""

    queryset = CustomUser.objects.all()
    serializer_class = UserInfoSerializer
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        following = get_object_or_404(
            CustomUser,
            id=self.kwargs.get('id'),
        )
        data = {'user': request.user.id, 'following': following.id}
        serializer = SubscriptionDataSerializer(
            data=data,
            context={'request': request}
        )
        if request.method == 'POST':
            return self.create_subscription(serializer)
        return self.delete_subscription(request.user, following)

    def create_subscription(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_subscription(self, user, following):
        subscription = Follow.objects.filter(
            user=user,
            following=following
        ).first()
        if not subscription:
            return Response(
                {'error': 'Такой подписки не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = CustomUser.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
    
    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = UserInfoSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели рецепта."""

    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer):
        """Функция сохранения пользователя как автора при создании рецепта."""
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        """Функция добавления рецепта в избранное."""
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'errors': 'Такого рецепта не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = SpecialRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = Favorite.objects.filter(user=request.user, recipe__id=pk)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Функция добавления рецепта в продуктовую корзину."""
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'errors': 'Такого рецепта не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = SpecialRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe = get_object_or_404(Recipe, id=pk)
        cart = ShoppingCart.objects.filter(user=request.user, recipe__id=pk)
        if cart.exists():
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """Функция загрузки продуктовой корзины пользователя."""
        if not request.user.shopping_cart_recipe.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')
        shopping_list = ['Список покупок.']
        for ingredient in ingredients:
            shopping_list += [
                f'{ingredient["ingredient__name"]}'
                f'({ingredient["ingredient__measurement_unit"]}):'
                f'{ingredient["amount"]}']
        filename = f'{request.user.username}_shopping_list.txt'
        result_list = '\n'.join(shopping_list)
        response = HttpResponse(result_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
