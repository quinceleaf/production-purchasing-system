# ––– DJANGO IMPORTS
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver, Signal


# ––– PYTHON UTILITY IMPORTS
import datetime as dt


# –––THIRD-PARTY IMPORTS
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by


# ––– PROJECT IMPORTS
from apps.core import models as core_models
from apps.materials import models as materials_models


# ––– PARAMETERS


# ––– SIGNALS


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# CLIENT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Client(core_models.AbstractBaseModel):

    STATE_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("PAST_DUE", "Account Past Due"),
        ("INACTIVE", "Inactive"),
    )

    name = models.CharField("Name", max_length=64, null=False)
    notes = models.TextField("Notes", null=True, blank=True)
    state = FSMField(
        default="PENDING",
        verbose_name="Status",
        choices=STATE_CHOICES,
        # protected=True,
    )

    def __str__(self):
        return f"{self.name}"

    # States:
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # PENDING (Default) - client has not been approved for accepting sales or production
    # APPROVED - client can place orders for production/orders can be placed for client
    # PAST DUE - client account is past due and no further orders can be accepted for client until resolved
    # INACTIVE - client (account in good standing) is dormant and is longer allowed to place orders until review

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="APPROVED",
        permission="apps.sales.change_client_status",
    )
    def approve(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="APPROVED",
        target="PAST_DUE",
        permission="apps.sales.change_client_status",
    )
    def set_past_due(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="INACTIVE",
        permission="apps.sales.change_client_status",
    )
    def set_inactive(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="PENDING",
        permission="apps.sales.change_client_status",
    )
    def set_pending(self, by=None):
        return

    class Meta:
        ordering = [
            "name",
        ]
        permissions = [("change_client_status", "Can change status of client")]


class ClientLocation(core_models.AbstractBaseModel):
    LOCATION_TYPE_CHOICES = [
        ("RETAIL", "Retail Location"),
        ("RDC", "Distribution Center"),
        ("CORPORATE", "Corporate Offices"),
        ("ACCOUNTING", "Accounting Dept"),
    ]

    name = models.CharField("Name", max_length=64, null=False)

    location_type = models.CharField(
        "Location Type", max_length=16, choices=LOCATION_TYPE_CHOICES, default="RDC"
    )

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="locations"
    )

    served_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="distributes_to",
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = [
            "location_type",
            "name",
        ]


class ClientPreference(core_models.AbstractBaseModel):
    LOCATION_TYPE_CHOICES = [
        ("LOCATION", "This Location"),
        ("RDC", "Distribution Center"),
        ("CORPORATE", "Corporate Offices"),
        ("ACCOUNTING", "Accounting Dept"),
    ]

    deliver_to_preference = models.CharField(
        "Deliver Product to",
        max_length=16,
        choices=LOCATION_TYPE_CHOICES,
        default="RDC",
    )
    bill_to_preference = models.CharField(
        "Direct Invoices to",
        max_length=16,
        choices=LOCATION_TYPE_CHOICES,
        default="CORPORATE",
    )

    client = models.OneToOneField(
        Client, on_delete=models.CASCADE, related_name="preferences"
    )

    def __str__(self):
        return f"{self.client} preference"


