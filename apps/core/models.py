# ––– DJANGO IMPORTS
from django.db import models
from django.http import HttpResponse


# ––– PYTHON UTILITY IMPORTS
import csv


# –––THIRD-PARTY IMPORTS
from simple_history.models import HistoricalRecords
import ulid


# ––– PROJECT IMPORTS


# ––– PARAMETERS


# ––– MODELS


def generate_ulid():
    return str(ulid.ULID())


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class HistoryMixin(models.Model):
    history = HistoricalRecords(inherit=True)

    def get_history(self):
        return_data = []
        all_histories = self.history.all()
        for history in all_histories:
            delta = history.diff_against(history.prev_record)
            for change in delta.changes:
                if change.old:
                    comment = (
                        f"{change.field} changed from {change.old} to {change.new}"
                    )
                else:
                    comment = f"{change.field} set to {change.new}"
            return_data.append(
                {
                    "date": history.history_date,
                    "user": history.history_user,
                    "comment": comment,
                }
            )
        return return_data

    class Meta:
        abstract = True


class AbstractBaseModel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=26,
        default=generate_ulid,
        unique=True,
        blank=True,
        editable=False,
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        abstract = True


class ImmutableBaseModel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=26,
        default=generate_ulid,
        unique=True,
        blank=True,
        editable=False,
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    class Meta:
        abstract = True


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# INVENTORY
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class InventoryEvent(ImmutableBaseModel):

    EVENT_TYPE_CHOICES = [
        ("PRODUCED", "Produced"),  # Positive
        ("PLANNED", "Planned"),  # Positive
        ("ORDERED", "Ordered"),  # Pos (vendor) / Neg (sales)
        ("RECEIVED", "Received"),  # Positive
        ("FULFILLED", "Fulfilled"),  # Negative
        ("ADJUSTED", "Adjusted"),  # Pos / Neg
        ("FORECASTED", "Forecasted"),  # Pos
    ]

    event_type = models.CharField(
        max_length=12, choices=EVENT_TYPE_CHOICES, default="PRODUCED"
    )
    quantity = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        null=False,
        blank=False,
        default=0.000,
    )
    unit = models.ForeignKey(
        "UnitMeasurement", on_delete=models.CASCADE, related_name="+"
    )

    class Meta:
        ordering = ["-id"]
        get_latest_by = ["id"]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# UNIT OF MEASUREMENT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class UnitMeasurement(AbstractBaseModel):
    UNIT_TYPE_CHOICES = (
        ("WEIGHT", "Weight"),
        ("VOLUME", "Volume"),
        ("EACH", "Each"),
        ("MISC", "Miscellaneous"),
        ("INVENTORY", "Inventory"),
    )

    name = models.CharField("Name", max_length=32, null=False, unique=True)
    symbol = models.CharField("Symbol", max_length=9, null=False)
    unit_type = models.CharField(
        "Type", max_length=12, choices=UNIT_TYPE_CHOICES, default="WEIGHT"
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = [
            "unit_type",
            "name",
        ]