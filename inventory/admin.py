from django.contrib import admin
from .models import Company, ProductModel, ProductVariant, Sale


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company',)    

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product_model', 'color', 'price', 'stock')
    list_filter = ('product_model', 'color')    

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'sold_price', 'date')
    list_filter = ('date',)    

