from django.contrib import admin
from django.urls import include, path

from apps.core import views

autocomplete_patterns = [
    path(
        "autocomplete-input/",
        views.AutocompleteInput.as_view(),
        name="autocomplete-input",
    ),
    path(
        "autocomplete-bill-of-materials/",
        views.AutocompleteBillOfMaterials.as_view(),
        name="autocomplete-bill-of-materials",
    ),
    path(
        "autocomplete-manufacturer/",
        views.AutocompleteManufacturer.as_view(),
        name="autocomplete-manufacturer",
    ),
    path(
        "autocomplete-material/",
        views.AutocompleteMaterial.as_view(),
        name="autocomplete-material",
    ),
    path(
        "autocomplete-material-for-bom/",
        views.AutocompleteMaterialForBOM.as_view(),
        name="autocomplete-material-for-bom",
    ),
    path(
        "autocomplete-product/",
        views.AutocompleteProduct.as_view(),
        name="autocomplete-product",
    ),
    path(
        "autocomplete-team/", views.AutocompleteTeam.as_view(), name="autocomplete-team"
    ),
    path(
        "autocomplete-unit-measurement-each/",
        views.AutocompleteUnitMeasurementEach.as_view(),
        name="autocomplete-unit-measurement-each",
    ),
    path(
        "autocomplete-unit-measurement-volume/",
        views.AutocompleteUnitMeasurementVolume.as_view(),
        name="autocomplete-unit-measurement-volume",
    ),
    path(
        "autocomplete-unit-measurement-weight/",
        views.AutocompleteUnitMeasurementWeight.as_view(),
        name="autocomplete-unit-measurement-weight",
    ),
    path(
        "autocomplete-unit-measurement/",
        views.AutocompleteUnitMeasurement.as_view(),
        name="autocomplete-unit-measurement",
    ),
    path(
        "autocomplete-vendor/",
        views.AutocompleteVendor.as_view(),
        name="autocomplete-vendor",
    ),
]