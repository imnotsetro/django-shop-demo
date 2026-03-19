from django.conf import settings
from django.db import models

from apps.products.models import Product


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING   = "pending",   "Pendiente"
        CONFIRMED = "confirmed", "Confirmada"
        CANCELLED = "cancelled", "Cancelada"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Usuario",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
        verbose_name="Producto",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")

    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio total")
    product_name = models.CharField(max_length=255, verbose_name="Nombre del producto")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
        verbose_name="Estado",
    )

    # Datos de entrega
    full_name       = models.CharField(max_length=255, verbose_name="Nombre completo")
    email           = models.EmailField(verbose_name="Correo electrónico")
    phone           = models.CharField(max_length=30, blank=True, verbose_name="Teléfono")
    country         = models.CharField(max_length=100, verbose_name="País")
    city            = models.CharField(max_length=100, verbose_name="Ciudad")
    between_streets = models.CharField(max_length=255, blank=True, verbose_name="Entre calles")
    postal_code     = models.CharField(max_length=10, verbose_name="Código postal")
    house_number    = models.CharField(max_length=20, verbose_name="Número / Depto")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de compra")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Orden #{self.pk} — {self.product_name} ({self.user})"