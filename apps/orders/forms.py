from django import forms


# ── Opciones ──────────────────────────────────────────────────────────────────

COUNTRY_CHOICES = [
    ("AR", "Argentina"),
    ("US", "United States"),
    ("AU", "Australia"),
    ("FR", "France"),
    ("DE", "Germany"),
    ("ES", "Spain"),
    ("UK", "United Kingdom"),
]

CITY_CHOICES = [
    ("Buenos Aires",  "Buenos Aires"),
    ("Córdoba",       "Córdoba"),
    ("Rosario",       "Rosario"),
    ("New York",      "New York"),
    ("Los Angeles",   "Los Angeles"),
    ("San Francisco", "San Francisco"),
    ("Chicago",       "Chicago"),
    ("Sydney",        "Sydney"),
    ("Paris",         "Paris"),
    ("Berlin",        "Berlin"),
    ("Madrid",        "Madrid"),
    ("London",        "London"),
]

# Valores fijos — deben coincidir exactamente con los hidden inputs del HTML
PAYMENT_CHOICES = [
    ("credit_card", "Tarjeta de crédito"),
]

DELIVERY_CHOICES = [
    ("andreani", "Andreani — Envío a domicilio"),
]


# ── Formulario principal ───────────────────────────────────────────────────────

class CheckoutForm(forms.Form):
    """
    Formulario de checkout para una compra individual.
    Método de pago: solo tarjeta de crédito.
    Método de envío: solo Andreani.
    """

    # ── Datos de entrega ──────────────────────────────────────────────────────
    full_name = forms.CharField(
        label="Nombre completo",
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "Juan Pérez"}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"placeholder": "nombre@ejemplo.com"}),
    )
    phone = forms.CharField(
        label="Teléfono",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "123-456-7890"}),
    )
    country = forms.ChoiceField(
        label="País",
        choices=COUNTRY_CHOICES,
    )
    city = forms.ChoiceField(
        label="Ciudad",
        choices=CITY_CHOICES,
    )
    between_streets = forms.CharField(
        label="Entre calles",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Entre Av. Corrientes y Av. Santa Fe"}),
    )
    postal_code = forms.CharField(
        label="Código postal",
        max_length=10,
        widget=forms.TextInput(attrs={"placeholder": "1425"}),
    )
    house_number = forms.CharField(
        label="Número / Depto",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "1234 o 3B"}),
    )

    # ── Método de pago y envío (hidden en el HTML, validados aquí) ────────────
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        initial="credit_card",
    )
    delivery_method = forms.ChoiceField(
        choices=DELIVERY_CHOICES,
        initial="andreani",
    )

    # ── Tarjeta ───────────────────────────────────────────────────────────────
    card_number = forms.CharField(
        label="Número de tarjeta",
        max_length=19,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "1234 5678 9012 3456", "autocomplete": "cc-number"}),
    )
    card_holder = forms.CharField(
        label="Nombre en la tarjeta",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "JUAN PEREZ", "autocomplete": "cc-name"}),
    )
    card_expiry = forms.CharField(
        label="Vencimiento (MM/AA)",
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "MM/AA", "autocomplete": "cc-exp"}),
    )
    card_cvv = forms.CharField(
        label="CVV",
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "•••", "autocomplete": "cc-csc"}),
    )

    # ── Validaciones ──────────────────────────────────────────────────────────

    def clean_card_number(self):
        number = self.cleaned_data.get("card_number", "").replace(" ", "").replace("-", "")
        if not number:
            raise forms.ValidationError("Ingresá el número de tarjeta.")
        if not number.isdigit():
            raise forms.ValidationError("El número de tarjeta solo debe contener dígitos.")
        if len(number) not in (13, 15, 16):
            raise forms.ValidationError("El número debe tener entre 13 y 16 dígitos.")
        return number

    def clean_card_holder(self):
        holder = self.cleaned_data.get("card_holder", "").strip()
        if not holder:
            raise forms.ValidationError("Ingresá el nombre tal como figura en la tarjeta.")
        return holder.upper()

    def clean_card_expiry(self):
        expiry = self.cleaned_data.get("card_expiry", "").strip()
        if not expiry:
            raise forms.ValidationError("Ingresá la fecha de vencimiento.")
        if len(expiry) != 5 or expiry[2] != "/" or not expiry[:2].isdigit() or not expiry[3:].isdigit():
            raise forms.ValidationError("Formato inválido. Usá MM/AA.")
        if not (1 <= int(expiry[:2]) <= 12):
            raise forms.ValidationError("El mes debe estar entre 01 y 12.")
        return expiry

    def clean_card_cvv(self):
        cvv = self.cleaned_data.get("card_cvv", "").strip()
        if not cvv:
            raise forms.ValidationError("Ingresá el CVV.")
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            raise forms.ValidationError("El CVV debe tener 3 o 4 dígitos.")
        return cvv

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone and not all(c.isdigit() or c in "+-() " for c in phone):
            raise forms.ValidationError("Formato de teléfono inválido.")
        return phone

    def clean_postal_code(self):
        postal = self.cleaned_data.get("postal_code", "").strip()
        if not postal:
            raise forms.ValidationError("Ingresá el código postal.")
        if not postal.isdigit():
            raise forms.ValidationError("El código postal solo debe contener números.")
        return postal