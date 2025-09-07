from django.db import models
from user.models import User  # Corrected import to match your 'user' app

class Product(models.Model):
    CATEGORIES = (
        ('vegetable', 'Vegetable'),
        ('fruit', 'Fruit'),
        ('seed', 'Seed'),
        ('dairy', 'Dairy'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
