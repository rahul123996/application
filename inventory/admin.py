from django.contrib import admin
from .models import Company, Category, ProductVariant, Sale, Customer, ProductModel

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'category')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        'product_model',
        'color',
        'purchase_price',
        'selling_price',
        'stock',
        'reorder_level'
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone',
        'email'
    )


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'customer',
        'quantity',
        'sold_price',
        'sold_by',
        'date'
    )