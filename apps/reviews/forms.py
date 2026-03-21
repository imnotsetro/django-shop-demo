from django import forms

from .models import Review

RATING_CHOICES = [
    (5, "5 — Excelente"),
    (4, "4 — Muy bueno"),
    (3, "3 — Bueno"),
    (2, "2 — Regular"),
    (1, "1 — Malo"),
]


class ReviewForm(forms.ModelForm):
    """Formulario para crear y editar reseñas."""

    rating = forms.ChoiceField(
        label="Calificación",
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Review
        fields = ["rating", "title", "body"]
        labels = {
            "title": "Título de la reseña",
            "body":  "Comentario",
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Resume tu experiencia en una frase",
                "class": "block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 "
                         "focus:border-primary-600 focus:ring-primary-600 "
                         "dark:border-gray-600 dark:bg-gray-700 dark:text-white "
                         "dark:placeholder:text-gray-400 dark:focus:border-primary-500 dark:focus:ring-primary-500",
            }),
            "body": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Contá tu experiencia con el producto...",
                "class": "block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 "
                         "focus:border-primary-500 focus:ring-primary-500 "
                         "dark:border-gray-600 dark:bg-gray-700 dark:text-white "
                         "dark:placeholder:text-gray-400 dark:focus:border-primary-500 dark:focus:ring-primary-500",
            }),
        }

    def clean_rating(self):
        value = self.cleaned_data.get("rating")
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise forms.ValidationError("Calificación inválida.")
        if value not in range(1, 6):
            raise forms.ValidationError("La calificación debe estar entre 1 y 5.")
        return value