from django.shortcuts import get_object_or_404, redirect

from recipes.models import ShortLink


def redirect_link(request, short_link):
    """Метод переадресации ссылок."""

    link = ShortLink.objects.get(
        short_link=short_link
    )
    return redirect(link.full_link)
