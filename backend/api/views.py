from django.db.models import F, Sum
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import HttpResponse, get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeGetSerializer,
    ShoppingCartSerializer,
    TagGetSerializer,
    UserSubscribeRepresentSerializer,
    UserSubscribeSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
    User,
    RecipeIngredient,
)


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецепта."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeGetSerializer
        return RecipeCreateUpdateSerializer

    def recipe_process(self, request, recipe, model, serializer, error_text):
        if request.method == "POST":
            new_item, created = model.objects.get_or_create(
                user=request.user, recipe=recipe)
            if not created:
                return Response(
                    {'detail': error_text},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(
                new_item,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            old_item = get_object_or_404(
                model,
                user=request.user,
                recipe=recipe
            )
            old_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.recipe_process(
            request,
            recipe,
            Favorite,
            FavoriteSerializer,
            'Рецепт уже добавлен в избранное.'
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        return self.recipe_process(
            request,
            recipe,
            ShoppingCart,
            ShoppingCartSerializer,
            'Рецепт уже добавлен в список покупок.'
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        recipes = Recipe.objects.filter(carts__user=request.user)
        shopping_cart = RecipeIngredient.objects.filter(
            recipe__in=recipes
        ).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).order_by('ingredient__name').annotate(ing_amount=Sum('amount'))

        text = 'Список покупок: \n\n'

        for recipe in shopping_cart:
            text += (
                f'{recipe["name"]}: '
                f'{recipe["ing_amount"]}/{recipe["measurement_unit"]}.\n'
            )

        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment;'
            'filename="shopping_cart.txt"'
        )
        return response


class CustomUserViewSet(DjoserUserViewSet):
    """Вьюсет Пользователя."""

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user_data = self.get_serializer(request.user)
        return Response(user_data.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            user_instance = self.get_object()
        except Http404:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        user_data = self.get_serializer(user_instance)
        return Response(user_data.data)

    @action(
        detail=False,
        methods=["PUT"],
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        user_data = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        user_data.is_valid(raise_exception=True)
        user_data.save()
        return Response(user_data.data)


class UserSubscriptionView(APIView):
    """Подписка на пользователя."""

    permission_classes = (IsAdminAuthorOrReadOnly,)

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        subscription_data = UserSubscribeSerializer(
            data={"user": request.user.id, "author": author.id},
            context={"request": request},
        )
        subscription_data.is_valid(raise_exception=True)
        subscription_data.save()
        return Response(subscription_data.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        subscription = request.user.follower.filter(author=author)
        if not subscription:
            return Response(
                {"error": "Нет подписки на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет всех подписок на пользователей."""

    serializer_class = UserSubscribeRepresentSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class TagViewSet(ModelViewSet):
    """Вьюсет тега."""

    http_method_names = ["get"]
    queryset = Tag.objects.all()
    serializer_class = TagGetSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    """Вьюсет ингредиента."""

    http_method_names = ["get"]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
