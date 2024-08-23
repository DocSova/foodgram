from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from recipes.constants import MIN_VALUE, MAX_VALUE
from recipes.models import (
    User,
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
    Subscription,
)


class UserGetSerializer(UserSerializer):
    """Сериализатор получения информации о пользователе."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )

    def create(self, validated_data):
        avatar_data = validated_data.pop("avatar", None)
        user = super().create(validated_data)
        if avatar_data:
            user.avatar.save(avatar_data.name, avatar_data)
        return user

    def update(self, instance, validated_data):
        avatar_data = validated_data.pop("avatar", None)
        if avatar_data:
            instance.avatar.delete()
            instance.avatar.save(avatar_data.name, avatar_data)
        return super().update(instance, validated_data)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )


class UserSubscribeRepresentSerializer(UserGetSerializer):
    """Сериализатор информации о подписке."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[: int(recipes_limit)]
        return RecipeShortSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )


class UserSignUpSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    class Meta:
        model = Subscription
        fields = "__all__"

    def validate(self, data):
        author = data["author"]
        user = self.context.get("request").user
        is_subscribed = Subscription.objects.filter(
            author=author,
            user=user
        ).exists()
        if (author == user or is_subscribed):
            raise serializers.ValidationError(
                "Нельзя подписаться на этого пользователя!"
            )
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        return UserSubscribeRepresentSerializer(
            instance.author, context={"request": request}
        ).data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""

    name = serializers.StringRelatedField(
        source="ingredient",
        read_only=True,
    )
    measurement_unit = serializers.StringRelatedField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class TagGetSerializer(serializers.ModelSerializer):
    """Сериализатор получения информации о тегах."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор работы с ингредиентами."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор получения информации о рецептах."""

    tags = TagGetSerializer(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source="recipe_ingredients",
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        """Проверить наличие рецепта в избранном."""
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверить наличие рецепта в списке покупок."""
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        )

    class Meta:
        model = Recipe
        fields = "__all__"
        extra_fields = ("is_favorited", "is_in_shopping_cart")
        read_only_fields = ('id', 'author',)


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientPostSerializer(
        many=True,
        source="recipe_ingredients",
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
    )

    def validate(self, data):
        if not self.initial_data.get("tags"):
            raise ValidationError("Рецепт не может быть без тега!")
        if not self.initial_data.get("ingredients"):
            raise ValidationError("Рецепт не может быть без ингредиентов.")
        return data

    def validate_tags(self, tags):
        if len(set(tags)) != len(tags):
            raise ValidationError("Теги должны быть уникальными!")
        return tags

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        for item in ingredients:
            try:
                ingredient = Ingredient.objects.get(id=item["id"])
            except Ingredient.DoesNotExist:
                raise ValidationError("Указанного ингридиента не существует!")

            if ingredient in ingredients_list:
                raise ValidationError("Ингредиенты должны быть уникальными!")

            ingredients_list.append(ingredient)
        return ingredients

    def create_ingredients(self, recipe, ingredients_data):
        new_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item.get("id"),
                amount=item["amount"]
            ) for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(new_ingredients)

    def create(self, validated_data):
        request = self.context.get("request")
        ingredients_data = validated_data.pop("recipe_ingredients")
        tags_data = validated_data.pop("tags")

        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags_data)

        self.create_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("recipe_ingredients")
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.clear()
        instance.tags.set(tags)

        super().update(instance, validated_data)

        self.create_ingredients(instance, ingredients)

        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeShortSerializer(
            instance.recipe,
            context={"request": request}
        ).data

    class Meta:
        model = Favorite
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже добавлен в избранное",
            )
        ]


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже добавлен в список покупок",
            )
        ]
