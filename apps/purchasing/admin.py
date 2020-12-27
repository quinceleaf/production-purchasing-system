from django.contrib import admin

# Register your models here.
from django.contrib import admin

from admin_auto_filters.filters import AutocompleteFilter
from django_fsm_log.admin import StateLogInline
from import_export.admin import ImportExportModelAdmin

from apps.purchasing import models
from apps.core.admin import admin_link, BaseAdminConfig, MaterialFilter


"""
Admin for following models:
Vendor
VendorCatalog
VendorOrder
VendorOrderLine
"""


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ADD-ONS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class VendorCatalogInline(admin.TabularInline):
    model = models.VendorCatalog
    extra = 0


class VendorOrderLineInline(admin.TabularInline):
    model = models.VendorOrderLine
    extra = 0


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MODELS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# VENDOR
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class VendorAdminConfig(BaseAdminConfig):
    def input_count(self, obj):
        return obj.inputs.count()

    input_count.short_description = "Input Count"

    def order_count(self, obj):
        return obj.vendor_orders.count()

    order_count.short_description = "Order Count"

    fieldsets = (
        (
            None,
            {"fields": ("name", "state", "terms")},
        ),
        (
            "Notes",
            {"fields": ("notes",)},
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    inlines = (VendorCatalogInline,)

    list_display = (
        "__str__",
        "input_count",
        "order_count",
    )
    search_fields = [
        "name",
    ]


@admin.register(models.Vendor)
class VendorAdmin(VendorAdminConfig):
    pass


class VendorCatalogAdminConfig(BaseAdminConfig):
    def most_recent_price_value(self, obj):
        return models.VendorOrderLine.objects.get(
            input=obj.input, vendor_order__vendor=obj.vendor
        )

    most_recent_price_value.short_description = "Most Recent Price"

    list_display = ("input", "vendor", "vendor_item_number")
    sortable_by = ("input", "vendor", "vendor_item_number")
    list_display_links = ("input", "vendor")
    list_filter = ("vendor",)


@admin.register(models.VendorCatalog)
class VendorCatalogAdmin(VendorCatalogAdminConfig):
    pass


class VendorOrderAdminConfig(BaseAdminConfig):

    inlines = (VendorOrderLineInline,)

    list_display = (
        "__str__",
        "date",
        "date_delivery_scheduled",
        "total_cost",
        "purchasing_reference",
        "invoice_id",
    )
    sortable_by = (
        "__str__",
        "purchasing_reference",
        "invoice_id",
    )
    list_filter = ("vendor",)
    autocomplete_fields = [
        "vendor",
    ]


@admin.register(models.VendorOrder)
class VendorOrderAdmin(VendorOrderAdminConfig):
    pass


class VendorOrderLineAdminConfig(BaseAdminConfig):
    def order(self, obj):
        return obj.vendor_order

    order.short_description = "Order"

    def vendor(self, obj):
        return obj.vendor_order.vendor

    vendor.short_description = "Vendor"

    list_display = ("__str__", "order")
    list_display_links = ("__str__", "order")


@admin.register(models.VendorOrderLine)
class VendorOrderLineAdmin(VendorOrderLineAdminConfig):
    pass