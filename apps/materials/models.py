# ––– DJANGO IMPORTS
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver, Signal


# ––– PYTHON UTILITY IMPORTS


# –––THIRD-PARTY IMPORTS
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by


# ––– PROJECT IMPORTS
from apps.core import models as core_models


# ––– PARAMETERS


# ––– MODELS


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# INPUTS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Input(core_models.AbstractBaseModel):

    STATE_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("DISQUALIFIED", "Disqualifed"),
        ("NAN", "No Approval Necessary"),
    )

    INVENTORY_CATEGORY_CHOICES = [
        ("RAW", "Raw Material"),
        ("MRO", "Maintenance/Operating Supplies"),
        ("PACKAGING", "Packaging/Disposable"),
        ("OTHER", "Other/Misc"),
    ]

    name = models.CharField("Name", max_length=96, null=False)
    category = models.CharField(
        "Category",
        max_length=32,
        choices=INVENTORY_CATEGORY_CHOICES,
        null=False,
        default="RAW",
    )
    manufacturer_item_number = models.CharField(
        "Manufacturer Item Number", max_length=32, null=True, blank=True
    )
    pack_size = models.PositiveSmallIntegerField(default=1)
    pack_total_weight = models.DecimalField(
        "Pack total, weight (std)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    pack_total_volume = models.DecimalField(
        "Pack total, volume (std)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    pack_total_each = models.PositiveSmallIntegerField("Pack total, each", default=0)
    notes = models.TextField("Notes", null=True, blank=True)
    version = models.PositiveSmallIntegerField(default=1)
    is_preferred = models.BooleanField(default=False)
    state = FSMField(
        default="PENDING",
        verbose_name="Status",
        choices=STATE_CHOICES,
        # protected=True,
    )

    manufacturer = models.ForeignKey(
        "Manufacturer", on_delete=models.CASCADE, related_name="inputs"
    )
    material = models.ForeignKey(
        "Material", on_delete=models.CASCADE, related_name="inputs"
    )
    unit = models.ForeignKey(
        core_models.UnitMeasurement,
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Default Unit of Measurement (UOM)",
    )

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.is_preferred:
            return super(Input, self).save(*args, **kwargs)
        with transaction.atomic():
            Input.objects.filter(
                material_id=self.material_id, is_preferred=True
            ).update(is_preferred=False)
            return super(Input, self).save(*args, **kwargs)

    # States:
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # PENDING (Default) - input has not been evaluated for allergens
    # APPROVED - input has allergen matrix completed and, if not base input, has ingredient statement entered
    # DISQUALIFIED - input violates one or more constraints for production (allergen, preference, religious restrictions)
    # NO APPROVAL NEEDED - input is category MRO/PACKAGING/SERVICE or otherwise does not need evaluation for allergens
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Inputs PENDING or DISQUALIFIED cannot be added to vendor orders
    # Inputs transitioning to PENDING or DISQUALIFIED will trigger blocks on recipes/BOMs containing their corresponding materials
    # Inputs transitioning to PENDING or DISQUALIFIED will be removed from production area and will not be used for production

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="APPROVED",
        permission="app.change_input_status",
    )
    def approve(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="DISQUALIFIED",
        permission="app.change_input_status",
    )
    def disqualify(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="NAN",
        permission="app.change_input_status",
    )
    def no_approval_needed(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="PENDING",
        permission="app.change_input_status",
    )
    def set_pending(self, by=None):
        return

    class Meta:
        get_latest_by = ["version"]
        ordering = ["name"]
        permissions = [
            ("change_input_status", "Can change status of input"),
        ]


class InputCharacteristics(core_models.AbstractBaseModel):
    characteristics = models.JSONField("Characteristics")
    version = models.PositiveSmallIntegerField(default=1)

    input = models.ForeignKey(
        Input, on_delete=models.CASCADE, related_name="characteristics"
    )

    def __str__(self):
        return f"{self.input.name} | characteristics"

    class Meta:
        get_latest_by = [
            "version",
        ]
        verbose_name_plural = "Input characteristics"


