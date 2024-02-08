import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Ипорт данных из csv файла в бд'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к CSV файлу')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        with open(file_path, 'r', encoding='utf-8') as file:
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