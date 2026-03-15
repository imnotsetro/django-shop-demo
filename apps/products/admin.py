from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "price", "stock", "created_at", "updated_at")
    list_filter = ("owner",)
    search_fields = ("name", "description", "owner")
    readonly_fields = ("created_at", "updated_at")