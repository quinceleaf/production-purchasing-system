from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.core import converters
from apps.production import forms, models, views

register_converter(converters.ULIDConverter, "ulid")

app_name = "apps.production"


WIZARD_FORMS = [
    ("lines", forms.BillOfMaterialsLineFormSet),
    ("procedure", forms.BillOfMaterialsProcedureForm),
    ("yields", forms.BillOfMaterialsYieldForm),
    ("characteristics", forms.BillOfMaterialsCharacteristicsForm),
    ("notes", forms.BillOfMaterialsNoteForm),
]

WIZARD_INSTANCES = {
    "line": models.BillOfMaterialsLine(),
    "procedure": models.BillOfMaterialsProcedure(),
    "yields": models.BillOfMaterialsYield(),
    "characteristics": models.BillOfMaterialsCharacteristics(),
    "notes": models.BillOfMaterialsNote(),
}


bill_of_materials_patterns = [
    path(
        "<ulid:pk>/status/<str:status>/",
        views.change_bill_of_materials_status,
        name="bill_of_materials_change_status",
    ),
    path(
        "<ulid:pk>/team/<str:team>/",
        views.change_bill_of_materials_team,
        name="bill_of_materials_change_team",
    ),
    path(
        "<ulid:pk>/edit/",
        views.BillOfMaterialsUpdateView.as_view(),
        name="bill_of_materials_edit",
    ),
    path(
        "<ulid:pk>/",
        views.BillOfMaterialsDetailView.as_view(),
        name="bill_of_materials_detail",
    ),
    path(
        "add/", views.BillOfMaterialsCreateView.as_view(), name="bill_of_materials_add"
    ),
    path(
        "list/", views.BillOfMaterialsListView.as_view(), name="bill_of_materials_list"
    ),
    path(
        "wizard/<ulid:pk>/",
        views.BillOfMaterialsWizardCreateView.as_view(WIZARD_FORMS),
        name="bill_of_materials_wizard",
    ),
    path(
        "wizard/",
        views.BillOfMaterialsWizardCreateView.as_view(WIZARD_FORMS),
        name="bill_of_materials_wizard",
    ),
]

element_patterns = [
    path(
        "<ulid:pk>/characteristics/<str:language>/",
        views.BillOfMaterialsCharacteristicsCreateView.as_view(),
        name="bill_of_materials_characteristics_add",
    ),
    path(
        "characteristics/<ulid:pk>/edit/",
        views.BillOfMaterialsCharacteristicsUpdateView.as_view(),
        name="bill_of_materials_characteristics_edit",
    ),
    path(
        "<ulid:pk>/ingredients/edit/",
        views.BillOfMaterialsLineUpdateView.as_view(),
        name="bill_of_materials_line_edit",
    ),
    path(
        "<ulid:pk>/note/",
        views.BillOfMaterialsNoteCreateView.as_view(),
        name="bill_of_materials_note_add",
    ),
    path(
        "note/<ulid:pk>/edit/",
        views.BillOfMaterialsNoteUpdateView.as_view(),
        name="bill_of_materials_note_edit",
    ),
    path(
        "<ulid:pk>/procedure/<str:language>/",
        views.BillOfMaterialsProcedureCreateView.as_view(),
        name="bill_of_materials_procedure_add",
    ),
    path(
        "procedure/<ulid:pk>/edit/",
        views.BillOfMaterialsProcedureUpdateView.as_view(),
        name="bill_of_materials_procedure_edit",
    ),
    path(
        "<ulid:pk>/yield/",
        views.BillOfMaterialsYieldCreateView.as_view(),
        name="bill_of_materials_yield_add",
    ),
    path(
        "yield/<ulid:pk>/edit/",
        views.BillOfMaterialsYieldUpdateView.as_view(),
        name="bill_of_materials_yield_edit",
    ),
]

team_urls = [
    path("<ulid:pk>/edit/", views.TeamUpdateView.as_view(), name="team_edit"),
    path("<ulid:pk>/", views.TeamDetailView.as_view(), name="team_detail"),
    path("add/", views.TeamCreateView.as_view(), name="team_add"),
    path("list/", views.TeamListView.as_view(), name="team_list"),
]


urlpatterns = [
    path("bill_of_materials/", include(bill_of_materials_patterns)),
    path("elements/", include(element_patterns)),
    path("teams/", include(team_urls)),
]
