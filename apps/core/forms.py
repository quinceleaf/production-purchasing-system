from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import (
    BaseInlineFormSet,
    formset_factory,
    inlineformset_factory,
    modelformset_factory,
)

from dal import autocomplete

from apps.core import models


# ––– FORMS


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super(BaseModelForm, self).__init__(*args, **kwargs)


class UnitMeasurementForm(BaseModelForm):
    def clean_name(self):
        objs = models.UnitMeasurement.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Unit with same name already exists")
        return name

    def clean_symbol(self):
        objs = models.UnitMeasurement.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        symbol = self.cleaned_data["symbol"]
        if objs.filter(symbol=symbol).exists():
            raise forms.ValidationError("Unit with same symbol already exists")
        return symbol

    class Meta:
        model = models.UnitMeasurement
        fields = ("name", "symbol", "unit_type")
