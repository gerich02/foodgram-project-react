from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.constants import (MAX_COOKING_TIME, MAX_INGREDIENT_AMOUNT,
                           MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT,
                           MIN_INGREDIENT_REQUIRED, MIN_TAG_REQUIRED)
from api.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UserInfoSerializer(UserCreateSerializer):
    """Сериализатор для получения информации о пользователе."""

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and request.user.follower.filter(following=obj).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов в рецепте."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT, message='Минимум: '
                              f'{MIN_INGREDIENT_AMOUNT} единица'),
            MaxValueValidator(MAX_INGREDIENT_AMOUNT, message='Максимум: '
                              f'{MAX_INGREDIENT_AMOUNT} единиц')
        ]
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError('Ингредиент не существует')
        return value


class SubscriptionSerializer(UserInfoSerializer):
    """Сериализатор для получения информации о подписках."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = (
            *UserInfoSerializer.Meta.fields,
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes_queryset = obj.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
            recipes_queryset = recipes_queryset[:recipes_limit]
        else:
            recipes_limit = None
        serializer = SpecialRecipeSerializer(
            recipes_queryset,
            many=True,
            context=self.context
        )
        return serializer.data


class SubscriptionDataSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки/отмены подписки на пользователя."""

    class Meta:
        model = Follow
        fields = (
            'user',
            'following'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Нельзя подписаться на автора дважды'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data.get('following'):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data

    def to_representation(self, instance):
        serializer = SubscriptionSerializer(
            instance.following,
            context=self.context
        )
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeDetailSerializer(serializers.ModelSerializer):
    author = UserInfoSerializer(
        read_only=True,
    )
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'image',
            'author',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_ingredients(self, obj):
        return obj.ingredients.annotate(
            amount=Sum('recipe_ingredients__amount')
        ).values(
            'id', 'name', 'amount', 'measurement_unit'
        )

    def get_is_favorited(self, obj):
        context_user = self.context.get('request').user
        return (
            context_user
            and context_user.is_authenticated
            and context_user.favorites.filter(
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        context_user = self.context.get('request').user
        return (
            context_user
            and context_user.is_authenticated
            and context_user.shopping_cart_recipe.filter(
                recipe=obj
            ).exists()
        )


class SpecialRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(
        help_text='Название рецепта'
    )
    image = Base64ImageField(
        read_only=True,
        help_text='Изображение рецепта в Base64'
    )
    cooking_time = serializers.ReadOnlyField(
        help_text='Время готовки в минутах'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time',
            'image'
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепта для создания и обновления рецепта."""

    author = UserInfoSerializer(read_only=True)
    ingredients = IngredientInRecipeCreateSerializer(
        many=True
    )
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise ValidationError(
                'Необходимо указать минимум '
                f'{MIN_INGREDIENT_REQUIRED} ингредиент'
            )
        ingredient_ids = [ingredient.get('id') for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError('Ингредиенты уже были добавлены в рецепт')
        tags = data.get('tags', [])
        if not tags:
            raise ValidationError(
                f'Необходимо указать хотя бы {MIN_TAG_REQUIRED} тег'
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги не должны повторяться')
        image = data.get('image')
        if not image:
            raise serializers.ValidationError('Добавьте изображение')
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient_data in ingredients:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
            )
        return instance

    def to_representation(self, instance):
        return RecipeDetailSerializer(instance, context=self.context).data


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'user',
            'recipe',
        )

    def validate_recipe(self, value):
        try:
            Recipe.objects.get(id=value.id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError('Такого рецепта не существует')
        return value

    def to_representation(self, instance):
        return SpecialRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')},
        ).data


class FavoriteSerializer(FavoriteShoppingCartSerializer):

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже был добавлен',
            ),
        ]


class ShoppingCartSerializer(FavoriteShoppingCartSerializer):

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже был добавлен',
            ),
        ]
