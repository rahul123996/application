from django.shortcuts import render, redirect
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Company, ProductVariant, Sale
from .models import Sale
from django.shortcuts import redirect


@login_required
def dashboard(request):
    total_companies = Company.objects.count()
    total_products = ProductVariant.objects.count()

    from django.db.models import Sum

    total_stock = ProductVariant.objects.aggregate(
        total=Sum("stock")
    )["total"] or 0

    total_sold = ProductVariant.objects.aggregate(
        total=Sum("sold_quantity")
    )["total"] or 0

    total_revenue = Sale.objects.aggregate(
        revenue=Sum(
            ExpressionWrapper(
                F("quantity") * F("variant__selling_price"),
                output_field=DecimalField()
            )
        )
    )["revenue"] or 0

    total_profit = Sale.objects.aggregate(
        profit=Sum(
            ExpressionWrapper(
                (F("variant__selling_price") - F("variant__purchase_price")) * F("quantity"),
                output_field=DecimalField()
            )
        )
    )["profit"] or 0

    low_stock_items = ProductVariant.objects.filter(
        total_stock__lte=F("sold_quantity") + F("reorder_level")
    )

    context = {
        "total_companies": total_companies,
        "total_products": total_products,
        "total_stock": total_stock,
        "total_sold": total_sold,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "low_stock_items": low_stock_items,
    }

    return render(request, "inventory/dashboard.html", context)


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
    products = Product.objects.all()

    if request.method == "POST":
        product_id = request.POST.get("product")
        quantity = int(request.POST.get("quantity"))
        sold_price = float(request.POST.get("sold_price"))

        product = Product.objects.get(id=product_id)

        try:
            Sale.objects.create(
                product=product,
                quantity=quantity,
                sold_price=sold_price,
                sold_by=request.user
            )
        except:
            return render(request, "inventory/error.html", {"message": "Not enough stock"})

        return redirect("dashboard")

    return render(request, "inventory/add_sale.html", {"products": products})