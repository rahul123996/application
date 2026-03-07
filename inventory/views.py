from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from .models import Product, Sale, Customer, Category
from .forms import ProductForm, SaleForm


# -------------------------
# DASHBOARD
# -------------------------
@login_required
def dashboard(request):

    products = Product.objects.all()
    sales = Sale.objects.all()

    total_products = products.count()
    total_sales_amount = 0

    for sale in sales:
        total_sales_amount += sale.quantity * sale.sold_price

    low_stock_products = Product.objects.filter(stock__lt=F('min_stock'))

    context = {
        "products": products,
        "sales": sales,
        "total_products": total_products,
        "total_sales_amount": total_sales_amount,
        "low_stock_products": low_stock_products,
    }

    return render(request, "dashboard.html", context)


# -------------------------
# PRODUCT LIST
# -------------------------
@login_required
def product_list(request):

    products = Product.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get("category")

    if category_id:
        products = products.filter(category__id=category_id)

    context = {
        "products": products,
        "categories": categories
    }

    return render(request, "product_list.html", context)


# -------------------------
# ADD PRODUCT
# -------------------------
@login_required
def add_product(request):

    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:
        form = ProductForm()

    return render(request, "add_product.html", {"form": form})


# -------------------------
# EDIT PRODUCT
# -------------------------
@login_required
def edit_product(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:
        form = ProductForm(instance=product)

    return render(request, "edit_product.html", {"form": form})


# -------------------------
# DELETE PRODUCT
# -------------------------
@login_required
def delete_product(request, pk):

    product = get_object_or_404(Product, pk=pk)

    product.delete()

    return redirect("product_list")


# -------------------------
# ADD SALE
# -------------------------
@login_required
def add_sale(request):

    if request.method == "POST":
        form = SaleForm(request.POST)

        if form.is_valid():

            sale = form.save(commit=False)

            product = sale.product

            if product.stock >= sale.quantity:
                product.stock -= sale.quantity
                product.save()

                sale.sold_by = request.user
                sale.save()

                return redirect("sales_history")

    else:
        form = SaleForm()

    return render(request, "add_sale.html", {"form": form})


# -------------------------
# SALES HISTORY
# -------------------------
@login_required
def sales_history(request):

    sales = Sale.objects.select_related("product", "customer").all()

    return render(request, "sales_history.html", {"sales": sales})