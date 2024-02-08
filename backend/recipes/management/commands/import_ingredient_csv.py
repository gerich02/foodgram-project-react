import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Команда для импорта данных об ингредиентах из CSV файла в базу данных.

    Attributes:
        help (str): Справочное сообщение о назначении команды.
    """

    help = 'Ипорт данных из csv файла в бд'

    def handle(self, *args, **kwargs):
        with open('data/ingredients.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name = row[0]

                measurement_unit = row[1] if len(row) > 1 else None

                ingredient_instance = Ingredient(
                    name=name,
                    measurement_unit=measurement_unit,
                )
                ingredient_instance.save()

        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))