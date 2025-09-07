from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('products/', views.view_products, name='products'),
    path('products/', views.view_products, name='view_products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # Other URLs (home, login, logout, register)
]