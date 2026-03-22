# ShopDemo 🛒

Un marketplace e-commerce completo construido con **Django 6**, **Tailwind CSS** y **Flowbite**. Incluye autenticación personalizada, gestión de productos, checkout, historial de órdenes y reseñas verificadas. Diseño moderno oscuro, responsive y listo para demo.

---

✨ Funcionalidades

🛍️ Productos — listado con búsqueda, detalle, CRUD con permisos por propietario

🔐 Autenticación — registro/login por email, perfil de usuario, rol administrador

🛒 Checkout — formulario de entrega y pago, historial de órdenes por usuario

⭐ Reseñas — solo compradores verificados pueden reseñar, una por producto, con calificación de estrellas

🗃️ Seed de demo — comando seed_db que genera 100 productos, usuarios y reseñas de ejemplo

---

## 🚀 Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/django-shop-demo.git
cd django-shop-demo
```

### 2. Crear y activar entorno virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 5. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Compilar Tailwind CSS

```bash
# Instalar dependencias de Node (solo la primera vez)
python manage.py tailwind install

# Compilar para desarrollo (con hot reload)
python manage.py tailwind start

# O compilar una vez para producción
python manage.py tailwind build
```

### 7. Crear superusuario

```bash
python manage.py createsuperuser
```

> Se pedirá email, nombre, apellido y contraseña.

### 8. Cargar datos de demo (opcional pero recomendado)

```bash
# Con valores por defecto: 100 productos, 50 usuarios, 80 reseñas
python manage.py seed_db

# Personalizar cantidades
python manage.py seed_db --products 100 --users 50 --reviews 80

# Limpiar todo y volver a sembrar
python manage.py seed_db --flush --products 100 --users 50 --reviews 80
```

> Todos los usuarios de demo usan la contraseña: **`Demo1234!`**

### 9. Iniciar el servidor

```bash
python manage.py runserver
```

Abrir en el navegador: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🤝 Contribuciones

Este es un proyecto de demo/aprendizaje. Si querés sugerir mejoras o reportar bugs, abrí un issue o un pull request.

---

## 📄 Licencia

MIT — libre para usar, modificar y distribuir.
