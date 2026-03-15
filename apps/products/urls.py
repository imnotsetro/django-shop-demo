from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # Lista de productos  →  /products/
    path("", views.product_list, name="product_list"),

    # Detalle             →  /products/<pk>/
    path("<int:pk>/", views.product_detail, name="product_detail"),

    # Crear               →  /products/new/
    path("new/", views.product_create, name="product_create"),

    # Editar              →  /products/<pk>/edit/
    path("<int:pk>/edit/", views.product_update, name="product_update"),

    # Eliminar            →  /products/<pk>/delete/
    path("<int:pk>/delete/", views.product_delete, name="product_delete"),
]