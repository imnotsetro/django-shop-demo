"""
Management command: seed_db
Uso:
    python manage.py seed_db
    python manage.py seed_db --products 100 --users 50 --reviews 80
    python manage.py seed_db --flush
"""

import random
import shutil
import unicodedata
from decimal import Decimal
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import Product

User = get_user_model()


# ── Helpers ───────────────────────────────────────────────────────────────────

def strip_accents(text):
    """Elimina acentos y caracteres diacriticos de un string."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


# ── Imagenes disponibles en media/demo/ ──────────────────────────────────────
DEMO_IMAGES = [
    "bicileta1",
    "bicileta2",
    "bicicleta3",
    "iphone",
    "licuadora",
    "samsung",
    "microondas",
    "heladera",
]

# ── Datos de productos ────────────────────────────────────────────────────────
PRODUCT_TEMPLATES = [
    {
        "image": "bicicleta1",
        "variants": [
            ("Bicicleta de Montana TrailX Pro",     "Rodado 29, cuadro de aluminio, 21 velocidades Shimano. Ideal para senderos y terreno irregular."),
            ("Bicicleta MTB Summit 500",             "Suspension delantera, frenos de disco hidraulicos, cuadro reforzado para maxima resistencia."),
            ("Bicicleta Todo Terreno Explorer",      "Disenada para aventureros. Ruedas anchas, cambios suaves y asiento ergonomico."),
            ("Bicicleta de Montana Juvenil XPeak",  "Perfecta para jovenes deportistas. Liviana, resistente y con colores llamativos."),
            ("Bicicleta Hardtail Enduro 27.5",       "Horquilla de suspension de 100mm, cuadro de acero cromoly, ideal para enduro."),
            ("Bicicleta de Montana CrossRide 650B", "Versatilidad total: funciona tanto en ciudad como en senderos moderados."),
        ],
    },
    {
        "image": "bicicleta2",
        "variants": [
            ("Bicicleta de Ruta Velocity R10",      "Cuadro de carbono ultraliviano, 22 velocidades, ideal para ciclismo de competencia."),
            ("Bicicleta de Carretera AeroSpeed",    "Diseno aerodinamico, manubrio drop bar, transmision Shimano 105 de 11 velocidades."),
            ("Bicicleta Gravel GravelKing GX",      "Combina lo mejor del ciclismo de ruta y montana. Llantas 700c con neumaticos mixtos."),
            ("Bicicleta de Ruta CarbonElite Pro",   "Peso total: 7.8kg. Horquilla de carbono, ruedas de perfil bajo, para largas distancias."),
            ("Bicicleta Triatlon IronRide T3",      "Geometria agresiva, aerobars incluidos. La opcion perfecta para triatletas."),
            ("Bicicleta de Ruta Aluminio SpeedX",   "Excelente relacion calidad-precio. Marco de aluminio 6061, frenos de llanta de alto perfil."),
        ],
    },
    {
        "image": "bicicleta3",
        "variants": [
            ("Bicicleta Urbana City Glide 7",       "7 velocidades, guardabarros, porta equipaje trasero y luz LED incluida. Para el dia a dia."),
            ("Bicicleta Electrica E-Ride 250W",     "Motor de 250W, bateria de 36V, autonomia de 60km. Asistida al pedaleo."),
            ("Bicicleta Plegable FoldUp 20",        "Se pliega en segundos, ideal para combinar con transporte publico."),
            ("Bicicleta Paseo Vintage Retro",       "Diseno retro con asiento de cuero, canasto delantero y campanilla."),
            ("Bicicleta de Ciudad CommuterPro",     "Cuadro mixto, posicion erguida, neumaticos antipinchazos. Perfecta para ir al trabajo."),
            ("Bicicleta Hibrida UrbanCross 28",     "Lo mejor de ruta y ciudad: comoda, veloz y practica."),
        ],
    },
    {
        "image": "iphone",
        "variants": [
            ("iPhone 15 Pro Max 256GB",             "Pantalla Super Retina XDR 6.7\", chip A17 Pro, camara triple 48MP, titanio grado aeroespacial."),
            ("iPhone 15 128GB Negro",               "Chip A16 Bionic, pantalla Dynamic Island, camara principal 48MP, USB-C."),
            ("iPhone 14 Pro 256GB Morado",          "Pantalla Always-On 6.1\", chip A16, camara ProRes 4K, Dynamic Island."),
            ("iPhone 13 128GB Rojo",                "Pantalla OLED 6.1\" Super Retina, chip A15, bateria mejorada, doble camara."),
            ("iPhone SE 3ra Gen 64GB",              "El iPhone mas compacto: chip A15 Bionic, 4.7\", compatible con 5G."),
            ("iPhone 15 Plus 512GB Azul",           "La pantalla mas grande de la linea estandar: 6.7\", bateria de larga duracion."),
            ("iPhone 14 Plus 128GB Amarillo",       "Pantalla 6.7\" Super Retina XDR, chip A15, camara dual mejorada con modo noche."),
        ],
    },
    {
        "image": "licuadora",
        "variants": [
            ("Licuadora Oster Pro 1200W",           "1200W, jarra de vidrio 1.5L, 3 velocidades + pulso, cuchillas de acero inoxidable."),
            ("Licuadora Philips Viva HR2041",        "600W, 2 velocidades, funcion turbo, boca ancha facil de limpiar."),
            ("Licuadora Personal BlendJet 2",       "Portatil, recargable USB-C, 3 segundos de carga, ideal para smoothies al paso."),
            ("Licuadora Industrial Vitamix A3500",  "Motor de 2.2HP, pantalla tactil, 5 programas preprogramados, jarra de 2L."),
            ("Licuadora de Vaso Moulinex Easy",     "450W, jarra de 1.2L, 2 velocidades, libre de BPA, base antideslizante."),
            ("Licuadora Tramontina Fit",            "600W, cuchillas de 4 hojas, 3 velocidades, jarra de 1.7L de vidrio."),
        ],
    },
    {
        "image": "samsung",
        "variants": [
            ("Samsung Galaxy S24 Ultra 256GB",      "Pantalla Dynamic AMOLED 6.8\" 120Hz, S Pen incluido, camara 200MP, Snapdragon 8 Gen 3."),
            ("Samsung Galaxy A54 5G 128GB",         "Pantalla Super AMOLED 6.4\", bateria 5000mAh, triple camara 50MP, resistencia IP67."),
            ("Samsung Galaxy S23 FE 256GB",         "Edicion Fan Edition: pantalla 6.4\" AMOLED, chip Exynos 2200, camara 50MP."),
            ("Samsung Galaxy Z Fold 5 512GB",       "Smartphone plegable: pantalla interna 7.6\" AMOLED, cover display 6.2\", Galaxy AI."),
            ("Samsung Galaxy Z Flip 5 256GB",       "Diseno clamshell con FlexWindow de 3.4\", pantalla interna 6.7\" AMOLED."),
            ("Samsung Galaxy A34 5G 128GB",         "Pantalla Super AMOLED 6.6\" 120Hz, triple camara 48MP, bateria 5000mAh."),
            ("Samsung Galaxy S24+ 256GB",           "Pantalla Dynamic AMOLED 6.7\" 120Hz, Galaxy AI integrado, carga 45W."),
        ],
    },
    {
        "image": "microondas",
        "variants": [
            ("Microondas Whirlpool 20L Silver",     "700W, 5 niveles de potencia, funcion descongelado, plato giratorio de 25.5cm."),
            ("Microondas Grill Electrolux EMG41",   "25L, 900W, grill incorporado, 8 funciones automaticas, display LED."),
            ("Microondas Conveccion Samsung MC35J", "35L, grill + conveccion, 1350W, modo slim fry para frituras saludables."),
            ("Microondas de Empotrar Bosch HMT84",  "20L, apto para instalar en mueble, 800W, funcion eco, acero inoxidable interior."),
            ("Microondas Compacto Daewoo KOR-6L0B", "17L, 700W, diseno compacto ideal para oficinas o dormitorios pequenos."),
            ("Microondas Panasonic NN-ST27H",       "20L, 800W, tecnologia inverter para coccion uniforme, 5 niveles de potencia."),
        ],
    },
    {
        "image": "heladera",
        "variants": [
            ("Heladera No Frost Samsung RT38K",     "384L, No Frost total, freezer superior, All-Around Cooling, display interior."),
            ("Heladera Side by Side LG GS65WPP",   "620L, Door-in-Door, dispensador de agua y hielo, compresora Linear Inverter."),
            ("Heladera con Freezer Drean DR250L",   "250L, dos puertas, eficiencia energetica A, gaseosa holder incluido."),
            ("Heladera Gafa HGFX28LFAN",            "277L, no frost, freezer con cajon, LED interior, manijas interiores."),
            ("Heladera Inverter Bosch KAN92VI35",   "562L, compresor inverter, 4 cajones, zona 0 grados para carnes y pescados."),
            ("Heladera Una Puerta Mabe RMF0400",    "200L, freezer pequeno superior, 3 estantes de vidrio, diseno compacto."),
            ("Heladera Dos Puertas Patrick HP490",  "493L, no frost, display externo, cielofreezer de 5 estrellas, Wi-Fi."),
        ],
    },
]

# ── Nombres y apellidos (sin acentos) ─────────────────────────────────────────
FIRST_NAMES = [
    "Martina", "Lucas", "Valentina", "Agustin", "Camila", "Nicolas",
    "Sofia", "Tomas", "Florencia", "Mateo", "Julia", "Santiago",
    "Lucia", "Facundo", "Ana", "Diego", "Paula", "Ignacio",
    "Carolina", "Rodrigo", "Natalia", "Ezequiel", "Valeria", "Marcos",
    "Gabriela", "Federico", "Laura", "Gonzalo", "Andrea", "Cristian",
]

LAST_NAMES = [
    "Garcia", "Lopez", "Martinez", "Gonzalez", "Rodriguez", "Perez",
    "Sanchez", "Ramirez", "Torres", "Flores", "Alvarez", "Romero",
    "Diaz", "Moreno", "Munoz", "Herrera", "Ruiz", "Jimenez",
    "Fernandez", "Castro", "Ortiz", "Vargas", "Ramos", "Chavez",
    "Silva", "Medina", "Aguilar", "Nunez", "Guzman", "Reyes",
]

EMAIL_DOMAINS = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"]

# ── Plantillas de resenas por calificacion ────────────────────────────────────
REVIEW_TEMPLATES = [
    # 5 estrellas
    (5, "Excelente producto",       "Supero todas mis expectativas. La calidad es increible y el envio fue rapido. Lo recomiendo sin dudas."),
    (5, "Muy satisfecho",           "Exactamente lo que buscaba. Funciona perfecto, la relacion calidad-precio es muy buena."),
    (5, "Compra inmejorable",       "Llego en perfectas condiciones. El producto es tal cual se describe. Muy contento con la compra."),
    (5, "Vale cada peso",           "Calidad premium a buen precio. Ya lo recomende a varios amigos y todos quedaron conformes."),
    (5, "Todo perfecto",            "El producto es de excelente calidad, el packaging estaba bien cuidado y llego antes de lo esperado."),
    (5, "Increible relacion precio","No esperaba tanta calidad por este precio. Funciona impecable desde el primer dia."),
    # 4 estrellas
    (4, "Muy buena compra",         "Buen producto en general. Le doy 4 estrellas porque el manual esta en ingles, pero funciona excelente."),
    (4, "Satisfecho",               "Buena relacion calidad-precio. Cumple bien con lo prometido, aunque podria mejorar el acabado."),
    (4, "Recomendable",             "Lo use varias veces y funciona muy bien. Le saco una estrella porque el embalaje llego un poco golpeado."),
    (4, "Buen producto",            "Funciona como se describe. La calidad es buena para el precio. Lo recomendaria."),
    (4, "Muy completo",             "Tiene todo lo necesario y mas. Facil de usar y duracion de bateria excelente."),
    (4, "Casi perfecto",            "Muy buen producto. Solo le falta un pequeno detalle de terminacion para ser perfecto."),
    # 3 estrellas
    (3, "Cumple lo basico",         "El producto hace lo que promete pero nada mas. Esperaba un poco mas por el precio que tiene."),
    (3, "Regular",                  "No esta mal pero tampoco es lo que esperaba. Hay mejores opciones en el mercado por precio similar."),
    (3, "Aceptable",                "Funciona bien pero tiene algunos detalles de calidad que podrian mejorar. Compra aceptable."),
    # 2 estrellas
    (2, "Podria ser mejor",         "El producto tiene fallas de fabricacion y la atencion al cliente no fue la mejor. Esperaba mas."),
    (2, "Decepcionante",            "No cumple con lo que promete la descripcion. Le falta robustez y los materiales son de baja calidad."),
    # 1 estrella
    (1, "No lo recomiendo",         "Llego defectuoso y el vendedor no respondio mis mensajes. Mala experiencia de compra."),
    (1, "Muy mala calidad",         "El producto no duro ni una semana. Calidad pesima para el precio que cobra."),
]


class Command(BaseCommand):
    help = "Llena la base de datos con productos, usuarios y resenas de prueba."

    def add_arguments(self, parser):
        parser.add_argument("--products", type=int, default=100,
                            help="Cantidad de productos a crear (default: 100)")
        parser.add_argument("--users",    type=int, default=50,
                            help="Cantidad de usuarios a crear (default: 50)")
        parser.add_argument("--reviews",  type=int, default=80,
                            help="Cantidad de resenas de ejemplo a crear (default: 80)")
        parser.add_argument("--flush",    action="store_true",
                            help="Elimina todos los datos no-staff antes de sembrar")

    def handle(self, *args, **options):
        n_products = options["products"]
        n_users    = options["users"]
        n_reviews  = options["reviews"]
        do_flush   = options["flush"]

        self.stdout.write(self.style.MIGRATE_HEADING("\n╔══════════════════════════════════════╗"))
        self.stdout.write(self.style.MIGRATE_HEADING(  "║          SEED DATABASE - ShopDemo    ║"))
        self.stdout.write(self.style.MIGRATE_HEADING(  "╚══════════════════════════════════════╝\n"))

        if do_flush:
            self._flush()

        with transaction.atomic():
            created_users    = self._seed_users(n_users)
            created_products = self._seed_products(n_products)
            created_reviews  = self._seed_reviews(n_reviews)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("━" * 44))
        self.stdout.write(self.style.SUCCESS(f"  + Usuarios creados:  {created_users}"))
        self.stdout.write(self.style.SUCCESS(f"  + Productos creados: {created_products}"))
        self.stdout.write(self.style.SUCCESS(f"  + Resenas creadas:   {created_reviews}"))
        self.stdout.write(self.style.SUCCESS("━" * 44))
        self.stdout.write(self.style.SUCCESS("\n  Seed completado exitosamente.\n"))

    # ── Flush ──────────────────────────────────────────────────────────────────

    def _flush(self):
        from apps.orders.models import Order
        from apps.reviews.models import Review

        self.stdout.write(self.style.WARNING("! Eliminando datos existentes..."))

        counts = {
            "resenas":   Review.objects.count(),
            "ordenes":   Order.objects.count(),
            "productos": Product.objects.count(),
            "usuarios":  User.objects.filter(is_staff=False, is_superuser=False).count(),
        }

        Review.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        User.objects.filter(is_staff=False, is_superuser=False).delete()

        for label, count in counts.items():
            self.stdout.write(self.style.WARNING(f"   -> {count} {label} eliminados"))
        self.stdout.write("")

    # ── Usuarios ───────────────────────────────────────────────────────────────

    def _seed_users(self, n_users):
        self.stdout.write(self.style.HTTP_INFO(f"► Creando {n_users} usuarios..."))
        created  = 0
        password = "Demo1234!"

        for i in range(1, n_users + 1):
            first  = random.choice(FIRST_NAMES)
            last   = random.choice(LAST_NAMES)
            domain = random.choice(EMAIL_DOMAINS)

            # Email completamente limpio: sin acentos, minusculas, con indice
            first_clean = strip_accents(first).lower()
            last_clean  = strip_accents(last).lower()
            email = f"{first_clean}.{last_clean}{i}@{domain}"

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
                + self.style.SUCCESS(f"{user.get_full_name():<22}")
                + f"  ->  {email}"
            )

        self.stdout.write(
            self.style.HTTP_INFO(f"\n   Contrasena de todos los usuarios: ")
            + self.style.SUCCESS(password)
            + "\n"
        )
        return created

    # ── Productos ──────────────────────────────────────────────────────────────

    def _seed_products(self, n_products):
        self.stdout.write(self.style.HTTP_INFO(f"► Creando {n_products} productos..."))

        users = list(User.objects.filter(is_staff=False, is_superuser=False))
        if not users:
            users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR("   X No hay usuarios disponibles."))
            return 0

        demo_dir = Path("media/demo")
        if not demo_dir.exists():
            self.stdout.write(self.style.WARNING("   ! Carpeta media/demo/ no encontrada. Productos sin imagen."))

        # Pool de variantes ciclando si n_products > variantes disponibles
        all_variants = [
            (t["image"], name, desc)
            for t in PRODUCT_TEMPLATES
            for name, desc in t["variants"]
        ]

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
        for image_name, name, description in product_pool[:n_products]:
            price = Decimal(str(random.randint(5_000, 500_000)))
            stock = random.randint(0, 200)

            product = Product(
                name=name,
                description=description,
                price=price,
                owner=random.choice(users),
                stock=stock,
            )

            image_value = self._resolve_image(demo_dir, image_name)
            if image_value:
                product.image = image_value

            product.save()
            created += 1

            icon = "OK" if stock > 0 else "--"
            self.stdout.write(
                f"   [{created:>3}/{n_products}] "
                + self.style.SUCCESS(f"{name[:42]:<42}")
                + f"  ${price:>9,.0f}  stock:{stock:>3}  {icon}"
            )

        return created

    # ── Resenas ────────────────────────────────────────────────────────────────

    def _seed_reviews(self, n_reviews):
        from apps.orders.models import Order
        from apps.reviews.models import Review

        self.stdout.write(self.style.HTTP_INFO(f"► Creando {n_reviews} resenas de ejemplo..."))

        products = list(Product.objects.all())
        users    = list(User.objects.filter(is_staff=False, is_superuser=False))

        if not products or not users:
            self.stdout.write(self.style.WARNING("   ! Se necesitan productos y usuarios para crear resenas."))
            return 0

        created      = 0
        attempts     = 0
        max_attempts = n_reviews * 6

        # Pares (author_id, product_id) ya existentes para respetar unicidad
        existing_pairs = set(
            Review.objects.values_list("author_id", "product_id")
        )

        while created < n_reviews and attempts < max_attempts:
            attempts += 1
            user    = random.choice(users)
            product = random.choice(products)
            pair    = (user.pk, product.pk)

            if pair in existing_pairs:
                continue

            rating, title, body = random.choice(REVIEW_TEMPLATES)

            # Crear orden confirmada si no existe (requerido por la logica de negocio)
            order_exists = Order.objects.filter(
                user=user,
                product=product,
                status=Order.Status.CONFIRMED,
            ).exists()

            if not order_exists:
                Order.objects.create(
                    user=user,
                    product=product,
                    quantity=1,
                    unit_price=product.price,
                    total_price=product.price,
                    product_name=product.name,
                    status=Order.Status.CONFIRMED,
                    full_name=user.get_full_name(),
                    email=user.email,
                    phone="",
                    country="AR",
                    city="Buenos Aires",
                    between_streets="",
                    postal_code="1000",
                    house_number="1",
                )

            Review.objects.create(
                product=product,
                author=user,
                rating=rating,
                title=title,
                body=body,
            )

            existing_pairs.add(pair)
            created += 1

            stars_str = ("*" * rating).ljust(5)
            self.stdout.write(
                f"   [{created:>3}/{n_reviews}] "
                + self.style.SUCCESS(f"[{stars_str}]  ")
                + f"{product.name[:35]:<35}  "
                + self.style.HTTP_INFO(f"por {user.get_full_name()}")
            )

        if attempts >= max_attempts and created < n_reviews:
            self.stdout.write(self.style.WARNING(
                f"   ! Solo se pudieron crear {created} resenas "
                f"(combinaciones usuario-producto agotadas)."
            ))

        return created

    # ── Image helper ───────────────────────────────────────────────────────────

    def _resolve_image(self, demo_dir, image_name):
        """Copia la imagen de demo a products/ y devuelve el path relativo."""
        if not demo_dir.exists():
            return None

        source_path = None
        for ext in ("jpg", "jpeg", "png", "webp"):
            candidate = demo_dir / f"{image_name}.{ext}"
            if candidate.exists():
                source_path = candidate
                break

        if not source_path:
            self.stdout.write(self.style.WARNING(f"      ! Imagen no encontrada: {image_name}.*"))
            return None

        dest_dir = Path("media/products")
        dest_dir.mkdir(parents=True, exist_ok=True)

        unique_name = f"seed_{image_name}_{random.randint(10000, 99999)}{source_path.suffix}"
        shutil.copy2(source_path, dest_dir / unique_name)

        return f"products/{unique_name}"