import csv

from django.core.management.base import BaseCommand
from tqdm import tqdm

from api.constants import TAG_DATA_ROUTE
from recipes.models import Tag


class Command(BaseCommand):
    """
    Команда для импорта данных о тэгах из CSV файла в базу данных.

    Attributes:
        help (str): Справочное сообщение о назначении команды.
    """

    help = 'Импорт данных из csv файла в бд'

    def handle(self, *args, **kwargs):
        # Подсчет количества строк в файле
        with open(TAG_DATA_ROUTE, encoding='utf-8') as file:
            num_lines = sum(1 for line in file)

        # Открытие файла снова для чтения данных и импорта
        with open(TAG_DATA_ROUTE, encoding='utf-8') as file:
            reader = csv.reader(file)
            # Использование tqdm с флагом total
            for row in tqdm(
                reader,
                total=num_lines,
                ncols=80,
                ascii=True,
                desc='Total'
            ):
                name = row[0]
                color = row[1]
                slug = row[2] if len(row) > 2 else None

                existing_tag = Tag.objects.filter(name=name).exists()
                if not existing_tag:
                    tag_instance = Tag(
                        name=name,
                        color=color,
                        slug=slug
                    )
                    tag_instance.save()

        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))
