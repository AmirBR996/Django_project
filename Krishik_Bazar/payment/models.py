from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.conf import settings  
class Order(models.Model):
    STATUS_CHOICES = (
        ('cart', 'Cart'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def update_total_price(self):
        """Update the total price of the order based on its items."""
        total = sum(item.quantity * item.price for item in self.items.all())
        self.total_price = total
        self.save(update_fields=['total_price'])
    
    def restore_stock(self):
        """Restore stock when an order is cancelled."""
        for item in self.items.all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])

    def __str__(self):
        return f"Order {self.id} ({self.user.username}, {self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
    