class InputInventoryEvent(core_models.InventoryEvent):

    input = models.ForeignKey(
        Input, on_delete=models.CASCADE, related_name="inventory_events"
    )

    def __str__(self):
        return f"{self.input.name} | inventory event"


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MANUFACTURER
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Manufacturer(core_models.AbstractBaseModel):

    STATE_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("DISQUALIFIED", "Disqualifed"),
        ("NAN", "No Approval Necessary"),
        ("LAPSED", "Lapsed"),
    )

    name = models.CharField("Name", max_length=96, null=False)
    notes = models.TextField("Notes", null=True, blank=True)
    state = FSMField(
        default="PENDING",
        verbose_name="Status",
        choices=STATE_CHOICES,
        # protected=True,
    )

    def __str__(self):
        return str(self.name)

    def get_fields(self):
        return [
            (field.name, field.value_to_string(self))
            for field in Manufacturer._meta.fields
        ]

    # States:
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # PENDING (Default) - manufacturer has not been evaluated per SVP and certifications or other assurance credentials have not been provided
    # APPROVED - manufacturer has provided certifications or other assurance credentials per SVP
    # DISQUALIFIED - manufacturer has been found to be unable to comply with necessary assurances per SVP
    # NO APPROVAL NEEDED - manufacturer produces inputs/provides services that are outside the scope of SVP
    # LAPSED - manufacturer has failed to submit renewed certifications or other assurance credentials per SVP
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Inputs from Manufacturers who are PENDING, LAPSED or DISQUALIFIED cannot be ordered from Vendors and will not appear in picklists
    # Inputs from Manufacturers transitioning to PENDING, LAPSED or DISQUALIFIED will be removed from production area and will not be used for production
    # Materials transitioning to PENDING or DISQUALIFIED will trigger blocks on recipes/BOMs containing them

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="APPROVED",
        permission="app.change_manufacturer_status",
    )
    def approve(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="DISQUALIFIED",
        permission="app.change_manufacturer_status",
    )
    def disqualify(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="NAN",
        permission="app.change_manufacturer_status",
    )
    def no_approval_needed(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="PENDING",
        permission="app.change_manufacturer_status",
    )
    def set_pending(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="LAPSED",
        permission="app.change_manufacturer_status",
    )
    def lapsed(self, by=None):
        return

    class Meta:
        get_latest_by = ["version"]
        ordering = ["name"]
        permissions = [
            ("change_manufacturer_status", "Can change status of manufacturer"),
        ]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MATERIAL
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Material(core_models.AbstractBaseModel):
    # WIP/FINISHED/SERVICE materials will have Recipe (BOM)

    UNIT_TYPE_CHOICES = (
        ("WEIGHT", "Weight"),
        ("VOLUME", "Volume"),
        ("EACH", "Each"),
        ("MISC", "Miscellaneous"),
        ("INVENTORY", "Inventory"),
    )

    INVENTORY_CATEGORY_CHOICES = [
        ("RAW", "Raw Material"),
        ("WIP", "Work-in-Progress"),
        ("FINISHED", "Finished Product"),
        ("SERVICE", "Service"),
        ("MRO", "Maintenance/Operating Supplies"),
        ("PACKAGING", "Packaging/Disposable"),
        ("OTHER", "Other/Misc"),
    ]

    name = models.CharField("Name", max_length=96, null=False)
    category = models.CharField(
        "Category",
        max_length=32,
        choices=INVENTORY_CATEGORY_CHOICES,
        null=False,
        default="RAW",
    )
    notes = models.TextField("Notes", null=True, blank=True)
    unit_type = models.CharField(
        "Unit Type",
        max_length=32,
        choices=UNIT_TYPE_CHOICES,
        null=False,
        default="WEIGHT",
    )
    upc_code = models.CharField(
        "UPC Code", max_length=12, null=True, blank=True
    )  # GTIN-12/UPC-A
    shelf_life = models.PositiveIntegerField("Shelf Life", default=0)
    version = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.name}"

    def calculate_cost_direct():
        pass

    def calculate_cost_naive():
        cost_point = self.inputs.all()

    def calculate_cost_cumulative():
        pass

    def calculate_cost_ma3():
        pass

    def calculate_cost_ma5():
        pass

    def calculate_cost_ma7():
        pass

    def calculate_cost_exp():
        pass

    class Meta:
        ordering = ["name"]
        get_latest_by = ["version"]


def generate_characteristics():
    return [{}]


class MaterialCharacteristics(core_models.AbstractBaseModel):
    # if category RAW/WIP/FINISHED must have allergen matrix (and ingredient statement, if appropriate)

    STATE_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("DISQUALIFIED", "Disqualifed"),
        ("NAN", "No Approved Necessary"),
    )

    characteristics = models.JSONField(
        "Characteristics", default=generate_characteristics
    )
    version = models.PositiveSmallIntegerField(default=1)
    state = FSMField(
        default="PENDING",
        verbose_name="Status",
        choices=STATE_CHOICES,
        # protected=True,
    )

    material = models.OneToOneField(
        Material, on_delete=models.CASCADE, related_name="characteristics"
    )

    def __str__(self):
        return f"{self.material.name} | characteristics"

    # States:
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # PENDING (Default) - material has not been evaluated for allergens
    # APPROVED - material has allergen matrix completed and, if not base material, has ingredient statement entered
    # DISQUALIFIED - material violates one or more constraints for production (allergen, preference, religious restrictions)
    # NO APPROVAL NEEDED - material is category MRO/PACKAGING/SERVICE or otherwise does not need evaluation for allergens
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Materials PENDING or DISQUALIFIED cannot be added to recipe/BOM
    # Materials transitioning to PENDING or DISQUALIFIED will trigger blocks on recipes/BOMs containing them

    @transition(field=state, source="*", target="APPROVED")
    def approved(self):
        return

    @transition(field=state, source="*", target="DISQUALIFIED")
    def disqualify(self):
        return

    @transition(field=state, source="*", target="NAN")
    def no_approval_needed(self):
        return

    @transition(field=state, source="*", target="PENDING")
    def set_pending(self):
        return

    class Meta:
        get_latest_by = ["version"]
        verbose_name_plural = "Material characteristics"


