from django.urls import path
from . import views
app_name = 'payment'

urlpatterns = [
    path('cart.html/', views.cart_view, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order')
]