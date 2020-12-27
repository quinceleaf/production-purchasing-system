# ––– DJANGO IMPORTS
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView


# ––– PYTHON UTILITY IMPORTS


# ––– THIRD-PARTY IMPORTS
from dal import autocomplete


# ––– APPLICATION IMPORTS
from apps.core import models as core_models
from apps.materials import models as materials_models
from apps.production import models as production_models
from apps.purchasing import models as purchasing_models
from apps.sales import models as sales_models

"""
Views for
Index
Autocompletes
Settings (list filters, session variables)
"""


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# INDEX
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class IndexView(LoginRequiredMixin, TemplateView):
    context_object_name = "modules_list"
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        context["page_title"] = "Home"
        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def change_list_filter_settings(request, **kwargs):

    filter_model = kwargs.get("model")
    print("model:", filter_model)
    filter_field = kwargs.get("filter_field")
    print("filter_field:", filter_field)
    filter_value = kwargs.get("filter_value", None)
    print("filter_value:", filter_value)
    if filter_value:
        request.session[f"display_filter_{filter_model}"] = filter_value
    print(f"set session to: filter_{filter_model} = {filter_value}")

    referer = request.META.get("HTTP_REFERER")
    return HttpResponseRedirect(referer)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AUTOCOMPLETES
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class AutocompleteBillOfMaterials(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = materials_models.Material.objects.filter(bills_of_materials__isnull=False)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class AutocompleteClient(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = sales_models.Client.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class AutocompleteInput(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = materials_models.Input.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class AutocompleteManufacturer(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = materials_models.Manufacturer.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class AutocompleteMaterial(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        valid_choices = ["RAW", "MRO", "PACKAGING", "OTHER"]
        qs = materials_models.Material.objects.filter(category__in=valid_choices)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class AutocompleteMaterialForBOM(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = materials_models.Material.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class AutocompleteProduct(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        valid_choices = ["WIP", "FINISHED"]
        qs = materials_models.Material.objects.filter(category__in=valid_choices)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class AutocompleteTeam(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = production_models.Team.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class AutocompleteUnitMeasurement(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = core_models.UnitMeasurement.objects.all()

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(symbol__icontains=self.q))

        return qs


class AutocompleteUnitMeasurementWeight(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = core_models.UnitMeasurement.objects.filter(unit_type="WEIGHT")

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(symbol__icontains=self.q))

        return qs


class AutocompleteUnitMeasurementVolume(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = core_models.UnitMeasurement.objects.filter(unit_type="VOLUME")

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(symbol__icontains=self.q))

        return qs


class AutocompleteUnitMeasurementEach(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = core_models.UnitMeasurement.objects.filter(unit_type="EACH")

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(symbol__icontains=self.q))

        return qs


class AutocompleteVendor(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = purchasing_models.Vendor.objects.all()

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(symbol__icontains=self.q))

        return qs
