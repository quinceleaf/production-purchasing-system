from django.contrib import admin

from admin_auto_filters.filters import AutocompleteFilter
from django_fsm_log.admin import StateLogInline
from import_export.admin import ImportExportModelAdmin

from apps.core.admin import admin_link, BaseAdminConfig, MaterialFilter
from apps.materials import models as materials_models
from apps.production import models


"""
Admin for following models:
BillOfMaterials
BillOfMaterialsCharacteristics
BillOfMaterialsLine
BillOfMaterialsNote
BillOfMaterialsProcedure
BillOfMaterialsYield
Team
"""


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ADD-ONS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class BillOfMaterialsCharacteristicsInline(admin.TabularInline):
    model = models.BillOfMaterialsCharacteristics
    extra = 0


class BillOfMaterialsLineInline(admin.TabularInline):
    model = models.BillOfMaterialsLine
    extra = 0


class BillOfMaterialsProcedureInline(admin.TabularInline):
    model = models.BillOfMaterialsProcedure
    extra = 0


class BillOfMaterialsYieldInline(admin.TabularInline):
    model = models.BillOfMaterialsYield
    extra = 0


class InputInline(admin.TabularInline):
    model = materials_models.Input
    extra = 0


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MODELS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# BILL OF MATERIALS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class BillOfMaterialsAdminConfig(BaseAdminConfig):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "material":
            kwargs["queryset"] = materials_models.Product.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    autocomplete_fields = ["material", "team"]
    fieldsets = (
        (
            None,
            {"fields": ("material", "state", "version", "team")},
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    inlines = (
        BillOfMaterialsCharacteristicsInline,
        BillOfMaterialsLineInline,
        BillOfMaterialsProcedureInline,
        BillOfMaterialsYieldInline,
        StateLogInline,
    )
    list_display = ("__str__", "version", "state")
    list_filter = ("state", "team", MaterialFilter)
    readonly_fields = [
        "version",
    ] + BaseAdminConfig.readonly_fields


@admin.register(models.BillOfMaterials)
class BillOfMaterialsAdmin(BillOfMaterialsAdminConfig):
    pass


class BillOfMaterialsCharacteristicsAdminConfig(BaseAdminConfig):
    fieldsets = (
        (
            None,
            {"fields": ("bill_of_materials",)},
        ),
        (
            "Production",
            {
                "fields": (
                    "temperature_preparation",
                    "temperature_storage",
                    "temperature_service",
                    "notes_production",
                )
            },
        ),
        (
            "Labor",
            {
                "fields": (
                    "total_active_time",
                    "total_inactive_time",
                    "staff_count",
                    "notes_labor",
                )
            },
        ),
    )
    raw_id_fields = ("bill_of_materials",)
    search_fields = ("bill_of_materials__name",)


@admin.register(models.BillOfMaterialsCharacteristics)
class BillOfMaterialsCharacteristicsAdmin(BillOfMaterialsCharacteristicsAdminConfig):
    pass


class BillOfMaterialsLineAdminConfig(BaseAdminConfig):
    autocomplete_fields = ["material", "unit"]
    list_display = ("__str__", "bill_of_materials")
    list_display_links = ("__str__", "bill_of_materials")
    search_fields = ["material", "unit", "bill_of_materials"]


@admin.register(models.BillOfMaterialsLine)
class BillOfMaterialsLineAdmin(BillOfMaterialsLineAdminConfig):
    pass


class BillOfMaterialsNoteAdminConfig(BaseAdminConfig):
    search_fields = ("bill_of_materials__name",)


@admin.register(models.BillOfMaterialsNote)
class BillOfMaterialsNoteAdmin(BillOfMaterialsNoteAdminConfig):
    pass


class BillOfMaterialsProcedureAdminConfig(BaseAdminConfig):
    search_fields = ("bill_of_materials__name",)


@admin.register(models.BillOfMaterialsProcedure)
class BillOfMaterialsProcedureAdmin(BillOfMaterialsProcedureAdminConfig):
    pass


class BillOfMaterialsYieldAdminConfig(BaseAdminConfig):
    search_fields = ("bill_of_materials__name",)


@admin.register(models.BillOfMaterialsYield)
class BillOfMaterialsYieldAdmin(BillOfMaterialsYieldAdminConfig):
    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TEAM
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.Team)
class TeamAdmin(BaseAdminConfig):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    search_fields = ("name",)
