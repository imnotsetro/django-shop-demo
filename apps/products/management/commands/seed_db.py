"""
Management command: seed_db
Uso:
    python manage.py seed_db
    python manage.py seed_db --products 100 --users 50
    python manage.py seed_db --flush   (borra todo antes de sembrar)

Crea productos con imágenes reales de media/demo/ y usuarios de prueba.
"""

import os
import random
import shutil
from decimal import Decimal
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import Product

User = get_user_model()


# ── Imágenes disponibles en media/demo/ ───────────────────────────────────────
# Cada entrada: (filename_sin_extension, extension)
DEMO_IMAGES = [
    ("bicicleta1",  "jpg"),
    ("bicicleta2",  "jpg"),
    ("bicicleta3", "jpg"),
    ("iphone",     "jpg"),
    ("licuadora",  "jpg"),
    ("samsung",    "jpg"),
    ("microondas", "jpg"),
    ("heladera",   "jpg"),
]

# ── Datos de productos agrupados por imagen ────────────────────────────────────
# Cada imagen tiene múltiples variantes de producto con nombre y descripción únicos
PRODUCT_TEMPLATES = [
    # ── Bicicletas ──
    {
        "image": "bicicleta1",
        "variants": [
            ("Bicicleta de Montaña TrailX Pro",      "Rodado 29, cuadro de aluminio, 21 velocidades Shimano. Ideal para senderos y terreno irregular."),
            ("Bicicleta MTB Summit 500",              "Suspensión delantera, frenos de disco hidráulicos, cuadro reforzado para máxima resistencia."),
            ("Bicicleta Todo Terreno Explorer",       "Diseñada para aventureros. Ruedas anchas, cambios suaves y asiento ergonómico."),
            ("Bicicleta de Montaña Juvenil XPeak",   "Perfecta para jóvenes deportistas. Liviana, resistente y con colores llamativos."),
            ("Bicicleta Hardtail Enduro 27.5",        "Horquilla de suspensión de 100mm, cuadro de acero cromoly, ideal para enduro."),
            ("Bicicleta de Montaña CrossRide 650B",  "Versatilidad total: funciona tanto en ciudad como en senderos moderados."),
        ],
    },
    {
        "image": "bicicleta2",
        "variants": [
            ("Bicicleta de Ruta Velocity R10",       "Cuadro de carbono ultraliviano, 22 velocidades, ideal para ciclismo de competencia."),
            ("Bicicleta de Carretera AeroSpeed",     "Diseño aerodinámico, manubrio drop bar, transmisión Shimano 105 de 11 velocidades."),
            ("Bicicleta Gravel GravelKing GX",       "Combina lo mejor del ciclismo de ruta y montaña. Llantas 700c con neumáticos mixtos."),
            ("Bicicleta de Ruta CarbonElite Pro",    "Peso total: 7.8kg. Horquilla de carbono, ruedas de perfil bajo, para largas distancias."),
            ("Bicicleta Triatlón IronRide T3",       "Geometría agresiva, aerobars incluidos. La opción perfecta para triatletas."),
            ("Bicicleta de Ruta Aluminio SpeedX",    "Excelente relación calidad-precio. Marco de aluminio 6061, frenos de llanta de alto perfil."),
        ],
    },
    {
        "image": "bicicleta3",
        "variants": [
            ("Bicicleta Urbana City Glide 7",        "7 velocidades, guardabarros, porta equipaje trasero y luz LED incluida. Para el día a día."),
            ("Bicicleta Eléctrica E-Ride 250W",      "Motor de 250W, batería de 36V, autonomía de 60km. Asistida al pedaleo."),
            ("Bicicleta Plegable FoldUp 20\"",       "Se pliega en segundos, ideal para combinar con transporte público."),
            ("Bicicleta Paseo Vintage Retro Classic","Diseño retro con asiento de cuero, canasto delantero y campanilla."),
            ("Bicicleta de Ciudad CommuterPro",      "Cuadro mixto, posición erguida, neumáticos antipinchazos. Perfecta para ir al trabajo."),
            ("Bicicleta Híbrida UrbanCross 28\"",    "Lo mejor de ruta y ciudad: cómoda, veloz y práctica."),
        ],
    },
    # ── Celulares ──
    {
        "image": "iphone",
        "variants": [
            ("iPhone 15 Pro Max 256GB",              "Pantalla Super Retina XDR 6.7\", chip A17 Pro, cámara triple 48MP, titanio grado aeroespacial."),
            ("iPhone 15 128GB Negro",                "Chip A16 Bionic, pantalla Dynamic Island, cámara principal 48MP, USB-C."),
            ("iPhone 14 Pro 256GB Morado",           "Pantalla Always-On 6.1\", chip A16, cámara ProRes 4K, Dynamic Island."),
            ("iPhone 13 128GB Rojo",                 "Pantalla OLED 6.1\" Super Retina, chip A15, batería mejorada, doble cámara."),
            ("iPhone SE 3ra Gen 64GB",               "El iPhone más compacto: chip A15 Bionic, 4.7\", compatible con 5G."),
            ("iPhone 15 Plus 512GB Azul",            "La pantalla más grande de la línea estándar: 6.7\", batería de larga duración."),
            ("iPhone 14 Plus 128GB Amarillo",        "Pantalla 6.7\" Super Retina XDR, chip A15, cámara dual mejorada con modo noche."),
        ],
    },
    # ── Electrodomésticos ──
    {
        "image": "licuadora",
        "variants": [
            ("Licuadora Oster Pro 1200W",            "1200W, jarra de vidrio 1.5L, 3 velocidades + pulso, cuchillas de acero inoxidable."),
            ("Licuadora Philips Viva HR2041",        "600W, 2 velocidades, función turbo, boca ancha fácil de limpiar."),
            ("Licuadora Personal BlendJet 2",        "Portátil, recargable USB-C, 3 segundos de carga, ideal para smoothies al paso."),
            ("Licuadora Industrial Vitamix A3500",   "Motor de 2.2HP, pantalla táctil, 5 programas preprogramados, jarra de 2L."),
            ("Licuadora de Vaso Moulinex Easy Blend","450W, jarra de 1.2L, 2 velocidades, libre de BPA, base antideslizante."),
            ("Licuadora Tramontina Fit",             "600W, cuchillas de 4 hojas, 3 velocidades, jarra de 1.7L de vidrio."),
        ],
    },
    {
        "image": "samsung",
        "variants": [
            ("Samsung Galaxy S24 Ultra 256GB",       "Pantalla Dynamic AMOLED 6.8\" 120Hz, S Pen incluido, cámara 200MP, Snapdragon 8 Gen 3."),
            ("Samsung Galaxy A54 5G 128GB",          "Pantalla Super AMOLED 6.4\", batería 5000mAh, triple cámara 50MP, resistencia IP67."),
            ("Samsung Galaxy S23 FE 256GB",          "Edición Fan Edition: pantalla 6.4\" AMOLED, chip Exynos 2200, cámara 50MP."),
            ("Samsung Galaxy Z Fold 5 512GB",        "Smartphone plegable: pantalla interna 7.6\" AMOLED, cover display 6.2\", Galaxy AI."),
            ("Samsung Galaxy Z Flip 5 256GB",        "Diseño clamshell con FlexWindow de 3.4\", pantalla interna 6.7\" AMOLED."),
            ("Samsung Galaxy A34 5G 128GB",          "Pantalla Super AMOLED 6.6\" 120Hz, triple cámara 48MP, batería 5000mAh."),
            ("Samsung Galaxy S24+ 256GB Violeta",    "Pantalla Dynamic AMOLED 6.7\" 120Hz, Galaxy AI integrado, carga 45W."),
        ],
    },
    {
        "image": "microondas",
        "variants": [
            ("Microondas Whirlpool 20L Silver",      "700W, 5 niveles de potencia, función descongelado, plato giratorio de 25.5cm."),
            ("Microondas Grill Electrolux EMG41",    "25L, 900W, grill incorporado, 8 funciones automáticas, display LED."),
            ("Microondas Convección Samsung MC35J",  "35L, grill + convección, 1350W, modo slim fry para frituras saludables."),
            ("Microondas de Empotrar Bosch HMT84M451","20L, apto para instalar en mueble, 800W, función eco, acero inoxidable interior."),
            ("Microondas Compacto Daewoo KOR-6L0B",  "17L, 700W, diseño compacto ideal para oficinas o dormitorios pequeños."),
            ("Microondas Panasonic NN-ST27H",        "20L, 800W, tecnología inverter para cocción uniforme, 5 niveles de potencia."),
        ],
    },
    {
        "image": "heladera",
        "variants": [
            ("Heladera No Frost Samsung RT38K",      "384L, No Frost total, freezer superior, All-Around Cooling, display interior."),
            ("Heladera Side by Side LG GS65WPP",    "620L, Door-in-Door, dispensador de agua y hielo, compresora Linear Inverter."),
            ("Heladera con Freezer Drean DR250L",    "250L, dos puertas, eficiencia energética A, gaseosa holder incluido."),
            ("Heladera Gafa HGFX28LFAN",             "277L, no frost, freezer con cajón, LED interior, manijas interiores."),
            ("Heladera Inverter Bosch KAN92VI35",    "562L, compresor inverter, 4 cajones, zona 0° para carnes y pescados."),
            ("Heladera Una Puerta Mabe RMF0400VMXXA","200L, freezer pequeño superior, 3 estantes de vidrio, diseño compacto."),
            ("Heladera Dos Puertas Patrick HP490BC", "493L, no frost, display externo, cielofreezer de 5 estrellas, Wi-Fi."),
        ],
    },
]

