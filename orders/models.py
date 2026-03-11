from django.db import models
from accounts.models import User
from menu.models import FoodItem
from vendor.models import Vendor
import json

# Create your models here.

request_object = ''

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        ('RazorPay', 'RazorPay'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.transaction_id} by {self.user.email}"

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Ordered', 'Ordered'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)
    status = models.CharField(max_length=100, choices=STATUS, default='New')
    tax_data = models.JSONField(blank=True, help_text="Data format: {'tax_type: {'tax_percentage': 'tax_amount'}}")
    total_data = models.JSONField(blank=True, null=True)
    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=100)
    is_ordered = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
    

    def order_placed_to(self):
        return ", ".join([str(i) for i in self.vendors.all()])

    
    def get_total_by_vendor(self):
        vendor = Vendor.objects.get(user=request_object.user)
        subtotal = 0
        tax = 0
        tax_dict = {}
        if self.total_data:
            total_data = json.load(self.total_data)
            data = total_data.get(str(vendor.id))
            for key, val in data.items():
                subtotal += float(key)
                val = val.replace("'", '"')
                val = json.loads(val)
                tax_dict.update(val)

                for i in val:
                    for j in val[i]:
                        tax += float(val[i][j])
        grand_total = subtotal + tax
        context = {
            'subtotal': subtotal,
            'tax_dict': tax_dict,
            'grand_total': grand_total
        }
        return context
    
    def __str__(self):
        return f"Order {self.order_number} by {self.user.email}"



class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fooditem.food_title
