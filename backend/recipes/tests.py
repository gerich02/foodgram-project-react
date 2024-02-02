from django.test import TestCase
from recipes.models import Ingredient


class IngredientModelTestCase(TestCase):

    def setUp(self) -> None:
        self.ingredient = Ingredient.objects.create(
            name='Кровь джуна',
            measurement_unit='мл'
        )

    def test_update_ingredient(self):
        self.ingredient.name = 'Молоко единорога'
        self.ingredient.measurement_unit = 'ml'
        self.assertEqual(self.ingredient.name, 'Молоко единорога')
        self.assertEqual(self.ingredient.measurement_unit, 'ml')

    def test_delete_ingredient(self):
        self.ingredient.delete()