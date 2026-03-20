from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product
from .utils import require_product_ownership, user_can_edit_product


# ── LIST ──────────────────────────────────────────────────────────────────────

PRODUCTS_PER_PAGE = 8


def product_list(request):
    """
    Vista pública de lista de productos con paginación.
    Template: products/product_list.html
    Contexto:
        - page_obj   → Page actual
        - paginator  → Objeto Paginator
    """
    queryset = Product.objects.select_related("owner").all()
    paginator = Paginator(queryset, PRODUCTS_PER_PAGE)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "products/product_list.html", {
        "page_obj":  page_obj,
        "paginator": paginator,
    })


# ── DETAIL ────────────────────────────────────────────────────────────────────

def product_detail(request, pk):
    """
    Vista pública de detalle de un producto.
    Pasa 'can_edit' al template para mostrar/ocultar botones de editar/eliminar.
    Template: products/product_detail.html
    Contexto:
        - product  → instancia del producto (con owner cargado)
        - can_edit → bool — True si el usuario puede editar/eliminar
    """
    product = get_object_or_404(Product.objects.select_related("owner"), pk=pk)
    can_edit = user_can_edit_product(request.user, product)

    return render(request, "products/product_detail.html", {
        "product":  product,
        "can_edit": can_edit,
    })


# ── MY PRODUCTS ───────────────────────────────────────────────────────────────

@login_required
def my_products_view(request):
    """
    Lista todos los productos creados por el usuario autenticado.
    Template: products/my_products.html
    Contexto:
        - page_obj  → Page actual con los productos del usuario
        - paginator → Objeto Paginator
    """
    queryset = Product.objects.filter(owner=request.user).select_related("owner")
    paginator = Paginator(queryset, PRODUCTS_PER_PAGE)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "products/my_products.html", {
        "page_obj":  page_obj,
        "paginator": paginator,
    })


# ── CREATE ────────────────────────────────────────────────────────────────────

@login_required
def product_create(request):
    """
    Crea un nuevo producto. Requiere sesión iniciada.
    El campo 'owner' se asigna automáticamente al usuario autenticado.
    Template: products/product_form.html
    Contexto:
        - form   → ProductForm (vacío o con errores)
        - action → 'create'
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            messages.success(request, f'Producto "{product.name}" creado exitosamente.')
            return redirect("products:product_detail", pk=product.pk)
    else:
        form = ProductForm()

    return render(request, "products/product_form.html", {
        "form":   form,
        "action": "create",
    })


# ── UPDATE ────────────────────────────────────────────────────────────────────

@login_required
def product_update(request, pk):
    """
    Edita un producto. Solo el propietario o un admin pueden acceder.
    Redirige con mensaje de error al detalle si no tiene permiso.
    Template: products/product_form.html
    Contexto:
        - form    → ProductForm precargado
        - product → instancia del producto
        - action  → 'update'
    """
    product = get_object_or_404(Product.objects.select_related("owner"), pk=pk)

    # ── Verificar permisos ────────────────────────────────────────────────────
    denied = require_product_ownership(request, product)
    if denied:
        return denied

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{product.name}" actualizado exitosamente.')
            return redirect("products:product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, "products/product_form.html", {
        "form":    form,
        "product": product,
        "action":  "update",
    })


# ── DELETE ────────────────────────────────────────────────────────────────────

@login_required
def product_delete(request, pk):
    """
    Elimina un producto. Solo el propietario o un admin pueden acceder.
    Redirige con mensaje de error al detalle si no tiene permiso.
    GET  → muestra pantalla de confirmación
    POST → elimina y redirige al listado
    Template: products/product_confirm_delete.html
    Contexto:
        - product → instancia del producto a eliminar
    """
    product = get_object_or_404(Product.objects.select_related("owner"), pk=pk)

    # ── Verificar permisos ────────────────────────────────────────────────────
    denied = require_product_ownership(request, product)
    if denied:
        return denied

    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f'Producto "{name}" eliminado exitosamente.')
        return redirect("products:product_list")

    return render(request, "products/product_confirm_delete.html", {"product": product})