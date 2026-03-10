from django.contrib import admin
from .models import OrderedFood, Payment, Order

class OrderedFoodOnline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ['food_item', 'quantity', 'price', 'amount', 'order', 'payment']
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_name', 'name', 'phone', 'email', 'total', 'payment_method', 'status', 'created_at']
    inlines = [OrderedFoodOnline]

# Register your models here.
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)
