from django.contrib import admin

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.admin import BaseAdmin


class RecipeIngredientInline(admin.TabularInline):
    """
    Встроенная административная форма для ингредиентов рецепта.

    Атрибуты:
        model (models.Model): Модель, связанная с встроенной формой.
        extra (int): Количество дополнительных пустых форм.
        min_num (int): Минимальное количество форм.
    """

    model = RecipeIngredient
    extra = 0
    min_num = 1


class TagInline(admin.TabularInline):
    """
    Встроенная административная форма для тэгов рецепта.

    Атрибуты:
        model (models.Model): Модель, связанная с встроенной формой.
        extra (int): Количество дополнительных пустых форм.
        min_num (int): Минимальное количество форм.
    """

    model = Recipe.tags.through
    extra = 0
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    """
    Класс административной панели для модели Ingredient.

    Атрибуты:
        inlines (tuple): Встроенные формы, связанные с моделью.
        list_display (tuple): Поля, отображаемые в списке записей.
        list_filter (tuple): Поля, доступные для фильтрации списка.
        search_fields (tuple): Поля, по которым можно выполнять поиск.
    """

    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    """
    Класс административной панели для модели Tag.

    Атрибуты:
        list_display (tuple): Поля, отображаемые в списке записей.
        search_fields (tuple): Поля, по которым можно выполнять поиск.
        list_filter (tuple): Поля, доступные для фильтрации списка.
    """

    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color')
    list_filter = ('name', 'color')


@admin.register(Recipe)
class RecipeAdmin(BaseAdmin):
    """
    Класс административной панели для модели Recipe.

    Атрибуты:
        inlines (tuple): Встроенные формы, связанные с моделью.
        list_display (tuple): Поля, отображаемые в списке записей.
        search_fields (tuple): Поля, по которым можно выполнять поиск.
        list_filter (tuple): Поля, доступные для фильтрации списка.
    """

    inlines = (RecipeIngredientInline, TagInline)
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
    """
    Класс административной панели для модели ShoppingCart.

    Атрибуты:
        list_display (tuple): Поля, отображаемые в списке записей.
        list_filter (tuple): Поля, доступные для фильтрации списка.
        search_fields (tuple): Поля, по которым можно выполнять поиск.
    """

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user',)


@admin.register(Favorite)
class FavoriteAdmin(BaseAdmin):
    """
    Класс административной панели для модели Favorite.

    Атрибуты:
        list_display (tuple): Поля, отображаемые в списке записей.
        list_filter (tuple): Поля, доступные для фильтрации списка.
        search_fields (tuple): Поля, по которым можно выполнять поиск.
    """

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user',)
