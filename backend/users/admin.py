from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.constants import PAGE_LIMIT
from users.models import CustomUser, Follow


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_per_page = PAGE_LIMIT


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
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
    list_display = (
        'user',
        'following',
    )
    list_filter = ('user', 'following',)
    search_fields = ('user__username', 'following__username',)
    ordering = ('user',)
