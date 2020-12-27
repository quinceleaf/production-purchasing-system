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
from apps.materials import models


class InputForm(BaseModelForm):

    manufacturer = forms.ModelChoiceField(
        queryset=models.Manufacturer.objects.all(),
        required=True,
        label=u"Manufacturer",
        widget=autocomplete.ModelSelect2(
            url="autocomplete-manufacturer",
            attrs={
                "data-placeholder": "Select ...",
                "data-minimum-input-length": 1,
                "style": "width: 70%;",
            },
        ),
    )

    material = forms.ModelChoiceField(
        queryset=models.Material.objects.all(),
        required=True,
        label=u"Material",
        widget=autocomplete.ModelSelect2(
            url="autocomplete-material",
            attrs={
                "data-placeholder": "Select ...",
                "data-minimum-input-length": 1,
                "style": "width: 70%;",
            },
        ),
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "notes-1"}),
    )

    unit = forms.ModelChoiceField(
        queryset=core_models.UnitMeasurement.objects.all(),
        required=True,
        label=u"Pack Form",
        widget=autocomplete.ModelSelect2(
            url="autocomplete-unit-measurement",
            attrs={
                "data-placeholder": "Select ...",
                "data-minimum-input-length": 1,
                "style": "width: 70%;",
            },
        ),
    )

    def clean_name(self):
        objs = models.Input.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Input with same name already exists")
        return name

    class Meta:
        model = models.Input
        fields = (
            "name",
            "category",
            "state",
            "material",
            "manufacturer",
            "manufacturer_item_number",
            "unit",
            "pack_size",
            "pack_total_weight",
            "pack_total_volume",
            "pack_total_each",
            "notes",
        )


class ManufacturerForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(ManufacturerForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        objs = models.Manufacturer.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Manufacturer with same name already exists")
        return name

    class Meta:
        model = models.Manufacturer
        fields = (
            "name",
            "state",
            "notes",
        )


class MaterialForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        valid_choices = ["RAW", "MRO", "PACKAGING", "OTHER"]
        self.fields["category"].choices = [
            choice
            for choice in models.Material.INVENTORY_CATEGORY_CHOICES
            if choice[0] in valid_choices
        ]

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "notes-1"}),
    )

    def clean_name(self):
        valid_choices = ["RAW", "MRO", "PACKAGING", "OTHER"]
        objs = models.Material.objects.filter(category__in=valid_choices)
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Material with same name already exists")
        return name

    class Meta:
        model = models.Material
        fields = (
            "name",
            "category",
            "unit_type",
            "notes",
        )


class ProductForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        valid_choices = ["FINISHED", "WIP"]
        self.fields["category"].choices = [
            choice
            for choice in models.Material.INVENTORY_CATEGORY_CHOICES
            if choice[0] in valid_choices
        ]

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "notes-1"}),
    )

    def clean_name(self):
        valid_choices = ["WIP", "FINISHED"]
        objs = models.Material.objects.filter(category__in=valid_choices)
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Product with same name already exists")
        return name

    class Meta:
        model = models.Material
        fields = (
            "name",
            "category",
            "unit_type",
            "upc_code",
            "shelf_life",
            "notes",
        )
