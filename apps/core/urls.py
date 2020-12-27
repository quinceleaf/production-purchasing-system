from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.core import converters, views

register_converter(converters.ULIDConverter, "ulid")
app_name = "apps.core"

urlpatterns = [
    path(
        "settings/<str:model>/<str:filter_field>/<str:filter_value>/",
        views.change_list_filter_settings,
        name="list_filter_settings",
    ),
    path("", views.IndexView.as_view(), name="index"),
]
