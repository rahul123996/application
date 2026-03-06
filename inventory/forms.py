from django import forms
from .models import ProductVariant


class ProductVariantForm(forms.ModelForm):

    class Meta:
        model = ProductVariant

        fields = [
            "product_model",
            "color",
            "stock",
            "purchase_price",
            "selling_price"
        ]