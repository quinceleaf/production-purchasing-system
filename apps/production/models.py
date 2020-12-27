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
from apps.purchasing import models as purchasing_models


# ––– PARAMETERS


# ––– DJANGO IMPORTS
from django.db import models
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


# ––– SIGNALS
incremented_bill_of_material_version = Signal()


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# BILL OF MATERIALS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class BillOfMaterials(core_models.AbstractBaseModel):

    STATE_CHOICES = (
        ("DRAFT", "Draft"),
        ("AWAITING", "Awaiting Approval"),
        ("RETURNED", "Returned for Revisions"),
        ("APPROVED", "Approved"),
        ("SUPERSEDED", "Superseded"),
        ("INACTIVE", "Inactive"),
    )

    version = models.PositiveSmallIntegerField(default=1)
    state = FSMField(
        default="DRAFT",
        verbose_name="Status",
        choices=STATE_CHOICES,
        # protected=True,
    )

    material = models.ForeignKey(
        materials_models.Material,
        on_delete=models.CASCADE,
        related_name="bills_of_materials",
    )
    team = models.ForeignKey(
        "Team", on_delete=models.CASCADE, related_name="bills_of_materials"
    )

    def __str__(self):
        # return f"version {self.version}"
        return f"{self.material.name} | ver.{self.version}"

    def get_absolute_url(self):
        return str(self.id)

    def get_procedure_english(self):
        return self.procedures.get(language="eng")

    def get_procedure_espagnol(self):
        return self.procedures.get(language="esp")

    def get_procedure_francais(self):
        return self.procedures.get(language="fra")

    # States:
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # DRAFT (Default) - BOM is in development and is not available for sale or production
    # AWAITING APPROVAL - BOM has been submitted for approval and is not available for sale or production
    # RETURNED FOR REVISION - BOM has been returned for further development, is not available for sale or production
    # APPROVED - BOM is approved and may be ordered for sale and produced
    # SUPERSEDED - BOM has been superseded by later version, which may or may not be currently active
    # INACTIVE - previously-approved BOM is currently inactive and is not available for sale or production

    @fsm_log_by
    @transition(
        field=state, source="*", target="DRAFT", permission="app.change_bom_status"
    )
    def set_draft(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source=["DRAFT", "RETURNED"],
        target="AWAITING",
        permission=["app.change_bom_status", "app.submit_bom_for_approval"],
    )
    def submit_for_approval(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="RETURNED",
        permission="app.change_bom_status",
    )
    def return_for_revision(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source=["AWAITING", "INACTIVE"],
        target="APPROVED",
        permission="app.change_bom_status",
    )
    def approve(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="APPROVED",
        target="SUPERSEDED",
        permission="app.change_bom_status",
    )
    def approve(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="INACTIVE",
        permission="app.change_bom_status",
    )
    def set_inactive(self, by=None):
        return

    class Meta:
        get_latest_by = ["version"]
        ordering = [
            "material",
            "version",
        ]
        permissions = [
            ("change_bom_status", "Can change status of BOM"),
            ("submit_bom_for_approval", "Can submit BOM for approval"),
        ]
        verbose_name_plural = "Bills of materials"


class BillOfMaterialsCharacteristics(core_models.AbstractBaseModel):

    # PRODUCTION

    TEMPERATURE_CHOICES = (
        ("HOT", "Hot"),
        ("AMBIENT", "Ambient"),
        ("COLD", "Cold"),
    )

    temperature_preparation = models.CharField(
        max_length=8, choices=TEMPERATURE_CHOICES, null=True, blank=True
    )
    temperature_storage = models.CharField(
        max_length=8, choices=TEMPERATURE_CHOICES, null=True, blank=True
    )
    temperature_service = models.CharField(
        max_length=8, choices=TEMPERATURE_CHOICES, null=True, blank=True
    )
    note_production = models.TextField(
        "Production Notes",
        null=True,
        blank=True,
    )

    # LABOR

    total_active_time = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True,
    )
    total_inactive_time = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True,
    )
    staff_count = models.PositiveSmallIntegerField(default=0)
    note_labor = models.TextField(
        "Labor Notes",
        null=True,
        blank=True,
    )

    bill_of_materials = models.OneToOneField(
        BillOfMaterials,
        on_delete=models.CASCADE,
        related_name="characteristics",
    )

    def __str__(self):
        return f"{self.bill_of_materials.material} | characteristics"

    class Meta:
        ordering = ["bill_of_materials__material"]
        verbose_name_plural = "Bill of materials characteristics"


