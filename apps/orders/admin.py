from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ("id", "product_name", "user", "quantity", "total_price", "status", "created_at")
    list_filter   = ("status", "created_at", "country")
    search_fields = ("product_name", "user__email", "user__first_name", "full_name", "email")
    readonly_fields = ("created_at", "updated_at", "unit_price", "total_price", "product_name")
    ordering = ("-created_at",)

    fieldsets = (
        ("Orden", {
            "fields": ("user", "product", "product_name", "quantity", "unit_price", "total_price", "status")
        }),
        ("Datos de entrega", {
            "fields": ("full_name", "email", "phone", "country", "city")
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at")
        }),
    )