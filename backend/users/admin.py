from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.constants import PAGE_LIMIT
from users.models import Follow, User


class BaseAdmin(admin.ModelAdmin):
    """Базовый класс для настроек административного интерфейса."""

    empty_value_display = '-'
    list_per_page = PAGE_LIMIT


@admin.register(User)
class UserAdmin(UserAdmin):
    """Класс для настройки административного интерфейса пользователей."""

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email',)
    ordering = ('username',)


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    """Класс для настройки административного интерфейса подписок."""

    list_display = (
        'user',
        'following',
    )
    list_filter = ('user', 'following',)
    search_fields = ('user__username', 'following__username',)
    ordering = ('user',)
