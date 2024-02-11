from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from api.constants import USER_VALID_MESSAGE, USERNAME_NOT_ME_ERR_MESSAGE


def username_not_me_validator(value):
    if value.lower() == 'me':
        raise ValidationError(USERNAME_NOT_ME_ERR_MESSAGE)


username_symbols_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message=USER_VALID_MESSAGE
)
