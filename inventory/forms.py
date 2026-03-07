from django import forms
from .models import ProductVariant
from .models import Sale

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

class SaleForm(forms.ModelForm):

    class Meta:
        model = Sale
        fields = ['product', 'customer', 'quantity', 'sold_price']        