from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "is_admin", "is_active", "created_at")
    list_filter = ("is_admin", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Información personal"), {"fields": ("first_name", "last_name")}),
        (_("Permisos"), {"fields": ("is_active", "is_admin", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Fechas"), {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "is_admin", "is_staff"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")