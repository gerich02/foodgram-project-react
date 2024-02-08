from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.constants import (MAX_COOKING_TIME, MAX_INGREDIENT_AMOUNT,
                           MAX_LENGTH_COLOR, MAX_LENGTH_NAME_AND_SLUG,
                           MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT)

User = get_user_model()


class Tag(models.Model):
    """Модель для хранения тегов рецептов."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME_AND_SLUG,
        verbose_name='Название',
        unique=True
    )
    color = models.CharField(
        max_length=MAX_LENGTH_COLOR,
        verbose_name='Цвет в HEX',
        unique=True
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_NAME_AND_SLUG,
        verbose_name='Уникальный слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для хранения ингредиентов."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME_AND_SLUG,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_NAME_AND_SLUG,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель для хранения рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор')
    name = models.CharField(
        max_length=MAX_LENGTH_NAME_AND_SLUG,
        verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Текст')
    image = models.ImageField(
        upload_to='images/',
        null=True,
        default=None,
        verbose_name='Изображение'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    slug = models.SlugField(verbose_name='Слаг')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    cooking_time = models.PositiveIntegerField(
        'Длительность приготовления',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message='Минимальное значение должно быть не менее '
                f'{MIN_COOKING_TIME} минуты'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message='Максимальное значение должно быть не более '
                f'{MAX_COOKING_TIME} минут'
            ),
        ]
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для хранения ингредиентов в рецепте."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message='Минимальное количество не менее '
                f'{MIN_INGREDIENT_AMOUNT}'
            ),
            MaxValueValidator(
                999,
                message='Максимальное количество не более '
                f'{MAX_INGREDIENT_AMOUNT}'
            ),
        ]
    )

    class Meta:
        verbose_name = 'количество ингредиента в рецепте'
        verbose_name_plural = 'количество ингредиентов в рецепте'
        default_related_name = 'recipe_ingredients'


class Favorite(models.Model):
    """Модель для хранения избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в избранном'
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite_recipe'
            )
        ]

    def __str__(self):
        return (
            f'{self.user} добавил рецепт {self.recipe} в избранное '
        )


class ShoppingCart(models.Model):
    """Модель для хранения рецептов в списке покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в списке покупок'
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        default_related_name = 'shopping_cart_recipe'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shopping_cart_recipe'
            )
        ]

    def __str__(self):
        return (
            f'{self.user} добавил рецепт {self.recipe} в список покупок '
        )
