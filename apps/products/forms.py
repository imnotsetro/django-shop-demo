from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "owner", "stock", "image"]  # 👈

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is not None and stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            ext = image.name.rsplit(".", 1)[-1].lower()
            if ext not in ("jpg", "jpeg", "png"):
                raise forms.ValidationError("Solo se permiten imágenes JPG o PNG.")
        return image