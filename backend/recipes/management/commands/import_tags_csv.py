import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    """
    Команда для импорта данных о тэгах из CSV файла в базу данных.

    Attributes:
        help (str): Справочное сообщение о назначении команды.
    """

    help = 'Ипорт данных из csv файла в бд'

    def handle(self, *args, **kwargs):
        with open('data/tags.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name = row[0],
                color = row[1],
                slug = row[2] if len(row) > 2 else None

                ingredient_instance = Tag(
                    name=name,
                    color=color,
                    slug=slug
                )
                ingredient_instance.save()

        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))
