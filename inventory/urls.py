from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('add-sale/', views.add_sale, name='add_sale'),
    path("products/", views.product_list, name="product_list"),
    path("sales-history/", views.sales_history, name="sales_history"),
    path("low-stock/", views.low_stock, name="low_stock"),
    path('add-product/', views.add_product, name='add_product'),
]