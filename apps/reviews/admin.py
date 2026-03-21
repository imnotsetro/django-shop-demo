from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ("product", "author", "rating", "title", "created_at")
    list_filter   = ("rating", "created_at")
    search_fields = ("title", "body", "author__email", "product__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)