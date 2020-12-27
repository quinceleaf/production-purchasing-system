from django.contrib import admin

from admin_auto_filters.filters import AutocompleteFilter
from django_fsm_log.admin import StateLogInline
from import_export.admin import ImportExportModelAdmin


from apps.core.admin import (
    admin_link,
    BaseAdminConfig,
    ImmutableAdminConfig,
    ManufacturerFilter,
    MaterialFilter,
    ProductFilter,
)
from apps.core.models import ExportCsvMixin
from apps.materials import models
from apps.production import models as production_models
from apps.purchasing import models as purchasing_models
from apps.purchasing.admin import VendorCatalogInline


"""
Admin for following models:
Input
InputCharacteristics
InputInventoryEvent
Manufacturer
Material
MaterialCharacteristics
MaterialCost
MaterialUnit
Product (PROXY)
"""

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ADD-ONS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class InputInline(admin.TabularInline):
    model = models.Input
    extra = 0


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MODELS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# INPUT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class InputAdminConfig(BaseAdminConfig):

    autocomplete_fields = ["manufacturer", "material", "unit"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "category",
                    "state",
                    "version",
                )
            },
        ),
        (
            "Material",
            {
                "fields": (
                    "material",
                    "is_preferred",
                    "unit",
                )
            },
        ),
        (
            "Manufacturer Information",
            {
                "fields": (
                    "manufacturer",
                    "manufacturer_item_number",
                    "pack_size",
                    "pack_total_weight",
                    "pack_total_volume",
                    "pack_total_each",
                )
            },
        ),
        (
            "Notes",
            {"fields": ("notes",)},
        ),
    ) + BaseAdminConfig.readonly_fieldsets

    inlines = (VendorCatalogInline,)
    list_display = ("__str__", "manufacturer")
    list_display_links = ("__str__", "manufacturer")
    list_filter = [ManufacturerFilter, MaterialFilter]
    search_fields = (
        "manufacturer__name",
        "material__name",
        "name",
        "unit__name",
        "unit__symbol",
    )


@admin.register(models.Input)
class InputAdmin(InputAdminConfig):
    pass


@admin.register(models.InputCharacteristics)
class InputCharacteristicsAdmin(BaseAdminConfig):
    pass


@admin.register(models.InputInventoryEvent)
class InputInventoryEventAdmin(ImmutableAdminConfig):
    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MANUFACTURER
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class ManufacturerAdminConfig(BaseAdminConfig):
    def input_count(self, obj):
        return obj.inputs.count()

    fieldsets = (
        (None, {"fields": ("name", "state", "notes")}),
    ) + BaseAdminConfig.readonly_fieldsets

    input_count.short_description = "Input Count"
    # fields = ["name", "state", "notes"]
    inlines = [StateLogInline]
    list_display = ("__str__", "state", "input_count")
    list_filter = ("state",)


@admin.register(models.Manufacturer)
class ManufacturerAdmin(ManufacturerAdminConfig):
    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MATERIAL
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class MaterialAdminConfig(BaseAdminConfig, ExportCsvMixin):
    def input_count(self, obj):
        return obj.inputs.count()

    input_count.short_description = "Input Count"

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Choices for model Material (the differentiating criteria between
        Material and its proxy model Product) should be limited to only material-appropriate options
        """
        if db_field.name == "category":
            kwargs["choices"] = [
                ("RAW", "Raw Material"),
                ("SERVICE", "Service"),
                ("MRO", "Maintenance/Operating Supplies"),
                ("PACKAGING", "Packaging/Disposable"),
                ("OTHER", "Other/Misc"),
            ]
        return super(MaterialAdminConfig, self).formfield_for_choice_field(
            db_field, request, **kwargs
        )

    actions = ["export_as_csv"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "category",
                    "version",
                    "unit_type",
                    "upc_code",
                    "shelf_life",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = ("__str__", "input_count")
    list_display_links = ("__str__", "input_count")
    list_filter = ("category",)
    search_fields = ["name"]


@admin.register(models.Material)
class MaterialAdmin(MaterialAdminConfig):
    pass


@admin.register(models.MaterialCharacteristics)
class MaterialCharacteristicsAdmin(BaseAdminConfig):
    list_filter = (MaterialFilter,)


@admin.register(models.MaterialCost)
class MaterialCostAdmin(ImmutableAdminConfig):
    list_filter = (MaterialFilter,)


@admin.register(models.MaterialUnit)
class MaterialUnitAdmin(BaseAdminConfig):
    list_filter = (MaterialFilter,)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PRODUCT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class ProductAdminConfig(BaseAdminConfig, ExportCsvMixin):
    def input_count(self, obj):
        return obj.inputs.count()

    input_count.short_description = "Input Count"

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Choices for proxy model Product (the differentiating criteria between
        Product and Material) should be limited to only product-appropriate options
        """
        if db_field.name == "category":
            kwargs["choices"] = [
                ("WIP", "Work-in-Progress"),
                ("FINISHED", "Finished Product"),
            ]
        return super(ProductAdminConfig, self).formfield_for_choice_field(
            db_field, request, **kwargs
        )

    actions = ["export_as_csv"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "category",
                    "version",
                    "unit_type",
                    "upc_code",
                    "shelf_life",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    inlines = (InputInline,)
    list_display = ("__str__", "input_count")
    list_display_links = ("__str__", "input_count")
    list_filter = ("category",)
    search_fields = ["name"]


@admin.register(models.Product)
class ProductAdmin(ProductAdminConfig):
    pass


@admin.register(models.ProductCharacteristics)
class ProductCharacteristicsAdmin(BaseAdminConfig):
    list_filter = (ProductFilter,)


@admin.register(models.ProductCost)
class ProductCostAdmin(ImmutableAdminConfig):
    list_filter = (ProductFilter,)


@admin.register(models.ProductUnit)
class ProductUnitAdmin(BaseAdminConfig):
    list_filter = (ProductFilter,)