from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from products.models import Product

@login_required(login_url='login')
def cart_view(request):
    order = Order.objects.filter(user=request.user, status='cart').first()
    if order:
        order.update_total_price()
    context = {'order': order}
    return render(request, 'payment/cart.html', context)

@login_required(login_url='login')
def update_cart_item(request, item_id):
    if request.method == 'POST':
        order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status='cart')
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            order_item.delete()
            messages.success(request, f"{order_item.product.name} removed from cart.")
        elif quantity > order_item.product.stock:
            messages.error(request, f"Cannot add {quantity}. Only {order_item.product.stock} left in stock.")
        else:
            order_item.quantity = quantity
            order_item.save()
            messages.success(request, f"Updated {order_item.product.name} to {quantity} in cart.")

        order_item.order.update_total_price()
        return redirect('payment:cart')
    return redirect('payment:cart')

@login_required(login_url='login')
def remove_cart_item(request, item_id):
    if request.method == 'POST':
        order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status='cart')
        product_name = order_item.product.name
        order_item.delete()
        order_item.order.update_total_price()
        messages.success(request, f"{product_name} removed from cart.")
    return redirect('payment:cart')

@login_required(login_url='login')
def checkout(request):
    order = Order.objects.filter(user=request.user, status='cart').first()
    if not order or not order.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('payment:cart')

    # Update total price before displaying checkout page
    order.update_total_price()

    if request.method == 'POST':
        # Simulate payment processing (replace with actual payment gateway integration)
        shipping_address = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method')

        if not all([shipping_address, payment_method]):
            messages.error(request, "All fields are required.")
            return render(request, 'payment/checkout.html', {'order': order})

        # Check stock availability before processing order
        insufficient_stock_items = []
        for item in order.items.all():
            if item.quantity > item.product.stock:
                insufficient_stock_items.append(f"{item.product.name} (Available: {item.product.stock}, Requested: {item.quantity})")
        
        if insufficient_stock_items:
            messages.error(request, f"Insufficient stock for: {', '.join(insufficient_stock_items)}")
            return render(request, 'payment/checkout.html', {'order': order})

        # Reduce stock for each item in the order
        for item in order.items.all():
            item.product.stock -= item.quantity
            item.product.save(update_fields=['stock'])

        # Update order status and details
        order.status = 'pending'
        order.update_total_price()
        order.save()

        messages.success(request, "Order placed successfully! Stock has been updated.")
        return redirect('payment:order_confirmation', order_id=order.id)

    context = {'order': order}
    return render(request, 'payment/checkout.html', context)

@login_required(login_url='login')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'payment/order_confirmation.html', context)

@login_required(login_url='login')
def cancel_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Only allow cancellation of pending orders
        if order.status == 'pending':
            # Restore stock
            order.restore_stock()
            
            # Update order status
            order.status = 'cancelled'
            order.save()
            
            messages.success(request, f"Order #{order.id} has been cancelled and stock has been restored.")
        else:
            messages.error(request, "Only pending orders can be cancelled.")
    
    return redirect('payment:order_confirmation', order_id=order_id)

def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''