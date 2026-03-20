from django.contrib import messages
from django.shortcuts import redirect

from .models import Product


def user_can_edit_product(user, product):
    """
    Devuelve True si el usuario tiene permiso para editar o eliminar el producto.

    Regla:
        - El propietario del producto (product.owner == user) siempre puede.
        - Un administrador (user.is_admin) puede sobre cualquier producto.
        - Cualquier otro usuario no puede.
    """
    if not user.is_authenticated:
        return False
    return product.owner == user or user.is_admin


def require_product_ownership(request, product):
    """
    Verifica que request.user pueda editar/eliminar el producto.
    Si no tiene permiso, agrega un mensaje de error y devuelve un redirect.
    Devuelve None si el acceso está permitido.

    Uso típico en una view:
        response = require_product_ownership(request, product)
        if response:
            return response
    """
    if not user_can_edit_product(request.user, product):
        messages.error(
            request,
            "No tenés permiso para modificar este producto. "
            "Solo el propietario o un administrador pueden hacerlo."
        )
        return redirect("products:product_detail", pk=product.pk)
    return None