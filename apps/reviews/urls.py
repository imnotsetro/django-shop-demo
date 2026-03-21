from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    # Crear reseña de un producto  →  /reviews/product/<pk>/create/
    path("product/<int:product_pk>/create/", views.review_create, name="review_create"),

    # Editar reseña                →  /reviews/<pk>/edit/
    path("<int:pk>/edit/",                  views.review_update, name="review_update"),

    # Eliminar reseña              →  /reviews/<pk>/delete/
    path("<int:pk>/delete/",               views.review_delete, name="review_delete"),

    # Mis reseñas                  →  /reviews/my/
    path("my/",                            views.my_reviews_view, name="my_reviews"),
]