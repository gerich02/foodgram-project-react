# Generated by Django 3.2.3 on 2024-02-07 11:42

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0005_auto_20240206_1711'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Favourite',
            new_name='Favorite',
        ),
    ]
