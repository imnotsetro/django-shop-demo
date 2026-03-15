from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import LoginForm, RegisterForm


# ── REGISTER ──────────────────────────────────────────────────────────────────

def register_view(request):
    """
    Registro de nuevos usuarios.
    Template: accounts/register.html
    Contexto: form → RegisterForm
    """
    if request.user.is_authenticated:
        return redirect("products:product_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.get_short_name()}! Tu cuenta fue creada exitosamente.")
            return redirect("products:product_list")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


# ── LOGIN ─────────────────────────────────────────────────────────────────────

def login_view(request):
    """
    Inicio de sesión.
    Template: accounts/login.html
    Contexto: form → LoginForm
    """
    if request.user.is_authenticated:
        return redirect("products:product_list")

    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Hola de nuevo, {user.get_short_name()}!")
            # Redirige a 'next' si existe, sino al listado
            next_url = request.GET.get("next") or "products:product_list"
            return redirect(next_url)
    else:
        form = LoginForm(request=request)

    return render(request, "accounts/login.html", {"form": form})


# ── LOGOUT ────────────────────────────────────────────────────────────────────

@login_required
def logout_view(request):
    """
    Cierre de sesión. Solo acepta POST para evitar CSRF via GET.
    Redirige al login tras cerrar sesión.
    """
    if request.method == "POST":
        logout(request)
        messages.info(request, "Sesión cerrada correctamente.")
    return redirect("accounts:login")


# ── PROFILE ───────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    """
    Perfil del usuario autenticado.
    Template: accounts/profile.html
    Contexto: user → request.user (disponible automáticamente en templates)
    """
    return render(request, "accounts/profile.html")