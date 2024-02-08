from django.contrib import admin

from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipe,
                            ShoppingCart, Tag)
from users.admin import BaseAdmin


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color')
    list_filter = ('name', 'color')


@admin.register(Recipe)
class RecipeAdmin(BaseAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        'name',
        'text',
        'author',
        'pub_date',
        'cooking_time',
        'display_ingredients',
        'favorites_count',
        'display_tags'
    )
    search_fields = ('name', 'author__username', 'favorites_count')
    list_filter = ('name', 'author', 'tags')

    @admin.display(description='Количество добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorites.count()

    @admin.display(description='Отображение ингредиентов')
    def display_ingredients(self, recipe):
        return ', '.join([
            ingredients.name for ingredients in recipe.ingredients.all()])

    @admin.display(description='Теги')
    def display_tags(self, recipe):
        return ', '.join([tags.name for tags in recipe.tags.all()])


@admin.register(ShoppingCart)
class ShoppingCartAdmin(BaseAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user',)


@admin.register(Favorite)
class FavoriteAdmin(BaseAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user',)
