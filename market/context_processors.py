from .models import Cart

def get_cart_counter(request):
    if request.user.is_authenticated:
        try:
            cart_count = Cart.objects.filter(user=request.user).count()
        except:
            cart_count = 0
    else:
        cart_count = 0
    return {'cart_count': cart_count}

def get_cart_amount(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for cart_item in cart_items:
            subtotal += cart_item.fooditem.price * cart_item.quantity
        tax = subtotal * 0.1
        grand_total = subtotal + tax
    return {'subtotal': subtotal, 'tax': tax, 'grand_total': grand_total}
