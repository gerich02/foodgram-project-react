from django.contrib.auth.models import AbstractUser
from django.db import models

from api.constants import USERS_NAME_EMAIL_PASS_MAX_LENGTH
from users.validators import (username_not_me_validator,
                              username_symbols_validator)


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField('Электронная почта', unique=True)
    username = models.CharField(
        'Никнейм',
        max_length=USERS_NAME_EMAIL_PASS_MAX_LENGTH,
        unique=True,
        validators=[
            username_symbols_validator,
            username_not_me_validator
        ]
    )
    first_name = models.CharField(
        'Имя',
        max_length=USERS_NAME_EMAIL_PASS_MAX_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=USERS_NAME_EMAIL_PASS_MAX_LENGTH
    )
    password = models.CharField(
        'Пароль',
        max_length=USERS_NAME_EMAIL_PASS_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='prevent_self_follow'
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            f'Пользователь {self.user} подписан'
            f'на {self.following}'
        )
