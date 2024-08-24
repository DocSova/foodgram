from django.shortcuts import get_object_or_404, redirect

from recipes.models import ShortLink


def redirect_link(request, short_link):
    """Метод переадресации ссылок."""

    print(short_link)

    link = get_object_or_404(
        ShortLink,
        short_link=short_link
    )
    return redirect(link.full_link)