# ── Vendedores de prueba ───────────────────────────────────────────────────────
SELLER_NAMES = [
    "TechStore Argentina", "ElectroHogar", "BiciMundo", "MegaShop Online",
    "ImportadoraX", "DirecTech", "HomeSmart", "GadgetHub", "VeloCity Store",
    "ElectroMax", "SmartHome AR", "Mundo Digital",
]

# ── Dominios de email para usuarios de prueba ─────────────────────────────────
EMAIL_DOMAINS = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"]

FIRST_NAMES = [
    "Martina", "Lucas", "Valentina", "Agustín", "Camila", "Nicolás",
    "Sofía", "Tomás", "Florencia", "Mateo", "Julia", "Santiago",
    "Lucía", "Facundo", "Ana", "Diego", "Paula", "Ignacio",
    "Carolina", "Rodrigo", "Natalia", "Ezequiel", "Valeria", "Marcos",
    "Gabriela", "Federico", "Laura", "Gonzalo", "Andrea", "Cristian",
]

LAST_NAMES = [
    "García", "López", "Martínez", "González", "Rodríguez", "Pérez",
    "Sánchez", "Ramírez", "Torres", "Flores", "Álvarez", "Romero",
    "Díaz", "Moreno", "Muñoz", "Herrera", "Ruiz", "Jiménez",
    "Fernández", "Castro", "Ortiz", "Vargas", "Ramos", "Chávez",
    "Silva", "Medina", "Aguilar", "Núñez", "Guzmán", "Reyes",
]


