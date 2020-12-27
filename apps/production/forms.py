from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import (
    BaseInlineFormSet,
    formset_factory,
    inlineformset_factory,
    modelformset_factory,
)

from dal import autocomplete

from apps.core import models as core_models
from apps.core.forms import BaseModelForm
from apps.materials import models as materials_models
from apps.production import models


class BillOfMaterialsCharacteristicsForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(BillOfMaterialsCharacteristicsForm, self).__init__(*args, **kwargs)
        if models.Team.objects.count() == 1:
            self.fields["team"].initial = models.Team.objects.get()

    team = forms.ModelChoiceField(
        queryset=models.Team.objects.all(),
        required=True,
        label=u"Team",
        widget=autocomplete.ModelSelect2(
            url="autocomplete-team",
            attrs={
                "data-placeholder": "Select ...",
                "data-minimum-input-length": 1,
            },
        ),
    )

    note_labor = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "procedure-1"}),
    )

    note_production = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "procedure-2"}),
    )

    class Meta:
        model = models.BillOfMaterialsCharacteristics
        fields = (
            "team",
            "temperature_preparation",
            "temperature_storage",
            "temperature_service",
            "note_production",
            "total_active_time",
            "total_inactive_time",
            "staff_count",
            "note_labor",
        )


class BillOfMaterialsLineForm(BaseModelForm):

    unit = forms.ModelChoiceField(
        queryset=core_models.UnitMeasurement.objects.all(),
        required=False,
        label=u"Unit",
        widget=autocomplete.ModelSelect2(
            url="autocomplete-unit-measurement",
            attrs={
                "data-placeholder": "Select ...",
                "data-minimum-input-length": 1,
                "style": "width: 70%;",
            },
        ),
    )

    material = forms.ModelChoiceField(
        queryset=materials_models.Material.objects.all(),
        required=False,
        label=u"Material",
        widget=autocomplete.ModelSelect2(
            url="autocomplete-material-for-bom",
            attrs={
                "data-placeholder": "Select ...",
                "data-minimum-input-length": 1,
                "style": "width: 70%;",
            },
        ),
    )

    class Meta:
        model = models.BillOfMaterialsLine
        fields = ("sequence", "quantity", "unit", "material", "note")


BillOfMaterialsLineFormSet = inlineformset_factory(
    parent_model=models.BillOfMaterials,
    model=models.BillOfMaterialsLine,
    form=BillOfMaterialsLineForm,
    fields=[
        "sequence",
        "quantity",
        "unit",
        "material",
        "note",
    ],
    extra=0,
    can_delete=True,
)


class BillOfMaterialsNoteForm(BaseModelForm):

    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "procedure-1"}),
    )

    class Meta:
        model = models.BillOfMaterialsNote
        fields = ("note",)


class BillOfMaterialsProcedureForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop("language", None)
        super(BillOfMaterialsProcedureForm, self).__init__(*args, **kwargs)
        if self.language:
            self.fields["language"].initial = self.language
            self.fields["language"].widget.attrs["readonly"] = True

    procedure = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 5, "id": "procedure-1"}),
    )

    class Meta:
        model = models.BillOfMaterialsProcedure
        fields = ("language", "procedure")


class BillOfMaterialsYieldForm(BaseModelForm):

    unit_each = forms.ModelChoiceField(
        queryset=core_models.UnitMeasurement.objects.filter(unit_type="EACH"),
        required=False,
        label=u"Unit (Each)",
        widget=autocomplete.ModelSelect2(
            url="autocomplete-unit-measurement-each",
            attrs={
                "data-placeholder": "Select ...",
                "data-minimum-input-length": 1,
                "style": "width: 70%;",
            },
        ),
    )

    unit_volume = forms.ModelChoiceField(
        queryset=core_models.UnitMeasurement.objects.filter(unit_type="VOLUME"),
        required=False,
        label=u"Unit (Volume)",
        widget=autocomplete.ModelSelect2(
            url="autocomplete-unit-measurement-volume",
            attrs={
                "data-placeholder": "Select ...",
                "data-minimum-input-length": 1,
                "style": "width: 70%;",
            },
        ),
    )

    unit_weight = forms.ModelChoiceField(
        queryset=core_models.UnitMeasurement.objects.filter(unit_type="WEIGHT"),
        required=False,
        label=u"Unit (Weight)",
        widget=autocomplete.ModelSelect2(
            url="autocomplete-unit-measurement-weight",
            attrs={
                "data-placeholder": "Select ...",
                "data-minimum-input-length": 1,
                "style": "width: 70%;",
            },
        ),
    )

    class Meta:
        model = models.BillOfMaterialsYield
        fields = (
            "quantity_weight",
            "unit_weight",
            "quantity_volume",
            "unit_volume",
            "quantity_each",
            "unit_each",
            "note_each",
        )


class TeamForm(BaseModelForm):
    def clean_name(self):
        objs = models.Team.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Team with same name already exists")
        return name

    class Meta:
        model = models.Team
        fields = ("name", "slug")