class BillOfMaterialsLine(core_models.AbstractBaseModel):
    sequence = models.PositiveSmallIntegerField(null=False, default=1)
    quantity = models.DecimalField(max_digits=8, decimal_places=3, null=False)
    note = models.CharField(max_length=32, null=True, blank=True)

    material = models.ForeignKey(
        materials_models.Material, on_delete=models.CASCADE, related_name="lines"
    )
    bill_of_materials = models.ForeignKey(
        BillOfMaterials, on_delete=models.CASCADE, related_name="lines"
    )
    unit = models.ForeignKey(core_models.UnitMeasurement, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bill_of_materials.material} | {self.material.name} "

    class Meta:
        ordering = ["sequence", "material"]
        verbose_name_plural = "Bill of materials lines"


class BillOfMaterialsNote(core_models.AbstractBaseModel):
    note = models.TextField()

    bill_of_materials = models.OneToOneField(
        BillOfMaterials, on_delete=models.CASCADE, related_name="note"
    )

    def __str__(self):
        return f"{self.bill_of_materials.material} | note"

    class Meta:
        ordering = ["bill_of_materials__material"]
        verbose_name_plural = "Bill of materials notes"


class BillOfMaterialsProcedure(core_models.AbstractBaseModel):
    LANGUAGE_CHOICES = (
        ("eng", "English"),
        ("esp", "Español"),
        ("fra", "Français"),
    )

    procedure = models.TextField()

    language = models.CharField(
        "Language",
        max_length=3,
        choices=LANGUAGE_CHOICES,
        default="eng",
    )

    bill_of_materials = models.ForeignKey(
        BillOfMaterials,
        on_delete=models.CASCADE,
        related_name="procedures",
    )

    def __str__(self):
        return f"{self.bill_of_materials.material} | {self.get_language_display()}"

    class Meta:
        ordering = ["bill_of_materials", "language"]
        unique_together = [
            "bill_of_materials",
            "language",
        ]
        verbose_name_plural = "Bill of materials procedures"


class BillOfMaterialsYield(core_models.AbstractBaseModel):
    # each BOM batch can specify a WEIGHT yield, a VOLUME yield and an EACH yield

    # WEIGHT
    quantity_weight = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    unit_weight = models.ForeignKey(
        core_models.UnitMeasurement,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    # VOLUME
    quantity_volume = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    unit_volume = models.ForeignKey(
        core_models.UnitMeasurement,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    # EACH
    quantity_each = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    # note_each field details what, precisely, the "each" unit is
    # ie, 36 ea 3" cookies, 72 ea 4" flan tart shells, etc
    note_each = models.CharField(max_length=64, null=True, blank=True)
    unit_each = models.ForeignKey(
        core_models.UnitMeasurement,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    bill_of_materials = models.OneToOneField(
        BillOfMaterials, on_delete=models.CASCADE, related_name="yields"
    )

    def __str__(self):
        return f"{self.bill_of_materials.material} | yield"

    class Meta:
        ordering = ["bill_of_materials__material"]
        verbose_name_plural = "Bill of materials yields"


@receiver(pre_save, sender=BillOfMaterials)
def check_increment_version(sender, instance, **kwargs):
    from apps.materials.models import Material
    from apps.production.models import BillOfMaterials, BillOfMaterialsLine

    if not instance._state.adding:
        # if state is mutable ("DRAFT", "AWAITING", "RETURNED", "INACTIVE"), changes do not trigger new version
        # if state is immutable ("APPROVED", "SUPERSEDED"), changes trigger new version

        immutable_states = [
            "APPROVED",
            "SUPERSEDED",
        ]
        if instance.state in immutable_states:
            instance.id = None
            instance.version += 1
            incremented_bill_of_material_version.send(
                sender=sender.__class__, new_version=instance.version
            )

            # TODO: BOM versioning
            # duplicate relations
            # new BillofMaterialsStatus => DRAFT
            # new BillofMaterialsCost => BLANK
            # all existing BillofMaterialsSection
            # all existing BillofMaterialsLine
        else:
            return
        # elif BillOfMaterials.objects.filter(material=instance.material).exists():
        #     # if BOM for given material exists but not immutable, do not increment version
        #     return
        # else:
        #     instance.id = None
        #     instance.version += 1
        #     incremented_bill_of_material_version.send(
        #         sender=self.__class__, new_version=self.version
        #     )
    else:
        print("New object creation")


@receiver(incremented_bill_of_material_version, sender=BillOfMaterials)
def duplicate_relations(sender, instance, **kwargs):
    print("HERE WOULD DUPLICATE RELATIONS")
    print("sender:", sender)
    print("instance:", instance)
    print("kwargs:", kwargs)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TEAM
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Team(core_models.AbstractBaseModel):
    name = models.CharField("Team name", max_length=32, null=True)
    slug = models.SlugField(max_length=32, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return str(self.id)

    class Meta:
        ordering = ["name"]