class Command(BaseCommand):
    help = "Llena la base de datos con productos y usuarios de prueba."

    def add_arguments(self, parser):
        parser.add_argument(
            "--products",
            type=int,
            default=100,
            help="Cantidad de productos a crear (default: 100)",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=50,
            help="Cantidad de usuarios a crear (default: 50)",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Elimina todos los productos y usuarios no-staff antes de sembrar",
        )

    def handle(self, *args, **options):
        n_products = options["products"]
        n_users    = options["users"]
        do_flush   = options["flush"]

        self.stdout.write(self.style.MIGRATE_HEADING("\n╔══════════════════════════════════════╗"))
        self.stdout.write(self.style.MIGRATE_HEADING(  "║          SEED DATABASE — ShopDemo    ║"))
        self.stdout.write(self.style.MIGRATE_HEADING(  "╚══════════════════════════════════════╝\n"))

        if do_flush:
            self._flush()

        with transaction.atomic():
            created_users    = self._seed_users(n_users)
            created_products = self._seed_products(n_products)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("━" * 42))
        self.stdout.write(self.style.SUCCESS(f"  ✓ Usuarios creados:  {created_users}"))
        self.stdout.write(self.style.SUCCESS(f"  ✓ Productos creados: {created_products}"))
        self.stdout.write(self.style.SUCCESS("━" * 42))
        self.stdout.write(self.style.SUCCESS("\n  Seed completado exitosamente.\n"))

    # ── Flush ──────────────────────────────────────────────────────────────────

    def _flush(self):
        self.stdout.write(self.style.WARNING("⚠  Eliminando datos existentes..."))
        p_count = Product.objects.count()
        u_count = User.objects.filter(is_staff=False, is_superuser=False).count()
        Product.objects.all().delete()
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        self.stdout.write(self.style.WARNING(f"   → {p_count} productos eliminados"))
        self.stdout.write(self.style.WARNING(f"   → {u_count} usuarios eliminados\n"))

    # ── Usuarios ───────────────────────────────────────────────────────────────

    def _seed_users(self, n_users):
        self.stdout.write(self.style.HTTP_INFO(f"► Creando {n_users} usuarios..."))
        created = 0
        password = "Demo1234!"  # Contraseña fija para todos los usuarios de prueba

        for i in range(1, n_users + 1):
            first = random.choice(FIRST_NAMES)
            last  = random.choice(LAST_NAMES)
            domain = random.choice(EMAIL_DOMAINS)
            # Garantizar unicidad con el índice
            email = f"{first.lower()}.{last.lower()}{i}@{domain}"

            if User.objects.filter(email=email).exists():
                self.stdout.write(f"   [skip] {email} ya existe")
                continue

            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first,
                last_name=last,
                is_admin=False,
            )
            created += 1
            self.stdout.write(
                f"   [{created:>3}/{n_users}] "
                + self.style.SUCCESS(f"{user.get_full_name()}")
                + f"  →  {email}"
            )

        self.stdout.write(
            self.style.HTTP_INFO(f"\n   Contraseña de todos los usuarios: ")
            + self.style.SUCCESS(password)
            + "\n"
        )
        return created

    # ── Productos ──────────────────────────────────────────────────────────────

    def _seed_products(self, n_products):
        self.stdout.write(self.style.HTTP_INFO(f"► Creando {n_products} productos..."))

        # Verificar que la carpeta media/demo existe
        demo_dir = Path("media/demo")
        if not demo_dir.exists():
            self.stdout.write(
                self.style.ERROR(f"   ✗ No se encontró la carpeta media/demo/")
            )
            self.stdout.write(
                self.style.WARNING("   Creando productos sin imagen...")
            )

        # Construir la lista infinita de variantes disponibles
        all_variants = []
        for template in PRODUCT_TEMPLATES:
            image_name = template["image"]
            for name, description in template["variants"]:
                all_variants.append((image_name, name, description))

        # Si necesitamos más productos que variantes, ciclar y numerar
        product_pool = []
        cycle = 0
        while len(product_pool) < n_products:
            for image_name, name, description in all_variants:
                suffix = f" (v{cycle + 1})" if cycle > 0 else ""
                product_pool.append((image_name, name + suffix, description))
                if len(product_pool) >= n_products:
                    break
            cycle += 1

        created = 0
        for i, (image_name, name, description) in enumerate(product_pool[:n_products], 1):
            price = Decimal(str(random.randint(5_000, 500_000)))
            stock = random.randint(0, 200)
            seller = random.choice(SELLER_NAMES)

            image_field_value = self._resolve_image(demo_dir, image_name)

            product = Product(
                name=name,
                description=description,
                price=price,
                owner=seller,
                stock=stock,
            )

            if image_field_value:
                product.image = image_field_value

            product.save()
            created += 1

            status_icon = "📦" if stock > 0 else "❌"
            self.stdout.write(
                f"   [{created:>3}/{n_products}] "
                + self.style.SUCCESS(f"{name[:45]:<45}")
                + f"  ${price:>9,.0f}  stock:{stock:>3}  {status_icon}"
            )

        return created

    def _resolve_image(self, demo_dir, image_name):
        """
        Busca la imagen en media/demo/, la copia a media/products/ y
        devuelve el path relativo para el ImageField.
        """
        if not demo_dir.exists():
            return None

        # Buscar el archivo con cualquier extensión conocida
        extensions = ["jpg", "jpeg", "png", "webp"]
        source_path = None
        for ext in extensions:
            candidate = demo_dir / f"{image_name}.{ext}"
            if candidate.exists():
                source_path = candidate
                break

        if not source_path:
            self.stdout.write(
                self.style.WARNING(f"      ⚠ Imagen no encontrada: {image_name}.*")
            )
            return None

        # Copiar a products/ con nombre único para evitar colisiones
        dest_dir = Path("media/products")
        dest_dir.mkdir(parents=True, exist_ok=True)

        unique_name = f"seed_{image_name}_{random.randint(10000, 99999)}{source_path.suffix}"
        dest_path = dest_dir / unique_name

        shutil.copy2(source_path, dest_path)

        # El ImageField guarda el path relativo a MEDIA_ROOT
        return f"products/{unique_name}"