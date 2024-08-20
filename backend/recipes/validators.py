import re

from django.core.exceptions import ValidationError

from recipes.constants import USER_READ_EDIT_URL


def validate_color(value):
    pattern = r"^#([A-Fa-f0-9]{6})$"
    if not re.match(pattern, value):
        raise ValidationError(
            "Поле должно содержать HEX-код цвета в формате #RRGGBB"
        )


def validate_username(value):
    if value.lower() == "me":
        raise ValidationError(
            f"Использование имени <me> в качестве username запрещено.")

    if re.search(r"^[\w.@+-]+\Z", value) is None:
        invalid_chars = set(re.findall(r"[^\w.@+-]", value))
        raise ValidationError(f"Недопустимые символы {invalid_chars} в username.")
