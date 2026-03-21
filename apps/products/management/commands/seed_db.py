"""
Management command: seed_db

Uso:
    python manage.py seed_db
    python manage.py seed_db --products 100 --users 50 --reviews 80
    python manage.py seed_db --flush

Notas:
    - 100 productos distintos con imagenes reales de Unsplash (URLs publicas).
    - Los productos se mezclan aleatoriamente para variedad visual en el listado.
    - Usa bulk_create para insertar en la minima cantidad de queries posible.
    - Los emails nunca contienen acentos ni caracteres especiales.
    - Cada producto referencia a un usuario (owner) como requiere el modelo.
    - Si se piden mas de 100 productos, el catalogo cicla con sufijo (v2), (v3)...
"""

import random
import unicodedata
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import Product

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def strip_accents(text):
    """Elimina acentos y diacriticos para generar emails ASCII limpios."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Catalogo de 100 productos
# Cada tupla: (url_imagen, nombre, descripcion, precio_min, precio_max)
# Los precios estan en pesos argentinos y reflejan rangos realistas por categoria.
# ─────────────────────────────────────────────────────────────────────────────

CATALOG = [
    # ── 1-10: Tecnologia principal ───────────────────────────────────────────
    (
        "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg",
        "Auriculares Bluetooth SoundPro X7",
        "Cancelacion activa de ruido, drivers 40mm, 40hs de bateria, conexion multipunto y plegado compacto para viajes.",
        18_000, 85_000,
    ),
    (
        "https://images.pexels.com/photos/4526407/pexels-photo-4526407.jpeg",
        "Smartwatch FitTrack Pro GPS",
        "GPS integrado, frecuencia cardiaca 24/7, SpO2, resistencia 5ATM, 14 dias de autonomia y mas de 100 modos deporte.",
        35_000, 120_000,
    ),
    (
        "https://images.pexels.com/photos/7989742/pexels-photo-7989742.jpeg",
        "Laptop Ultradelgada SlimBook 14",
        "Intel Core i7 12va gen, 16GB RAM LPDDR5, SSD 512GB NVMe, pantalla IPS 14 FHD 400nits, peso 1.3kg, bateria 65W.",
        280_000, 650_000,
    ),
    (
        "https://images.pexels.com/photos/31541678/pexels-photo-31541678.jpeg",
        "Camara Mirrorless ProShot A7 IV",
        "Sensor full-frame 33MP BSI, video 4K 60fps, estabilizacion IBIS 5 ejes, doble ranura CFexpress, WiFi6 + BT5.",
        450_000, 980_000,
    ),
    (
        "https://images.pexels.com/photos/12564670/pexels-photo-12564670.jpeg",
        "Teclado Mecanico TactilePro RGB TKL",
        "Switches Gateron G Pro 3.0 Red, retroiluminacion RGB por tecla, construccion CNC aluminio, USB-C desmontable.",
        22_000, 75_000,
    ),
    (
        "https://images.pexels.com/photos/14642111/pexels-photo-14642111.jpeg",
        "Mouse Inalambrico ErgoClick M500",
        "Sensor PixArt PMW3395 26000 DPI, 7 botones programables, bateria 70hs, receptor 2.4GHz + Bluetooth dual.",
        8_500, 28_000,
    ),
    (
        "https://images.pexels.com/photos/33298190/pexels-photo-33298190.jpeg",
        "Monitor IPS 27 QHD 144Hz ClearView",
        "Panel IPS 2560x1440 144Hz, 1ms GtG, sRGB 99%, DCI-P3 85%, HDMI 2.0 + DP 1.4, soporte regulable VESA 100.",
        180_000, 420_000,
    ),
    (
        "https://images.pexels.com/photos/19545620/pexels-photo-19545620.jpeg",
        "Silla Gamer ThorneX Pro Series",
        "Estructura acero 1.8mm, espuma 60D alta densidad, apoyabrazos 4D, reclinacion 180 grados, ruedas PU 65mm.",
        95_000, 220_000,
    ),
    (
        "https://images.pexels.com/photos/15840650/pexels-photo-15840650.jpeg",
        "Parlante Bluetooth BassWave 360",
        "Sonido omnidireccional 30W RMS, resistencia IPX7, 24hs autonomia, conexion TWS stereo, carga USB-C rapida.",
        25_000, 90_000,
    ),
    (
        "https://images.pexels.com/photos/9058883/pexels-photo-9058883.jpeg",
        "Headset Gamer HyperSound 7.1 USB",
        "Sonido surround virtual 7.1, microfono retractil -38dBV cancelacion de ruido, almohadillas memory foam 50mm.",
        18_000, 55_000,
    ),
    # ── 11-20: Deportes y outdoor ─────────────────────────────────────────────
    (
        "https://images.pexels.com/photos/2404959/pexels-photo-2404959.png",
        "Zapatillas Running AirStride Carbon Pro",
        "Placa de carbono fibra, espuma ZoomX reactiva, upper Flyknit transpirable, drop 8mm, peso 240g talla 42.",
        45_000, 140_000,
    ),
    (
        "https://images.pexels.com/photos/10835912/pexels-photo-10835912.jpeg",
        "Bicicleta Montana AllTrail 27.5 21v",
        "Cuadro aluminio 6061 T6, horquilla suspension RST 100mm, frenos hidraulicos Tektro, Shimano Altus 3x7v.",
        120_000, 320_000,
    ),
    (
        "https://images.pexels.com/photos/9558021/pexels-photo-9558021.jpeg",
        "Bicicleta Urbana CityRide 7v Comfort",
        "7 velocidades Shimano Nexus, guardabarros acero, portaequipaje trasero, luz LED USB y candado incluidos.",
        85_000, 185_000,
    ),
    (
        "https://images.pexels.com/photos/8565457/pexels-photo-8565457.jpeg",
        "Pelota Futbol ProMatch FIFA Quality Pro",
        "Cuero sintetico termosellado 32 paneles, camara butyl 100%, certificacion FIFA Quality Pro, talla 5.",
        12_000, 38_000,
    ),
    (
        "https://images.pexels.com/photos/15840650/pexels-photo-15840650.jpeg",
        "Raqueta Tenis Head Speed MP 300g",
        "Marco grafeno 360+ Auxetic, peso 300g, balance 315mm, patron 16x19, con encordado Luxilon ALU Power.",
        45_000, 130_000,
    ),
    (
        "https://images.pexels.com/photos/19545620/pexels-photo-19545620.jpeg",
        "Mancuernas Hexagonales Goma 10kg Par",
        "Recubrimiento goma virgen antideslizante, cabeza hexagonal anti-rodamiento, marcacion kg/lb grabada al laser.",
        15_000, 55_000,
    ),
    (
        "https://images.pexels.com/photos/14642111/pexels-photo-14642111.jpeg",
        "Colchoneta Yoga TPE EcoFlow 6mm",
        "TPE biodegradable doble capa, superficie antideslizante seca y humeda, 183x61cm, bolso de transporte incluido.",
        8_500, 28_000,
    ),
    (
        "https://images.pexels.com/photos/14642111/pexels-photo-14642111.jpeg",
        "Casco Ciclismo AeroShell MIPS Pro",
        "Tecnologia MIPS proteccion rotacional, 22 ventilaciones aerodinamicas, cierre BOA L2, peso 260g, CE EN1078.",
        22_000, 68_000,
    ),
    (
        "https://images.pexels.com/photos/14642111/pexels-photo-14642111.jpeg",
        "Botines Futbol SpeedKick Elite FG",
        "Parte superior cuero sintetico Kangaroo-like, suela FG 13 tacos conicos, zona strike precision reforzada.",
        22_000, 75_000,
    ),
    (
        "https://images.pexels.com/photos/7695063/pexels-photo-7695063.jpeg",
        "Campera Deportiva WindShield Softshell 3L",
        "Tejido softshell 3 capas DWR, resistencia viento y lluvia ligera, forro polar 100g, bolsillos YKK con cierre.",
        38_000, 110_000,
    ),
    # ── 21-30: Moda y accesorios ──────────────────────────────────────────────
    (
        "https://images.pexels.com/photos/3108924/pexels-photo-3108924.jpeg",
        "Chaqueta Cuero Genuino UrbanEdge Biker",
        "Cuero vacuno 100% curtido vegetal, forro polar 200g desmontable, 4 bolsillos, cierre YKK, costuras dobles.",
        85_000, 220_000,
    ),
    (
        "https://images.pexels.com/photos/13784288/pexels-photo-13784288.jpeg",
        "Jeans Slim Fit DenimElite 511 Stretch",
        "Denim premium 12oz 98% algodon 2% elastano, corte slim fit, lavado stone wash enzima, 5 bolsillos, tallas 28-42.",
        18_000, 52_000,
    ),
    (
        "https://images.pexels.com/photos/36279914/pexels-photo-36279914.jpeg",
        "Vestido Elegante MidNight Satin Midi",
        "Saten 95% poliester 5% elastano, largo midi rodilla, espalda descubierta lazo, negro/bordo/azul marino.",
        22_000, 68_000,
    ),
    (
        "https://images.pexels.com/photos/10632837/pexels-photo-10632837.jpeg",
        "Blusa Seda Artificial FloralSoft Manga Larga",
        "Tejido viscosa fluido 100%, estampado floral digital, cuello V con lazo, manga larga puno ajustable.",
        12_000, 35_000,
    ),
    (
        "https://images.pexels.com/photos/5991637/pexels-photo-5991637.jpeg",
        "Falda Plisada A-Line SummerFlow Tiro Alto",
        "Crepe 100% poliester, tiro alto elastico invisible, largo rodilla, forro interior, 8 colores disponibles.",
        10_000, 28_000,
    ),
    (
        "https://images.pexels.com/photos/8146448/pexels-photo-8146448.jpeg",
        "Zapatos Oxford ClassicStep Cuero",
        "Cuero genuino bovino, suela Goodyear welted goma antideslizante, plantilla anatomica, negro y marron.",
        38_000, 95_000,
    ),
    (
        "https://images.pexels.com/photos/31153067/pexels-photo-31153067.png",
        "Sandalias Verano ComfortWalk Memory",
        "Plantilla memory foam 20mm, correa ajustable triple tira, suela goma EVA texturada antideslizante, veganas.",
        8_500, 28_000,
    ),
    (
        "https://images.pexels.com/photos/35525638/pexels-photo-35525638.jpeg",
        "Camiseta Algodon Organico EcoBasic 180g",
        "Algodon organico 100% certificado GOTS, tejido jersey 180gsm, cuello redondo reforzado, sin costuras laterales.",
        5_500, 18_000,
    ),
    (
        "https://images.pexels.com/photos/5693888/pexels-photo-5693888.jpeg",
        "Mochila Urbana TechPack 30L Impermeable",
        "Compartimento acolchado laptop 17 pulgadas, puerto USB externo con power bank 10000mAh, material 900D Oxford.",
        25_000, 75_000,
    ),
    (
        "https://images.pexels.com/photos/27726847/pexels-photo-27726847.jpeg",
        "Lentes Sol Polarizados WaveRider UV400",
        "Lentes policarbonato polarizadas 6 capas UV400, montura acetato italiano, estuche rigido + pano incluidos.",
        15_000, 55_000,
    ),
    # ── 31-40: Relojes y joyeria ──────────────────────────────────────────────
    (
        "https://images.pexels.com/photos/277390/pexels-photo-277390.jpeg",
        "Reloj Analogico TimeMaster Acero 316L",
        "Movimiento cuarzo japones Miyota 2035, cristal mineral antirasguños...",
        35_000, 120_000,
    ),
    (
        "https://images.pexels.com/photos/190819/pexels-photo-190819.jpeg",
        "Reloj Digital Outdoor FieldPro X Solar",
        "Altimetro 0-9000m, barometro, brujula electronica...",
        22_000, 85_000,
    ),
    (
        "https://images.pexels.com/photos/1191531/pexels-photo-1191531.jpeg",
        "Collar Plata 925 Cadena Veneciana 45cm",
        "Plata esterlina 925 con baño rodio...",
        8_500, 32_000,
    ),
    (
        "https://images.pexels.com/photos/1454171/pexels-photo-1454171.jpeg",
        "Pulsera Acero Magnetica FusionFit",
        "Acero 316L hipoalergenico...",
        5_500, 18_000,
    ),
    (
        "https://images.pexels.com/photos/265906/pexels-photo-265906.jpeg",
        "Anillo Plata 925 Zirconia",
        "Zirconia corte brillante...",
        6_500, 22_000,
    ),

    # ── Mochilas y accesorios ──────────────────────────────────────────────
    (
        "https://images.pexels.com/photos/2905238/pexels-photo-2905238.jpeg",
        "Mochila Escolar ErgoPack",
        "Ergonomica con soporte lumbar...",
        15_000, 42_000,
    ),
    (
        "https://images.pexels.com/photos/936075/pexels-photo-936075.jpeg",
        "Bolsa Gym SportDuffle",
        "Compartimento ventilado...",
        12_000, 38_000,
    ),
    (
        "https://images.pexels.com/photos/374870/pexels-photo-374870.jpeg",
        "Guantes Deportivos GripMax",
        "Antideslizantes y ergonomicos...",
        5_500, 18_000,
    ),

    # ── Perfumeria y belleza ───────────────────────────────────────────
    (
        "https://images.pexels.com/photos/965989/pexels-photo-965989.jpeg",
        "Perfume Dark Cedar",
        "Fragancia amaderada...",
        28_000, 85_000,
    ),
    (
        "https://images.pexels.com/photos/3373736/pexels-photo-3373736.jpeg",
        "Kit Maquillaje Profesional",
        "Paleta completa...",
        22_000, 68_000,
    ),
    (
        "https://images.pexels.com/photos/4841464/pexels-photo-4841464.jpeg",
        "Crema Facial HyaluroMax",
        "Hidratacion profunda...",
        8_500, 28_000,
    ),

    # ── Hogar ─────────────────────────────────────────────
    (
        "https://images.pexels.com/photos/5552789/pexels-photo-5552789.jpeg",
        "Lampara LED Escritorio",
        "Luz ajustable...",
        12_000, 38_000,
    ),
    (
        "https://images.pexels.com/photos/5552789/pexels-photo-5552789.jpeg",
        "Escritorio Moderno",
        "Estructura metalica...",
        85_000, 220_000,
    ),
    (
        "https://images.pexels.com/photos/276528/pexels-photo-276528.jpeg",
        "Silla Oficina Ergonomica",
        "Respaldo mesh...",
        75_000, 185_000,
    ),
    (
        "https://images.pexels.com/photos/276224/pexels-photo-276224.jpeg",
        "Alfombra Geometrica",
        "Base antideslizante...",
        45_000, 130_000,
    ),
    (
        "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg",
        "Cortinas Blackout",
        "Bloqueo total de luz...",
        18_000, 55_000,
    ),

    # ── Electrodomésticos ──────────────────────────────────────────────
    (
        "https://images.pexels.com/photos/1599791/pexels-photo-1599791.jpeg",
        "Microondas Digital",
        "900W con grill...",
        55_000, 130_000,
    ),
    (
        "https://images.pexels.com/photos/276583/pexels-photo-276583.jpeg",
        "Heladera No Frost",
        "Eficiencia A+...",
        280_000, 650_000,
    ),
    (
        "https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg",
        "Licuadora 1200W",
        "Jarra vidrio...",
        18_000, 55_000,
    ),
    (
        "https://images.pexels.com/photos/276267/pexels-photo-276267.jpeg",
        "Tostadora Acero",
        "4 ranuras...",
        12_000, 35_000,
    ),
    (
        "https://images.pexels.com/photos/699953/pexels-photo-699953.jpeg",
        "Sarten Ceramica",
        "Antiadherente...",
        15_000, 48_000,
    ),

    # ── Comida ─────────────────────────────────────────────
    (
        "https://images.pexels.com/photos/1639557/pexels-photo-1639557.jpeg",
        "Hamburguesa Gourmet",
        "Carne premium...",
        22_000, 55_000,
    ),
    (
        "https://images.pexels.com/photos/825661/pexels-photo-825661.jpeg",
        "Pizza Artesanal",
        "Masa madre...",
        8_500, 22_000,
    ),
    (
        "https://images.pexels.com/photos/357756/pexels-photo-357756.jpeg",
        "Sushi Premium",
        "Box 30 piezas...",
        18_000, 45_000,
    ),
    (
        "https://images.pexels.com/photos/65882/chocolate-dark-coffee-confiserie-65882.jpeg",
        "Chocolate Artesanal",
        "72% cacao...",
        5_500, 18_000,
    ),
    (
        "https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg",
        "Cafe Especialidad",
        "Grano seleccionado...",
        8_500, 28_000,
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# Personas — sin acentos ni caracteres especiales en ningun campo
# ─────────────────────────────────────────────────────────────────────────────

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

# ─────────────────────────────────────────────────────────────────────────────
# Plantillas de resenas
# ─────────────────────────────────────────────────────────────────────────────

REVIEW_TEMPLATES = [
    (5, "Excelente producto",        "Supero todas mis expectativas. Calidad increible y envio rapido. Lo recomiendo sin dudas a todos."),
    (5, "Muy satisfecho",            "Exactamente lo que buscaba. Funciona perfecto, relacion calidad-precio inmejorable."),
    (5, "Compra inmejorable",        "Llego en perfectas condiciones, tal cual se describe. Muy contento con la compra."),
    (5, "Vale cada peso",            "Calidad premium a buen precio. Ya lo recomende a varios amigos, todos quedaron conformes."),
    (5, "Todo perfecto",             "Packaging impecable, llego antes de lo esperado. Sin dudas volveria a comprar en este vendedor."),
    (5, "Supero lo esperado",        "No esperaba tanta calidad por este precio. Funciona impecable desde el primer dia de uso."),
    (4, "Muy buena compra",          "Buen producto en general, funciona muy bien. Le saco una estrella porque el manual esta en ingles."),
    (4, "Satisfecho con la compra",  "Cumple bien con lo prometido, aunque el acabado podria ser un poco mejor. Lo recomiendo igual."),
    (4, "Recomendable",              "Funciona muy bien en el dia a dia. Le saco una estrella porque el embalaje llego algo golpeado."),
    (4, "Buen producto",             "Funciona exactamente como se describe. Buena calidad para el precio que tiene. Lo recomendaria."),
    (4, "Muy completo",              "Tiene todo lo necesario y mas. Facil de usar desde el primer momento, bateria excelente."),
    (4, "Casi perfecto",             "Muy buen producto, solo le falta un pequeno detalle de terminacion para ser ideal del todo."),
    (3, "Cumple lo basico",          "Hace lo que promete pero nada mas. Esperaba un poco mas de calidad por el precio que tiene."),
    (3, "Regular, puede mejorar",    "No esta mal pero existen mejores opciones en el mercado por un precio similar o menor."),
    (3, "Aceptable",                 "Funciona correcto pero tiene detalles de fabricacion que podrian mejorar. Compra aceptable."),
    (2, "Podria ser mejor",          "Tiene fallas de fabricacion evidentes y la atencion al vendedor no fue la mejor experiencia."),
    (2, "Decepcionante",             "No cumple del todo con la descripcion. Le falta robustez y los materiales son de baja calidad."),
    (1, "No lo recomiendo",          "Llego con defectos de fabrica y el vendedor no respondio mis mensajes en ningun momento."),
    (1, "Muy mala calidad",          "No duro ni una semana con uso normal. Calidad pesima para el precio que cobra el vendedor."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Command
# ─────────────────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Llena la base de datos con productos reales, usuarios y resenas."

    def add_arguments(self, parser):
        parser.add_argument("--products", type=int, default=100,
                            help="Cantidad de productos a crear (default: 100)")
        parser.add_argument("--users",    type=int, default=50,
                            help="Cantidad de usuarios a crear (default: 50)")
        parser.add_argument("--reviews",  type=int, default=80,
                            help="Cantidad de resenas a crear (default: 80)")
        parser.add_argument("--flush",    action="store_true",
                            help="Elimina todos los datos no-staff antes de sembrar")

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\n╔══════════════════════════════════════╗\n"
            "║       SEED DATABASE - ShopDemo       ║\n"
            "╚══════════════════════════════════════╝\n"
        ))

        if options["flush"]:
            self._flush()

        with transaction.atomic():
            c_users    = self._seed_users(options["users"])
            c_products = self._seed_products(options["products"])
            c_reviews  = self._seed_reviews(options["reviews"])

        self.stdout.write("\n" + self.style.SUCCESS("━" * 46))
        self.stdout.write(self.style.SUCCESS(f"  + Usuarios creados:  {c_users}"))
        self.stdout.write(self.style.SUCCESS(f"  + Productos creados: {c_products}"))
        self.stdout.write(self.style.SUCCESS(f"  + Resenas creadas:   {c_reviews}"))
        self.stdout.write(self.style.SUCCESS("━" * 46))
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
        # Orden de borrado respeta FK: reviews -> orders -> products -> users
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
        password = "Demo1234!"
        created  = 0

        for i in range(1, n_users + 1):
            first  = random.choice(FIRST_NAMES)
            last   = random.choice(LAST_NAMES)
            domain = random.choice(EMAIL_DOMAINS)
            # Email 100% ASCII: sin acentos, sin caracteres especiales, unico por indice
            email = f"{strip_accents(first).lower()}.{strip_accents(last).lower()}{i}@{domain}"

            if User.objects.filter(email=email).exists():
                continue

            user = User.objects.create_user(
                email=email, password=password,
                first_name=first, last_name=last, is_admin=False,
            )
            created += 1
            self.stdout.write(
                f"   [{created:>3}/{n_users}] "
                + self.style.SUCCESS(f"{user.get_full_name():<22}")
                + f"  ->  {email}"
            )

        self.stdout.write(
            self.style.HTTP_INFO("\n   Contrasena de todos los usuarios: ")
            + self.style.SUCCESS(password) + "\n"
        )
        return created

    # ── Productos ──────────────────────────────────────────────────────────────

    def _seed_products(self, n_products):
        self.stdout.write(self.style.HTTP_INFO(f"► Creando {n_products} productos..."))

        users = list(User.objects.filter(is_staff=False, is_superuser=False))
        if not users:
            users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR("   X No hay usuarios disponibles. Crea usuarios primero."))
            return 0

        # Mezclar el catalogo para que los productos queden variados en el listado
        shuffled = list(CATALOG)
        random.shuffle(shuffled)

        # Ciclar si se piden mas productos que los 100 disponibles
        pool = []
        cycle = 0
        while len(pool) < n_products:
            for url, name, desc, pmin, pmax in shuffled:
                suffix = f" (v{cycle + 1})" if cycle > 0 else ""
                pool.append((url, name + suffix, desc, pmin, pmax))
                if len(pool) >= n_products:
                    break
            cycle += 1
            random.shuffle(shuffled)  # re-mezclar en cada ciclo extra

        # Construir objetos en memoria y hacer bulk_create (1 sola query INSERT)
        to_create  = []
        log_lines  = []
        for url, name, desc, pmin, pmax in pool[:n_products]:
            price = Decimal(str(random.randint(pmin, pmax)))
            stock = random.randint(1, 150)
            to_create.append(Product(
                name=name,
                description=desc,
                price=price,
                owner=random.choice(users),
                stock=stock,
                image=url,  # URL Unsplash almacenada como string en ImageField
            ))
            log_lines.append((name, price, stock))

        Product.objects.bulk_create(to_create, batch_size=50)

        for i, (name, price, stock) in enumerate(log_lines, 1):
            icon = "OK" if stock > 0 else "--"
            self.stdout.write(
                f"   [{i:>3}/{n_products}] "
                + self.style.SUCCESS(f"{name[:42]:<42}")
                + f"  ${price:>9,.0f}  stock:{stock:>3}  {icon}"
            )
        return len(to_create)

    # ── Resenas ────────────────────────────────────────────────────────────────

    def _seed_reviews(self, n_reviews):
        from apps.orders.models import Order
        from apps.reviews.models import Review

        self.stdout.write(self.style.HTTP_INFO(f"► Creando {n_reviews} resenas..."))

        products = list(Product.objects.all())
        users    = list(User.objects.filter(is_staff=False, is_superuser=False))

        if not products or not users:
            self.stdout.write(self.style.WARNING("   ! Se necesitan productos y usuarios para crear resenas."))
            return 0

        # Cargar pares existentes para no violar la unicidad (author, product)
        existing_pairs = set(Review.objects.values_list("author_id", "product_id"))

        orders_bulk  = []
        reviews_bulk = []
        created      = 0
        attempts     = 0

        while created < n_reviews and attempts < n_reviews * 6:
            attempts += 1
            user    = random.choice(users)
            product = random.choice(products)
            pair    = (user.pk, product.pk)
            if pair in existing_pairs:
                continue

            rating, title, body = random.choice(REVIEW_TEMPLATES)

            # Crear orden confirmada simulada si no existe
            # (la logica de negocio requiere haber comprado el producto para resenar)
            order_exists = Order.objects.filter(
                user=user, product=product, status=Order.Status.CONFIRMED,
            ).exists()

            if not order_exists:
                orders_bulk.append(Order(
                    user=user, product=product,
                    quantity=1,
                    unit_price=product.price,
                    total_price=product.price,
                    product_name=product.name,
                    status=Order.Status.CONFIRMED,
                    full_name=user.get_full_name(),
                    email=user.email,
                    phone="", country="AR", city="Buenos Aires",
                    between_streets="", postal_code="1000", house_number="1",
                ))

            reviews_bulk.append(Review(
                product=product, author=user,
                rating=rating, title=title, body=body,
            ))
            existing_pairs.add(pair)
            created += 1

            stars = ("*" * rating).ljust(5)
            self.stdout.write(
                f"   [{created:>3}/{n_reviews}] "
                + self.style.SUCCESS(f"[{stars}]  ")
                + f"{product.name[:35]:<35}  "
                + self.style.HTTP_INFO(f"por {user.get_full_name()}")
            )

        if attempts >= n_reviews * 6 and created < n_reviews:
            self.stdout.write(self.style.WARNING(
                f"   ! Solo se crearon {created} resenas "
                "(combinaciones usuario-producto agotadas)."
            ))

        # Insertar ordenes y resenas en bloque (2 queries total)
        Order.objects.bulk_create(orders_bulk, batch_size=50, ignore_conflicts=True)
        Review.objects.bulk_create(reviews_bulk, batch_size=50, ignore_conflicts=True)

        return created