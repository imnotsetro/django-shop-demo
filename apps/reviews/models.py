from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.products.models import Product


class Review(models.Model):
    """
    Reseña de un producto realizada por un usuario que lo compró.

    Restricciones de negocio (aplicadas en la view):
        - Solo usuarios que hayan comprado el producto pueden reseñarlo.
        - Un usuario solo puede tener una reseña por producto.
        - Solo el autor o un admin pueden editar/eliminar la reseña.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Producto",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Autor",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Calificación",
    )
    title = models.CharField(
        max_length=150,
        verbose_name="Título",
    )
    body = models.TextField(
        verbose_name="Comentario",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ["-created_at"]
        # Garantiza unicidad: un usuario, un producto, una reseña
        constraints = [
            models.UniqueConstraint(
                fields=["product", "author"],
                name="unique_review_per_user_per_product",
            )
        ]

    def __str__(self):
        return f"{self.rating}★ — {self.product.name} por {self.author}"

    @property
    def stars_filled(self):
        """Devuelve un rango de 1..rating para renderizar estrellas rellenas."""
        return range(1, self.rating + 1)

    @property
    def stars_empty(self):
        """Devuelve un rango para renderizar estrellas vacías."""
        return range(self.rating + 1, 6)