class ClientLocationAddress(core_models.AbstractBaseModel):

    STATE_CHOICES = [
        ("AL", "Alabama "),
        ("AK", "Alaska "),
        ("AZ", "Arizona "),
        ("AR", "Arkansas "),
        ("CA", "California "),
        ("CO", "Colorado "),
        ("CT", "Connecticut "),
        ("DE", "Delaware "),
        ("FL", "Florida "),
        ("GA", "Georgia "),
        ("HI", "Hawaii "),
        ("ID", "Idaho "),
        ("IL", "Illinois "),
        ("IN", "Indiana "),
        ("IA", "Iowa "),
        ("KS", "Kansas "),
        ("KY", "Kentucky "),
        ("LA", "Louisiana "),
        ("ME", "Maine "),
        ("MD", "Maryland "),
        ("MA", "Massachusetts "),
        ("MI", "Michigan "),
        ("MN", "Minnesota "),
        ("MS", "Mississippi "),
        ("MO", "Missouri "),
        ("MT", "Montana "),
        ("NE", "Nebraska "),
        ("NV", "Nevada "),
        ("NH", "New Hampshire "),
        ("NJ", "New Jersey "),
        ("NM", "New Mexico "),
        ("NY", "New York "),
        ("NC", "North Carolina "),
        ("ND", "North Dakota "),
        ("OH", "Ohio "),
        ("OK", "Oklahoma "),
        ("OR", "Oregon "),
        ("PA", "Pennsylvania "),
        ("RI", "Rhode Island "),
        ("SC", "South Carolina "),
        ("SD", "South Dakota "),
        ("TN", "Tennessee "),
        ("TX", "Texas "),
        ("UT", "Utah "),
        ("VT", "Vermont "),
        ("VA", "Virginia "),
        ("WA", "Washington "),
        ("WV", "West Virginia "),
        ("WI", "Wisconsin "),
        ("WY", "Wyoming "),
    ]

    address_line_1 = models.CharField(
        "Address Line 1", max_length=64, null=True, blank=True
    )
    address_line_2 = models.CharField(
        "Address Line 2", max_length=64, null=True, blank=True
    )
    address_line_3 = models.CharField(
        "Address Line 1", max_length=64, null=True, blank=True
    )
    address_city = models.CharField("City", max_length=32, null=True, blank=True)
    address_state = models.CharField(
        "State",
        max_length=2,
        choices=STATE_CHOICES,
        default="NY",
        null=False,
        blank=False,
    )
    address_zipcode = models.CharField("Zipcode", max_length=10, null=True, blank=True)
    notes = models.TextField("Notes", null=True, blank=True)

    location = models.OneToOneField(
        ClientLocation, on_delete=models.CASCADE, related_name="address"
    )

    def __str__(self):
        return str(self.location.name)

    class Meta:
        verbose_name_plural = "Client location addresses"


class ClientContact(core_models.AbstractBaseModel):

    PREFERRED_METHOD_CHOICES = [
        ("MOBILE", "via Mobile"),
        ("TELEPHONE", "via Telephone"),
        ("FAX", "via Fax"),
        ("EMAIL", "via Email"),
    ]

    name = models.CharField("Name", max_length=64, null=False, blank=False)
    preferred_method = models.CharField(
        "Preferred Contact Method",
        max_length=9,
        choices=PREFERRED_METHOD_CHOICES,
        default="MOBILE",
    )
    contact_mobile = models.CharField("Mobile", max_length=64, null=True, blank=True)
    contact_telephone = models.CharField(
        "Office Tel.", max_length=64, null=True, blank=True
    )
    contact_fax = models.CharField("Fax", max_length=64, null=True, blank=True)
    contact_email = models.EmailField("Email", null=True, blank=True)
    notes = models.TextField("Notes", null=True, blank=True)

    location = models.ForeignKey(
        ClientLocation, on_delete=models.CASCADE, related_name="contacts"
    )

    def __str__(self):
        return str(self.name)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# DELIVERY METHOD
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def default_cutoff_time():
    return dt.time(14, 0)
    # return UTC_TZ.localize(start_time)


class DeliveryMethod(core_models.AbstractBaseModel):
    name = models.CharField("Service", max_length=24, null=False, blank=False)
    lead_time = models.PositiveIntegerField(default=0)
    cutoff_time = models.TimeField(
        auto_now=False,
        auto_now_add=False,
        default=default_cutoff_time,
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.name)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SALES
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def increment_invoice_id():
    # arbitrary starting number of 2800; adjust as necessary
    from apps.sales.models import SaleOrder

    prefix = "INV-"
    last_sale = SaleOrder.objects.all().order_by("invoice_id").last()
    if not last_sale:
        return str(prefix) + "2800"
    prior_id = last_sale.invoice_id
    invoice_id_int = int(prior_id[4:])
    invoice_id_int += 1
    new_invoice_id = str(prefix) + str(invoice_id_int).zfill(4)
    return new_invoice_id


