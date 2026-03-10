from .models import Cart, Tax

def get_cart_counter(request):
    if request.user.is_authenticated:
        try:
            cart_count = Cart.objects.filter(user=request.user).count()
        except:
            cart_count = 0
    else:
        cart_count = 0
    return {'cart_count': cart_count}

def get_cart_amounts(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    tax_dict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for cart_item in cart_items:
            subtotal += cart_item.fooditem.price * cart_item.quantity
        get_tax = Tax.objects.filter(is_active=True)
        tax = 0
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((subtotal * tax_percentage / 100), 2)
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})
            tax += tax_amount
        grand_total = subtotal + tax
    return {'subtotal': subtotal, 'tax': tax, 'grand_total': grand_total, 'tax_dict': tax_dict}
