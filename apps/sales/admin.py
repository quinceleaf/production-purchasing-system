from django.contrib import admin
from django.contrib.auth.admin import AdminPasswordChangeForm, UserAdmin
from django.utils.html import mark_safe

from apps.users import models
from apps.core.admin import admin_link, BaseAdminConfig


"""
User
UserProfile
"""


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ADD-ONS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class UserProfileInline(admin.TabularInline):
    model = models.UserProfile


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MODELS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class UserAdminConfig(BaseAdminConfig):
    fieldsets = (
        (
            "None",
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "password",
                    "is_active",
                )
            },
        ),
        (
            "Last Login",
            {"fields": ("last_login",)},
        ),
        (
            "Groups & Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    filter_horizontal = ["groups", "user_permissions"]
    inlines = (UserProfileInline,)
    readonly_fields = ["id", "created_at", "last_login", "updated_at"]


@admin.register(models.User)
class UserAdmin(UserAdminConfig):
    pass


@admin.register(models.UserProfile)
class UserProfileAdmin(BaseAdminConfig):
    list_display = ("__str__", "avatar", "get_thumbnail")

    def get_thumbnail(self, obj):
        return mark_safe(f'<img width="50px" src="{obj.avatar.url}" />')

    get_thumbnail.short_description = "Thumbnail"