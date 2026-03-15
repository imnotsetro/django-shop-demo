from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Product
from .forms import ProductForm


# ── LIST ──────────────────────────────────────────────────────────────────────

PRODUCTS_PER_PAGE = 8

def product_list(request):
    """
    Vista de lista de productos con paginación.
    Template esperado: products/product_list.html
    Contexto disponible:
        - page_obj   → Page actual (contiene los productos de esa página)
        - paginator  → Objeto Paginator (total de páginas, conteos, etc.)
    """
    queryset = Product.objects.all()
    paginator = Paginator(queryset, PRODUCTS_PER_PAGE)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)  # nunca lanza excepción

    return render(request, "products/product_list.html", {
        "page_obj": page_obj,
        "paginator": paginator,
    })


# ── DETAIL ────────────────────────────────────────────────────────────────────

def product_detail(request, pk):
    """
    Vista de detalle de un producto.
    Template esperado: products/product_detail.html
    Contexto disponible:
        - product   → instancia del producto
    """
    product = get_object_or_404(Product, pk=pk)
    return render(request, "products/product_detail.html", {"product": product})


# ── CREATE ────────────────────────────────────────────────────────────────────

def product_create(request):
    """
    Vista para crear un producto.
    Template esperado: products/product_form.html
    Contexto disponible:
        - form      → ProductForm (vacío o con errores)
        - action    → 'create' (útil para personalizar el template)
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Producto "{product.name}" creado exitosamente.')
            return redirect("products:product_detail", pk=product.pk)
    else:
        form = ProductForm()

    return render(request, "products/product_form.html", {"form": form, "action": "create"})


# ── UPDATE ────────────────────────────────────────────────────────────────────

def product_update(request, pk):
    """
    Vista para editar un producto existente.
    Template esperado: products/product_form.html
    Contexto disponible:
        - form      → ProductForm precargado con los datos actuales
        - product   → instancia del producto
        - action    → 'update' (útil para personalizar el template)
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

    return render(
        request,
        "products/product_form.html",
        {"form": form, "product": product, "action": "update"},
    )


# ── DELETE ────────────────────────────────────────────────────────────────────

def product_delete(request, pk):
    """
    Vista para eliminar un producto.
    Template esperado: products/product_confirm_delete.html
    Contexto disponible:
        - product   → instancia del producto a eliminar
    Flujo:
        GET  → muestra pantalla de confirmación
        POST → elimina y redirige al listado
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f'Producto "{name}" eliminado exitosamente.')
        return redirect("products:product_list")

    return render(request, "products/product_confirm_delete.html", {"product": product})