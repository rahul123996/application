from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User 


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class ProductVariant(models.Model):
    product_model = models.ForeignKey("ProductModel", on_delete=models.CASCADE)
    color = models.CharField(max_length=50)

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.product_model} - {self.color}"


# ✅ NEW MODEL
class Customer(models.Model):

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# ✅ UPDATED SALE MODEL
class Sale(models.Model):

    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField()

    sold_price = models.DecimalField(max_digits=10, decimal_places=2)

    sold_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    date = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.sold_price

    def profit(self):
        return (self.sold_price - self.product.purchase_price) * self.quantity

    def save(self, *args, **kwargs):

        if self.product.stock < self.quantity:
            raise ValidationError("Not enough stock")

        # reduce stock
        self.product.stock -= self.quantity
        self.product.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} - {self.quantity}"
    

class ProductModel(models.Model):

    name = models.CharField(max_length=200)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    min_stock = models.IntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name   