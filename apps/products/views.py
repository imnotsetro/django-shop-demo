from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Product
from .forms import ProductForm


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
    queryset = Product.objects.all()
    paginator = Paginator(queryset, PRODUCTS_PER_PAGE)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "products/product_list.html", {
        "page_obj": page_obj,
        "paginator": paginator,
    })


# ── DETAIL ────────────────────────────────────────────────────────────────────

def product_detail(request, pk):
    """
    Vista pública de detalle de un producto.
    Template: products/product_detail.html
    Contexto:
        - product → instancia del producto
    """
    product = get_object_or_404(Product, pk=pk)
    return render(request, "products/product_detail.html", {"product": product})


# ── CREATE ────────────────────────────────────────────────────────────────────

@login_required
def product_create(request):
    """
    Crea un nuevo producto. Requiere sesión iniciada.
    El campo 'owner' se asigna automáticamente al nombre completo del usuario.
    Template: products/product_form.html
    Contexto:
        - form   → ProductForm (vacío o con errores)
        - action → 'create'
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user.get_full_name() or request.user.email
            product.save()
            messages.success(request, f'Producto "{product.name}" creado exitosamente.')
            return redirect("products:product_detail", pk=product.pk)
    else:
        form = ProductForm()

    return render(request, "products/product_form.html", {
        "form": form,
        "action": "create",
    })


# ── UPDATE ────────────────────────────────────────────────────────────────────

@login_required
def product_update(request, pk):
    """
    Edita un producto existente. Requiere sesión iniciada.
    Template: products/product_form.html
    Contexto:
        - form    → ProductForm precargado
        - product → instancia del producto
        - action  → 'update'
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{product.name}" actualizado exitosamente.')
            return redirect("products:product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, "products/product_form.html", {
        "form": form,
        "product": product,
        "action": "update",
    })


# ── DELETE ────────────────────────────────────────────────────────────────────

@login_required
def product_delete(request, pk):
    """
    Elimina un producto. Requiere sesión iniciada.
    GET  → muestra pantalla de confirmación
    POST → elimina y redirige al listado
    Template: products/product_confirm_delete.html
    Contexto:
        - product → instancia del producto a eliminar
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f'Producto "{name}" eliminado exitosamente.')
        return redirect("products:product_list")

    return render(request, "products/product_confirm_delete.html", {"product": product})