class SaleOrder(core_models.AbstractBaseModel):

    STATE_CHOICES = (
        ("PENDING", "Pending"),
        ("CANCELLED", "Cancelled"),
        ("CANCELLED_PENALTY", "Cancelled Late (Penalty)"),
        ("RELEASED", "Released for Production"),
        ("COMMITTED", "Committed for Production"),
        ("FULFILLED", "Fulfilled"),
        ("FULFILLED_SHORT", "Fulfilled (product short/complaint)"),
    )

    invoice_id = models.CharField(
        "Invoice Number",
        max_length=8,
        default=increment_invoice_id,
        null=False,
        unique=True,
        editable=False,
    )
    date = models.DateTimeField(
        "Date placed", default=dt.date.today
    )  # auto_now_add=True)
    date_delivery_scheduled = models.DateField(
        "Scheduled Delivery Date", null=False, blank=False
    )
    date_order_release = models.DateField("Order Release Date", null=True, blank=True)
    date_delivery_actual = models.DateField(
        "Actual Delivery Date", null=True, blank=True
    )
    notes = models.TextField("Notes", null=True, blank=True)
    state = FSMField(
        default="PENDING",
        verbose_name="Status",
        choices=STATE_CHOICES,
        # protected=True,
    )

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="sale_orders"
    )
    delivery_method = models.ForeignKey(
        DeliveryMethod,
        on_delete=models.CASCADE,
        related_name="sale_orders",
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        ClientLocation, on_delete=models.CASCADE, related_name="sale_orders"
    )

    def __str__(self):
        return f"{self.client} | {self.location} | {self.invoice_id} | delivery {self.date_delivery_scheduled.strftime('%Y-%m-%d')}"

    # States:
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # PENDING (Default) - standing order or order-in-progress with sales
    # CANCELLED - order cancelled prior to production commitment (without penalty)
    # CANCELLED_LATE - order cancelled after production commitment (penalty to be assessed)
    # RELEASED - order released to production but not yet committed or fulfilled
    # COMMITTED - order committed (produced or ingredients purchased)
    # FULFILLED - order delivered and complete
    # FULFILLED_SHORT - order delivered, but client claims short or other complaint

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="PENDING",
        permission="apps.sales.change_sales_order_status",
    )
    def set_pending(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source=["PENDING", "RELEASED", "CANCELLED_LATE"],
        target="CANCELLED",
        permission="apps.sales.change_sales_order_status",
    )
    def cancel(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source=["COMMITTED", "CANCELLED"],
        target="CANCELLED_LATE",
        permission="apps.sales.change_sales_order_status",
    )
    def cancel_late(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source=["PENDING", "CANCELLED", "CANCELLED_LATE"],
        target="RELEASED",
        permission="apps.sales.change_sales_order_status",
    )
    def release(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source=["RELEASED"],
        target="COMMITTED",
        permission="apps.sales.change_sales_order_status",
    )
    def commit(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source=["COMMITTED", "FULFILLED_SHORT"],
        target="FULFILLED",
        permission="apps.sales.change_sales_order_status",
    )
    def fulfilled(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source=["COMMITTED", "FULFILLED"],
        target="FULFILLED_SHORT",
        permission="apps.sales.change_sales_order_status",
    )
    def fulfilled_short(self, by=None):
        return

    class Meta:
        get_latest_by = ["date"]
        ordering = ["date_delivery_scheduled"]
        permissions = [
            ("change_sales_order_status", "Can change status of sales order")
        ]


class SaleOrderLine(core_models.AbstractBaseModel):

    quantity = models.PositiveSmallIntegerField("Quantity", default=0)

    material = models.ForeignKey(
        materials_models.Material,
        on_delete=models.CASCADE,
        related_name="sales_order_lines",
    )
    sale_order = models.ForeignKey(
        SaleOrder, on_delete=models.CASCADE, related_name="lines"
    )
    unit = models.ForeignKey(
        core_models.UnitMeasurement, on_delete=models.CASCADE, related_name="+"
    )

    def __str__(self):
        return f"{self.sale_order.client.name} | {self.sale_order.invoice_id} | {self.material.name}"


@receiver(pre_save, sender=SaleOrder)
def set_sale_order_release_date(sender, instance, **kwargs):
    """
    Offset order release date based on delivery leadtime to location
    """
    from apps.sales.operations import (
        calculate_valid_delivery_methods,
    )

    # TODO: Use zipcode set in SiteSettings
    facility_zipcode = "10474"

    shipping_method = calculate_valid_delivery_methods(
        facility_zipcode, instance.location.address.address_zipcode
    )
    if shipping_method:
        delivery_method = DeliveryMethod.objects.get(name=shipping_method[1])
        instance.delivery_method = delivery_method
        # if dt.timezone.now()
        instance.date_order_release = instance.date_delivery_scheduled - dt.timedelta(
            days=delivery_method.lead_time
        )
