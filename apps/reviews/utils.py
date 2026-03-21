from django.contrib import messages
from django.shortcuts import redirect

from apps.orders.models import Order


def user_has_purchased(user, product):
    """
    Devuelve True si el usuario tiene al menos una orden confirmada del producto.
    """
    return Order.objects.filter(
        user=user,
        product=product,
        status=Order.Status.CONFIRMED,
    ).exists()


def user_can_manage_review(user, review):
    """
    Devuelve True si el usuario puede editar o eliminar la reseña.
    Solo el autor o un admin pueden hacerlo.
    """
    if not user.is_authenticated:
        return False
    return review.author == user or user.is_admin


def require_review_ownership(request, review):
    """
    Verifica permisos sobre la reseña. Si no los tiene, redirige con error.
    Devuelve None si el acceso está permitido.
    """
    if not user_can_manage_review(request.user, review):
        messages.error(
            request,
            "No tenés permiso para modificar esta reseña. "
            "Solo el autor o un administrador pueden hacerlo."
        )
        return redirect("products:product_detail", pk=review.product.pk)
    return None