# ProductionSGR URL Configuration

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path



urlpatterns = [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("user/", include("django.contrib.auth.urls")),
    # path("__debug__/", include(debug_toolbar.urls)),
    path("", include("apps.core.urls", namespace="core")),
    path("", include("apps.production.urls", namespace="production")),
    path("", include("apps.materials.urls", namespace="materials")),
    path("", include("apps.purchasing.urls", namespace="purchasing")),
    path("", include("apps.sales.urls", namespace="sales")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "SG|R Production System Administration"
admin.site.site_title = "SG|R Production System Administration"
admin.site.index_title = "SG|R Production System Administration"