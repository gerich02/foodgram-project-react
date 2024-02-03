from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    color = models.CharField(max_length=200, verbose_name='Цвет в HEX')
    slug = models.SlugField(max_length=200, verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'

