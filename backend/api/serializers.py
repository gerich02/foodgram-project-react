import base64

import webcolors
from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.constants import (MAX_INGREDIENT_AMOUNT,
                           MIN_INGREDIENT_AMOUNT,
                           MIN_INGREDIENT_REQUIRED,
                           MIN_TAG_REQUIRED)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import CustomUser, Follow


class Base64ImageField(serializers.ImageField):
    """Класс для загрузки изображений в формате base64."""

    def to_internal_value(self, data):

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    """Класс для преобразования цвета в формате HEX в имя цвета."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тега."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


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


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = CustomUser
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
        model = CustomUser
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


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепта."""

    tags = TagSerializer(read_only=True, many=True)
    author = UserInfoSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = (
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, obj):
        return obj.ingredients.annotate(
            amount=Sum('recipe_ingredients__amount')
        ).values(
            'id',
            'name',
            'amount',
            'measurement_unit'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart_recipe.filter(recipe=obj).exists()
        return False

    def validate(self, data):
        user = self.context.get('request').user
        if user.is_anonymous:
            raise AuthenticationFailed(
                "Требуется аутентификация для выполнения этого действия"
            )
        tags_ids = self.initial_data.get('tags')
        if not tags_ids:
            raise ValidationError(
                f'Необходимо указать хотя бы {MIN_TAG_REQUIRED} тег'
            )
        if len(tags_ids) != len(set(tags_ids)):
            raise ValidationError('Теги не должны повторяться')
        if not Tag.objects.filter(id__in=tags_ids).exists():
            raise ValidationError(
                'Один или несколько указанных тегов не существуют'
            )
        tags = Tag.objects.filter(id__in=tags_ids)
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError(
                'Необходимо указать минимум '
                f'{MIN_INGREDIENT_REQUIRED} ингредиент'
            )
        ingredient_ids = [ingredient.get('id') for ingredient in ingredients]
        if not Ingredient.objects.filter(pk__in=ingredient_ids).exists():
            raise ValidationError(
                'Один или несколько указанных ингредиентов не существуют'
            )
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError('Ингредиенты уже были добавлены в рецепт')
        valid_ingredients = {}
        for ingredient in ingredients:
            valid_ingredients[ingredient['id']] = int(ingredient['amount'])
            if int(ingredient['amount']) <= 0:
                raise ValidationError(
                    'Количество ингредиента должно быть больше нуля'
                )
        ingredient_objects = Ingredient.objects.filter(
            pk__in=valid_ingredients.keys()
        )
        for ingredient_object in ingredient_objects:
            valid_ingredients[ingredient_object.pk] = (
                ingredient_object, valid_ingredients[ingredient_object.pk])
        data.update({
            'tags': tags,
            'ingredients': valid_ingredients,
            'author': self.context.get('request').user
        })
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=ingredient_data,
                recipe=recipe,
                amount=amount
            ) for ingredient_data, amount in ingredients.values()])
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=ingredient_data,
                recipe=instance,
                amount=amount
            ) for ingredient_data, amount in ingredients.values()])
        instance.save()
        return instance


class SpecialRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное и корзину."""

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


class SubscriptionSerializer(UserInfoSerializer):
    """Сериализатор для получения информации о подписках."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = CustomUser
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
