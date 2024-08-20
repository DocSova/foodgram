from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet,
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    UserSubscriptionsViewSet,
    UserSubscriptionView,
)

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path(
        "users/subscriptions/",
        UserSubscriptionsViewSet.as_view({"get": "list"}),
    ),
    path(
        "users/<int:user_id>/subscribe/",
        UserSubscriptionView.as_view(),
    ),
    path(
        "users/me/avatar/",
        CustomUserViewSet.as_view({"put": "avatar"})
    ),
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
