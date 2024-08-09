import re

from django.core.exceptions import ValidationError

from recipes.constants import USER_READ_EDIT_URL


def username_validator(value):
    regex = r"^[\w.@+-]+\Z"
    if re.search(regex, value) is None:
        invalid_characters = set(re.findall(r"[^\w.@+-]", value))
        raise ValidationError(
            (
                f"Недопустимые символы {invalid_characters} в username. "
                f"username может содержать только буквы, цифры и "
                f"знаки @/./+/-/_."
            ),
        )

    if value.lower() == USER_READ_EDIT_URL:
        raise ValidationError(
            f"Использовать имя <{USER_READ_EDIT_URL}> в качестве "
            f"username запрещено."
        )


def color_validator(value):
    regex = r"^#([A-Fa-f0-9]{6})$"
    if not re.match(regex, value):
        raise ValidationError(
            "Поле должно содержать HEX-код цвета в формате #RRGGBB"
        )
