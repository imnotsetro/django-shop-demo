from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.products.models import Product
from .forms import CheckoutForm
from .models import Order


# ── CHECKOUT ──────────────────────────────────────────────────────────────────

@login_required
def checkout_view(request, pk):
    """
    Checkout para comprar un producto individual.
    GET  → muestra el formulario pre-relleno con datos del usuario.
    POST → valida, crea la orden, descuenta stock y redirige a confirmación.
    """
    product = get_object_or_404(Product, pk=pk)

    if product.stock < 1:
        messages.error(request, "Este producto no tiene stock disponible.")
        return redirect("products:product_detail", pk=pk)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
                    product_locked = Product.objects.select_for_update().get(pk=pk)
                    if product_locked.stock < 1:
                        messages.error(request, "El producto se agotó mientras procesabas el pago.")
                        return redirect("products:product_detail", pk=pk)

                    order = Order.objects.create(
                        user=request.user,
                        product=product_locked,
                        quantity=1,
                        unit_price=product_locked.price,
                        total_price=product_locked.price,
                        product_name=product_locked.name,
                        status=Order.Status.CONFIRMED,
                        full_name=data["full_name"],
                        email=data["email"],
                        phone=data.get("phone", ""),
                        country=data["country"],
                        city=data["city"],
                        between_streets=data.get("between_streets", ""),
                        postal_code=data["postal_code"],
                        house_number=data["house_number"],
                    )

                    product_locked.stock -= 1
                    product_locked.save(update_fields=["stock", "updated_at"])

            except Product.DoesNotExist:
                messages.error(request, "El producto ya no existe.")
                return redirect("products:product_list")

            messages.success(request, f'¡Compra confirmada! Tu orden #{order.pk} fue procesada.')
            return redirect("orders:order_detail", pk=order.pk)
        # Si el form es inválido, vuelve a renderizar mostrando los errores
    else:
        form = CheckoutForm(initial={
            "full_name": request.user.get_full_name(),
            "email":     request.user.email,
        })

    return render(request, "orders/checkout.html", {
        "product": product,
        "form":    form,
    })


# ── ORDER DETAIL ──────────────────────────────────────────────────────────────

@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})


# ── ORDER HISTORY ─────────────────────────────────────────────────────────────

@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).select_related("product")
    return render(request, "orders/order_history.html", {"orders": orders})