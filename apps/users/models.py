# ––– DJANGO IMPORTS
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver, Signal


# ––– PYTHON UTILITY IMPORTS


# –––THIRD-PARTY IMPORTS


# ––– PROJECT IMPORTS
from apps.core import models as core_models


# ––– PARAMETERS


# ––– MODELS


class User(PermissionsMixin, AbstractBaseUser, core_models.AbstractBaseModel):
    username_validator = UnicodeUsernameValidator()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    email = models.EmailField("Email address", blank=True)
    is_active = models.BooleanField("Active", default=True)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    first_name = models.CharField(max_length=40, null=True, blank=True)
    last_name = models.CharField(max_length=80, null=True, blank=True)
    username = models.CharField(
        "Username", max_length=255, unique=True, validators=[username_validator]
    )

    objects = UserManager()

    class Meta:
        ordering = [
            "last_name",
            "first_name",
        ]

    def __str__(self):
        return f"{self.username}"


class UserProfile(core_models.AbstractBaseModel):

    avatar = models.ImageField(upload_to="avatars", null=True, blank=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return f"{self.user.username} | profile"


@receiver(post_save, sender=User)
def create_profile_on_user_creation(sender, created, instance, **kwargs):
    """
    Create UserProfile upon User instance creation
    """
    from apps.users.models import UserProfile

    if created:
        UserProfile(user=instance)
