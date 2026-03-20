from django.conf import settings
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Propietario",
    )

    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name="Imagen",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de modificación")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def owner_display(self):
        """Devuelve el nombre completo del propietario, o su email como fallback."""
        return self.owner.get_full_name() or self.owner.email