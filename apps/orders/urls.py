from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    # Checkout de un producto  →  /orders/checkout/<pk>/
    path("checkout/<int:pk>/", views.checkout_view, name="checkout"),

    # Detalle de una orden     →  /orders/<pk>/
    path("<int:pk>/",          views.order_detail_view, name="order_detail"),

    # Historial de compras     →  /orders/
    path("",                   views.order_history_view, name="order_history"),
]