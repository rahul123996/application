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


# FIRST Product model
class ProductModel(models.Model):
    name = models.CharField(max_length=100)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product_model = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.product_model} - {self.color}"


class Sale(models.Model):
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
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

        Sale.objects.create(
            product=product,
            quantity=quantity,
            sold_price=sold_price,
            sold_by=request.user
)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale - {self.product}"