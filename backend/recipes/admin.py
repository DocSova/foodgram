from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscribe,
    Tag,
    User,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админ-панель пользователей."""

    list_display = ("id", "username", "email")
    search_fields = ("username", "email")
    list_filter = ("username", "email")
    list_display_links = ("username",)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Админ-панель подписок."""

    list_display = ("id", "user", "author")
    search_fields = ("user", "author")
    list_filter = ("user", "author")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-панель тегов."""

    list_display = ("id", "name", "color", "slug")
    search_fields = ("name", "slug")
    list_display_links = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-панель ингридиентов."""

    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)
    list_display_links = ("name",)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель рецептов."""

    list_display = ("id", "name", "author", "favorites_amount", "get_img")
    search_fields = ("name", "author")
    list_filter = ("name", "author", "tags")
    list_display_links = ("name",)
    inlines = (RecipeIngredientInline,)
    readonly_fields = ["favorites_amount"]

    @admin.display(description="Добавлено в избранное")
    def favorites_amount(self, obj):
        return obj.favorites.count()

    @admin.display(description="Изображение")
    def get_img(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width=50")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-панель избранного."""

    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-панель корзины."""

    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
