from django.shortcuts import render, redirect
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Company, ProductVariant, Sale
from django.db.models import Sum
from .models import ProductVariant
from .forms import ProductVariantForm


@login_required
def dashboard(request):

    total_products = ProductVariant.objects.count()

    total_stock = ProductVariant.objects.aggregate(
        Sum("stock")
    )["stock__sum"] or 0

    total_sales = Sale.objects.aggregate(
        Sum("quantity")
    )["quantity__sum"] or 0

    return render(request, "inventory/dashboard.html", {
        "total_products": total_products,
        "total_stock": total_stock,
        "total_sales": total_sales
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "inventory/login.html", {"error": "Invalid Credentials"})

    return render(request, "inventory/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")

def add_sale(request):
    products = ProductVariant.objects.all()

    if request.method == "POST":
        product_id = request.POST.get("product")
        quantity = int(request.POST.get("quantity"))
        sold_price = float(request.POST.get("sold_price"))

        product = ProductVariant.objects.get(id=product_id)

        if product.stock < quantity:
            return render(request, "inventory/error.html", {
                "message": "Not enough stock available"
            })

        Sale.objects.create(
            product=product,
            quantity=quantity,
            sold_price=sold_price,
            sold_by=request.user
        )

        # Reduce stock
        product.stock -= quantity
        product.save()

        return redirect("dashboard")

    return render(request, "inventory/add_sale.html", {"products": products})

@login_required
def product_list(request):

    products = ProductVariant.objects.select_related(
        "product_model",
        "product_model__company",
        "product_model__category"
    )

    return render(request, "inventory/product_list.html", {
        "products": products
    })

from django.db.models import Sum

@login_required
def sales_history(request):

    sales = Sale.objects.select_related(
        "product",
        "product__product_model",
        "product__product_model__company"
    ).order_by("-date")

    total_sales = sales.aggregate(total=Sum("quantity"))["total"] or 0

    return render(request, "inventory/sales_history.html", {
        "sales": sales,
        "total_sales": total_sales
    })

@login_required
def low_stock(request):

    low_products = ProductVariant.objects.filter(stock__lt=5)

    return render(request, "inventory/low_stock.html", {
        "products": low_products
    })

@login_required
def add_product(request):

    if request.method == "POST":
        form = ProductVariantForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:
        form = ProductVariantForm()

    return render(request, "inventory/add_product.html", {
        "form": form
    })