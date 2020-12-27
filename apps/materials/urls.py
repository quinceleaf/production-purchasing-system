from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.core import converters
from apps.materials import views

register_converter(converters.ULIDConverter, "ulid")

app_name = "apps.materials"


input_urls = [
    path("<ulid:pk>/edit/", views.InputUpdateView.as_view(), name="input_edit"),
    path("<ulid:pk>/", views.InputDetailView.as_view(), name="input_detail"),
    path("add/", views.InputCreateView.as_view(), name="input_add"),
    path("list/", views.InputListView.as_view(), name="input_list"),
]

manufacturer_urls = [
    path(
        "<ulid:pk>/edit/",
        views.ManufacturerUpdateView.as_view(),
        name="manufacturer_edit",
    ),
    path(
        "<ulid:pk>/", views.ManufacturerDetailView.as_view(), name="manufacturer_detail"
    ),
    path("add/", views.ManufacturerCreateView.as_view(), name="manufacturer_add"),
    path("list/", views.ManufacturerListView.as_view(), name="manufacturer_list"),
]

material_urls = [
    path("<ulid:pk>/edit/", views.MaterialUpdateView.as_view(), name="material_edit"),
    path("<ulid:pk>/", views.MaterialDetailView.as_view(), name="material_detail"),
    path("add/", views.MaterialCreateView.as_view(), name="material_add"),
    path("list/", views.MaterialListView.as_view(), name="material_list"),
]

product_urls = [
    path("<ulid:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("<ulid:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("add/", views.ProductCreateView.as_view(), name="product_add"),
    path("list/", views.ProductListView.as_view(), name="product_list"),
]


urlpatterns = [
    path("inputs/", include(input_urls)),
    path("manufacturers/", include(manufacturer_urls)),
    path("materials/", include(material_urls)),
    path("products/", include(product_urls)),
]
