from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(FilterSet):
    """Фильтр для модели рецептов"""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'tags', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(
                shopping_cart_recipe__user=self.request.user
            )
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр для модели ингредиентов"""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
