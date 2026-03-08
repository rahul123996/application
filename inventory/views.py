from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.db.models import Sum, F, Q, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth

from django.http import HttpResponse

import json
import openpyxl

from .models import Company, ProductVariant, Sale
from .forms import ProductVariantForm


# ===============================
# DASHBOARD
# ===============================
@login_required
def dashboard(request):

    total_products = ProductVariant.objects.count()
    total_sales = Sale.objects.count()

    revenue_expr = ExpressionWrapper(
        F("sold_price") * F("quantity"),
        output_field=DecimalField()
    )

    profit_expr = ExpressionWrapper(
        (F("sold_price") - F("product__purchase_price")) * F("quantity"),
        output_field=DecimalField()
    )

    total_revenue = Sale.objects.aggregate(
        revenue=Sum(revenue_expr)
    )["revenue"] or 0

    total_profit = Sale.objects.aggregate(
        profit=Sum(profit_expr)
    )["profit"] or 0

    low_stock_products = ProductVariant.objects.filter(stock__lt=5)

    top_products = (
        Sale.objects
        .values("product__product_model__name")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")[:5]
    )

    monthly_sales = (
        Sale.objects
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("quantity"))
        .order_by("month")
    )

    months = []
    sales_data = []

    for item in monthly_sales:
        months.append(item["month"].strftime("%b"))
        sales_data.append(item["total"])

    context = {
        "total_products": total_products,
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "low_stock_products": low_stock_products,
        "top_products": top_products,
        "months": json.dumps(months),
        "sales_data": json.dumps(sales_data),
    }

    return render(request, "inventory/dashboard.html", context)


# ===============================
# LOGIN
# ===============================
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")

        return render(request, "inventory/login.html", {
            "error": "Invalid credentials"
        })

    return render(request, "inventory/login.html")


# ===============================
# LOGOUT
# ===============================
def logout_view(request):

    logout(request)
    return redirect("login")


# ===============================
# ADD SALE
# ===============================
@login_required
def add_sale(request):

    if request.method == "POST":

        product_id = request.POST.get("product")
        quantity = int(request.POST.get("quantity"))
        sold_price = float(request.POST.get("sold_price"))

        product = get_object_or_404(ProductVariant, id=product_id)

        if quantity > product.stock:
            messages.error(request, "Not enough stock available")
            return redirect("add_sale")

        Sale.objects.create(
            product=product,
            quantity=quantity,
            sold_price=sold_price,
            sold_by=request.user
        )

        product.stock -= quantity
        product.save()

        messages.success(request, "Sale added successfully")

        return redirect("dashboard")

    products = ProductVariant.objects.all()

    return render(request, "inventory/add_sale.html", {
        "products": products
    })


# ===============================
# SALES HISTORY
# ===============================
@login_required
def sales_history(request):

    sales = Sale.objects.select_related(
        "product",
        "product__product_model",
        "product__product_model__company"
    ).order_by("-date")

    total_sales = sales.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    return render(request, "inventory/sales_history.html", {
        "sales": sales,
        "total_sales": total_sales
    })


# ===============================
# LOW STOCK
# ===============================
@login_required
def low_stock(request):

    products = ProductVariant.objects.filter(stock__lt=5)

    return render(request, "inventory/low_stock.html", {
        "products": products
    })


# ===============================
# PRODUCT LIST
# ===============================
@login_required
def product_list(request):

    query = request.GET.get("q")

    products = ProductVariant.objects.all()

    if query:
        products = products.filter(
            Q(product_model__name__icontains=query) |
            Q(color__icontains=query)
        )

    return render(request, "inventory/product_list.html", {
        "products": products
    })


# ===============================
# ADD PRODUCT
# ===============================
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


# ===============================
# EDIT PRODUCT
# ===============================
@login_required
def edit_product(request, pk):

    product = get_object_or_404(ProductVariant, pk=pk)

    if request.method == "POST":

        form = ProductVariantForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:
        form = ProductVariantForm(instance=product)

    return render(request, "inventory/edit_product.html", {
        "form": form
    })


# ===============================
# DELETE PRODUCT
# ===============================
@login_required
def delete_product(request, pk):

    product = get_object_or_404(ProductVariant, pk=pk)

    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(request, "inventory/delete_product.html", {
        "product": product
    })


# ===============================
# INVOICE
# ===============================
@login_required
def invoice(request, sale_id):

    sale = get_object_or_404(Sale, id=sale_id)

    total = sale.sold_price * sale.quantity

    return render(request, "inventory/invoice.html", {
        "sale": sale,
        "total": total
    })


# ===============================
# EXPORT SALES EXCEL
# ===============================
@login_required
def export_sales_excel(request):

    sales = Sale.objects.all()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Sales Report"

    headers = ["Product", "Quantity", "Price", "Total", "Date", "Sold By"]
    sheet.append(headers)

    for sale in sales:

        total = sale.quantity * sale.sold_price

        sheet.append([
            str(sale.product),
            sale.quantity,
            sale.sold_price,
            total,
            str(sale.date),
            str(sale.sold_by)
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = 'attachment; filename="sales_report.xlsx"'

    workbook.save(response)

    return response