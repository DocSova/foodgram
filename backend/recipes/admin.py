from django.contrib import admin
from django.utils.safestring import mark_safe

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
    User,
    ShortLink,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Панель пользователей."""

    list_display = ("id", "username", "email")
    list_filter = ("username", "email")
    list_display_links = ("username",)
    search_fields = ("username", "email")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Панель ингридиентов."""

    list_display = ("id", "name", "measurement_unit")
    list_filter = ("name",)
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Панель тегов."""

    list_display = ("id", "name", "color", "slug")
    list_display_links = ("name",)
    search_fields = ("name", "slug")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Панель корзины."""

    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Панель избранного."""

    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Панель подписок."""

    list_display = ("id", "user", "author")
    list_filter = ("user", "author")
    search_fields = ("user", "author")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Панель рецептов."""

    list_display = ("id", "name", "author", "favorites_count", "recipe_image")
    list_filter = ("name", "author", "tags")
    list_display_links = ("name",)
    search_fields = ("name", "author")
    inlines = (RecipeIngredientInline,)
    readonly_fields = ["favorites_count"]

    @admin.display(description="Добавлено в избранное")
    def favorites_count(self, obj):
        return obj.favorites.count()

    @admin.display(description="Изображение")
    def recipe_image(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width=50")


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    """Панель коротких ссылок."""

    list_display = ("recipe", "short_link", "full_link")
    search_fields = ("recipe",)
