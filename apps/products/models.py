from django.conf import settings
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripcion")
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creacion")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de modificacion")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def owner_display(self):
        """Devuelve el nombre completo del propietario, o su email como fallback."""
        return self.owner.get_full_name() or self.owner.email

    @property
    def image_url(self):
        """
        Devuelve la URL correcta de la imagen independientemente de su origen:
          - URL externa (ej: seed con Unsplash) -> se retorna tal cual.
          - Archivo local subido por el usuario  -> se retorna via .url de Django.
          - Sin imagen                           -> retorna None.

        Usar siempre {{ product.image_url }} en templates en lugar de
        {{ product.image.url }}, que falla cuando el valor es una URL externa.
        """
        if not self.image:
            return None
        raw = str(self.image)
        if raw.startswith("http://") or raw.startswith("https://"):
            return raw
        return self.image.url