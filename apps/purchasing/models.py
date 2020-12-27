# ––– DJANGO IMPORTS
from django.db import models, transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver, Signal


# ––– PYTHON UTILITY IMPORTS


# –––THIRD-PARTY IMPORTS
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by


# ––– PROJECT IMPORTS
from apps.core import models as core_models
from apps.materials import models as materials_models


# ––– PARAMETERS


# ––– MODELS


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# VENDORS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Vendor(core_models.AbstractBaseModel):

    STATE_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("DISQUALIFIED", "Disqualifed"),
        ("NAN", "No Approval Necessary"),
        ("LAPSED", "Lapsed"),
    )

    PAYMENT_TERMS_CHOICES = [
        ("NET7", "Net 7 Days"),
        ("NET10", "Net 10 Days"),
        ("NET21", "Net 21 Days"),
        ("NET30", "Net 30 Days"),
        ("EOM", "End-of-Month"),
        ("15MFI", "15th MFI"),
        ("2/10NET30", "Net 30, 2% Disc./Net 10"),
        ("UNSPECIFIED", "Terms Not Specified"),
    ]

    name = models.CharField("Name", max_length=96, null=False)
    terms = models.CharField(
        "Terms",
        max_length=32,
        choices=PAYMENT_TERMS_CHOICES,
        null=False,
        default="UNSPECIFIED",
    )
    notes = models.TextField("Notes", null=True, blank=True)
    state = FSMField(
        default="PENDING",
        verbose_name="Status",
        choices=STATE_CHOICES,
        # protected=True,
    )

    inputs = models.ManyToManyField(
        materials_models.Input, through="VendorCatalog", related_name="vendors"
    )

    def __str__(self):
        return str(self.name)

    # States:
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # PENDING (Default) - vendor has not been evaluated per SVP and certifications or other assurance credentials have not been provided
    # APPROVED - vendor has provided certifications or other assurance credentials per SVP
    # DISQUALIFIED - vendor has been found to be unable to comply with necessary assurances per SVP
    # NO APPROVAL NEEDED - vendor produces inputs/provides services that are outside the scope of SVP
    # LAPSED - vendor has failed to submit renewed certifications or other assurance credentials per SVP
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Vendors who are PENDING, LAPSED or DISQUALIFIED cannot be ordered from and will not appear in picklists

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="APPROVED",
        permission="app.change_vendor_status",
    )
    def approve(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="DISQUALIFIED",
        permission="app.change_vendor_status",
    )
    def disqualify(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="NAN",
        permission="app.change_vendor_status",
    )
    def no_approval_needed(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="PENDING",
        permission="app.change_vendor_status",
    )
    def set_pending(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="LAPSED",
        permission="app.change_vendor_status",
    )
    def lapsed(self, by=None):
        return

    class Meta:
        get_latest_by = ["version"]
        ordering = ["name"]
        permissions = [
            ("change_vendor_status", "Can change status of vendor"),
        ]


class VendorCatalog(core_models.AbstractBaseModel):
    input = models.ForeignKey(
        materials_models.Input,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="catalogs",
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="catalogs",
    )
    vendor_item_number = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.vendor.name} Catalog"

    class Meta:
        get_latest_by = ["input"]


class VendorOrder(core_models.AbstractBaseModel):
    invoice_id = models.CharField(
        "Vendor Invoice Number", max_length=48, null=True, blank=True
    )
    purchasing_reference = models.CharField(
        "Purchasing Reference", max_length=48, null=True, blank=True
    )
    total_cost = models.DecimalField(
        "Invoice Total",
        max_digits=9,
        decimal_places=2,
        null=False,
        blank=False,
        default=0.000,
    )
    date = models.DateTimeField("Date placed", auto_now_add=True)
    date_delivery_scheduled = models.DateTimeField("Scheduled Delivery Date")
    date_delivery_actual = models.DateTimeField("Actual Delivery Date")
    notes = models.TextField("Notes", null=True, blank=True)

    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="vendor_orders"
    )

    def __str__(self):
        return f"{self.vendor.name} order for {self.date_delivery_scheduled.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        total_cost = D(0)
        if self.lines.count() > 0:
            total_cost = self.lines.aggregate(Sum("extension"))["extension__sum"]
        self.total_cost = total_cost
        super(VendorOrder, self).save(*args, **kwargs)

    class Meta:
        ordering = ["-date_delivery_scheduled"]
        get_latest_by = ["date"]


class VendorOrderLine(core_models.AbstractBaseModel):
    quantity = models.PositiveSmallIntegerField("Quantity", default=0)

    unit_price = models.DecimalField(
        "Unit Price",
        max_digits=9,
        decimal_places=2,
        null=False,
        blank=False,
        default=0.000,
    )
    extension = models.DecimalField(
        "Extension",
        max_digits=9,
        decimal_places=2,
        null=False,
        blank=False,
        default=0.000,
    )

    input = models.ForeignKey(
        materials_models.Input, on_delete=models.CASCADE, related_name="lines"
    )
    unit = models.ForeignKey(
        core_models.UnitMeasurement, on_delete=models.CASCADE, related_name="+"
    )
    vendor_order = models.ForeignKey(
        VendorOrder, on_delete=models.CASCADE, related_name="lines"
    )

    def __str__(self):
        return f"{self.vendor_order.vendor.name} order {self.vendor_order.invoice_id} for {self.input.name}"

    def save(self, *args, **kwargs):
        self.extension = self.quantity * self.unit_price
        super(VendorOrderLine, self).save(*args, **kwargs)

    class Meta:
        ordering = ["input"]


@receiver(post_save, sender=VendorOrderLine)
def create_or_update_vendor_order_line(sender, instance, created, **kwargs):
    instance.vendor_order.save()
    return