class MaterialUnit(core_models.AbstractBaseModel):

    allowed_weight = models.BooleanField(default=True)
    allowed_volume = models.BooleanField(default=False)
    allowed_each = models.BooleanField(default=False)
    ratio_weight_to_volume = models.DecimalField(
        "Ratio of weight to volume, (standardized)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    ratio_weight_to_each = models.DecimalField(
        "Ratio of weight to each, (standardized)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    ratio_volume_to_each = models.DecimalField(
        "Ratio of volume to each, (standardized)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    version = models.PositiveSmallIntegerField(default=1)

    material = models.OneToOneField(
        Material, on_delete=models.CASCADE, related_name="permitted_units"
    )

    def __str__(self):
        return f"{self.material.name} | permitted units"

    class Meta:
        ordering = ["material"]
        get_latest_by = ["version"]


class MaterialCost(core_models.ImmutableBaseModel):

    BASIS_CHOICES = [
        ("DIRECT", "Directly Assigned"),
        ("CALCULATED", "Calculated"),
        ("NAIVE", "Naïve"),
        ("CUMULATIVE", "Cumulative"),
        ("MA3", "Moving Average (3)"),
        ("MA5", "Moving Average (5)"),
        ("MA7", "Moving Average (5)"),
        ("EXP", "Exponential Smoothing"),
    ]

    unit_cost_weight = models.DecimalField(
        "Cost per unit, weight, (standardized)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    unit_cost_volume = models.DecimalField(
        "Cost per unit, volume (standardized)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    unit_cost_each = models.DecimalField(
        "Cost per each",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    basis = models.CharField(
        "Assignment basis", max_length=24, choices=BASIS_CHOICES, default="DIRECT"
    )

    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name="costs"
    )

    def __str__(self):
        return f"{self.material.name} | {self.created_at} assigned cost"

    class Meta:
        ordering = ["material", "created_at"]
        get_latest_by = ["created_at"]


@receiver(post_save, sender=Material)
def create_related_on_material_creation(sender, created, instance, **kwargs):
    """
    Create related objects upon Material instance create
    """
    from apps.materials.models import (
        MaterialCharacteristics,
        MaterialCost,
        MaterialUnit,
    )

    if created:
        MaterialCharacteristics.objects.create(material=instance)
        MaterialCost.objects.create(material=instance)
        MaterialUnit.objects.create(material=instance)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PRODUCTS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

""" 
Products are proxy model of Materials
Products have category of WIP or FINISHED

"""


class ProductManager(models.Manager):
    def get_queryset(self):
        return (
            super(ProductManager, self)
            .get_queryset()
            .filter(Q(category="WIP") | Q(category="FINISHED"))
        )


class Product(Material):
    objects = ProductManager()

    class Meta:
        proxy = True


class ProductCharacteristicsManager(models.Manager):
    def get_queryset(self):
        return (
            super(ProductCharacteristicsManager, self)
            .get_queryset()
            .filter(Q(material__category="WIP") | Q(material__category="FINISHED"))
        )


class ProductCharacteristics(MaterialCharacteristics):
    # if category RAW/WIP/FINISHED must have allergen matrix (and ingredient statement, if appropriate)

    objects = ProductCharacteristicsManager()

    class Meta:
        proxy = True


class ProductUnitManager(models.Manager):
    def get_queryset(self):
        return (
            super(ProductUnitManager, self)
            .get_queryset()
            .filter(Q(material__category="WIP") | Q(material__category="FINISHED"))
        )


class ProductUnit(MaterialUnit):
    # if category RAW/WIP/FINISHED must have allergen matrix (and ingredient statement, if appropriate)

    objects = ProductUnitManager()

    class Meta:
        proxy = True


class ProductCostManager(models.Manager):
    def get_queryset(self):
        return (
            super(ProductCostManager, self)
            .get_queryset()
            .filter(Q(material__category="WIP") | Q(material__category="FINISHED"))
        )


class ProductCost(MaterialCost):
    # if category RAW/WIP/FINISHED must have allergen matrix (and ingredient statement, if appropriate)

    objects = ProductCostManager()

    class Meta:
        proxy = True
