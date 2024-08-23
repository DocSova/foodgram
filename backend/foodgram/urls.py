from django.contrib import admin
from django.urls import include, path

from api.helpers import redirect_link


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("s/<short_link>/", redirect_link, name="redirect_link"),
]
