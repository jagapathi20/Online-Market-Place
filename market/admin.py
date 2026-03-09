from django.contrib import admin
from .models import Cart

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'fooditem', 'quantity', 'created_at', 'updated_at')
    list_filter = ('user', 'fooditem', 'created_at', 'updated_at')
    search_fields = ('user__username', 'fooditem__name')
    ordering = ('-created_at',)

class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'tax_percentage', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('tax_type',)

admin.site.register(Cart, CartAdmin)
admin.site.register(Tax, TaxAdmin)