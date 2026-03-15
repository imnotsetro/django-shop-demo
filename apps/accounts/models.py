from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio.")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("El superusuario debe tener is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado.
    Usa email como identificador principal en lugar de username.
    """

    email = models.EmailField(
        unique=True,
        verbose_name="Correo electrónico",
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name="Nombre",
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Apellido",
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name="¿Es administrador?",
        help_text="Indica si el usuario tiene permisos de administración en la aplicación.",
    )

    # Campos requeridos por Django
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff",
        help_text="Permite acceder al panel de administración de Django.",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["email"]

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name