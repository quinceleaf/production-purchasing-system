from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.core import converters
from apps.purchasing import views

register_converter(converters.ULIDConverter, "ulid")

app_name = "apps.purchasing"


vendor_urls = [
    path("<ulid:pk>/edit/", views.VendorUpdateView.as_view(), name="vendor_edit"),
    path("<ulid:pk>/", views.VendorDetailView.as_view(), name="vendor_detail"),
    path("add/", views.VendorCreateView.as_view(), name="vendor_add"),
    path("list/", views.VendorListView.as_view(), name="vendor_list"),
]


urlpatterns = [
    path("vendors/", include(vendor_urls)),
]
