from rest_framework import viewsets 
from djoser.views import UserViewSet
from recipes.models import Ingredient, Tag
from users.models import CustomUser
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    CustomUserSerializer,
    UserRegistrationSerializer
)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer