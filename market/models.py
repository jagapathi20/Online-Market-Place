from django.db import models
from django.contrib.auth.models import User
from menu.models import FoodItem

# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return f"{self.quantity} x {self.fooditem.name} in {self.user.username}'s cart"


class Tax(models.Model):
    tax_type = models.CharField(max_length=10, unique=True)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Tax Percentage (%)')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tax'
        verbose_name_plural = 'Taxes'
    
    def __str__(self):
        return self.tax_type