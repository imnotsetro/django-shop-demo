from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.products.models import Product
from .forms import ReviewForm
from .models import Review
from .utils import require_review_ownership, user_has_purchased, user_can_manage_review


# ── CREATE ────────────────────────────────────────────────────────────────────

@login_required
def review_create(request, product_pk):
    """
    Crea una reseña para un producto.
    Solo usuarios con una compra confirmada del producto pueden reseñarlo.
    Un usuario no puede reseñar el mismo producto dos veces.

    Redirige al detalle del producto en todos los casos.
    """
    product = get_object_or_404(Product, pk=product_pk)

    # Verificar que el usuario haya comprado el producto
    if not user_has_purchased(request.user, product):
        messages.error(request, "Solo podés reseñar productos que hayas comprado.")
        return redirect("products:product_detail", pk=product_pk)

    # Verificar que no tenga reseña existente
    if Review.objects.filter(product=product, author=request.user).exists():
        messages.error(request, "Ya escribiste una reseña para este producto.")
        return redirect("products:product_detail", pk=product_pk)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.author = request.user
            review.save()
            messages.success(request, "¡Reseña publicada exitosamente!")
            return redirect("products:product_detail", pk=product_pk)
    else:
        form = ReviewForm()

    return render(request, "reviews/review_form.html", {
        "form":    form,
        "product": product,
        "action":  "create",
    })


# ── UPDATE ────────────────────────────────────────────────────────────────────

@login_required
def review_update(request, pk):
    """
    Edita una reseña existente.
    Solo el autor o un admin pueden editarla.
    """
    review = get_object_or_404(Review.objects.select_related("product", "author"), pk=pk)

    denied = require_review_ownership(request, review)
    if denied:
        return denied

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Reseña actualizada exitosamente.")
            return redirect("products:product_detail", pk=review.product.pk)
    else:
        form = ReviewForm(instance=review)

    return render(request, "reviews/review_form.html", {
        "form":    form,
        "product": review.product,
        "review":  review,
        "action":  "update",
    })


# ── DELETE ────────────────────────────────────────────────────────────────────

@login_required
def review_delete(request, pk):
    """
    Elimina una reseña. Solo acepta POST.
    Solo el autor o un admin pueden eliminarla.
    """
    review = get_object_or_404(Review.objects.select_related("product", "author"), pk=pk)

    denied = require_review_ownership(request, review)
    if denied:
        return denied

    if request.method == "POST":
        product_pk = review.product.pk
        review.delete()
        messages.success(request, "Reseña eliminada correctamente.")
        return redirect("products:product_detail", pk=product_pk)

    # GET accidental → redirigir al detalle
    return redirect("products:product_detail", pk=review.product.pk)


# ── MY REVIEWS ────────────────────────────────────────────────────────────────

@login_required
def my_reviews_view(request):
    """
    Lista todas las reseñas escritas por el usuario autenticado.
    Template: reviews/my_reviews.html
    Contexto:
        - reviews → QuerySet de reseñas del usuario
    """
    reviews = (
        Review.objects
        .filter(author=request.user)
        .select_related("product", "author")
        .order_by("-created_at")
    )
    return render(request, "reviews/my_reviews.html", {"reviews": reviews})