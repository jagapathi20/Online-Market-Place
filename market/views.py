from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from market.context_processors import get_cart_counter
from vendor.models import Vendor
from menu.models import Category, FoodItem
from cart.models import Cart

# Create your views here.
def market(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    return render(request, 'marketplace/listings.html', {'vendors': vendors, 'vendor_count': vendor_count})

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    return render(request, 'marketplace/vendor_detail.html', {'vendor': vendor, 'categories': categories, 'cart_items': cart_items})


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                try:
                    checkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    checkCart.save()
                    return JsonResponse({'status': 'success', 'message': 'Cart updated', 'cart_counter': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amount': get_cart_amount(request)})
                except Cart.DoesNotExist:
                    checkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'success', 'message': 'Item added to cart', 'cart_count': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amount': get_cart_amount(request)})
            except FoodItem.DoesNotExist:
                return JsonResponse({'status': 'failed', 'message': 'Food item not found'})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'please login to continue'})


def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                try:
                    checkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if checkCart.quantity > 1:
                        checkCart.quantity -= 1
                        checkCart.save()
                        return JsonResponse({'status': 'success', 'message': 'Cart updated', 'cart_counter': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amount': get_cart_amount(request)})
                    else:
                        checkCart.delete()
                        return JsonResponse({'status': 'success', 'message': 'Item removed from cart', 'cart_counter': get_cart_counter(request), 'qty': 0, 'cart_amount': get_cart_amount(request)})
                except Cart.DoesNotExist:
                    return JsonResponse({'status': 'failed', 'message': 'Item not in cart'})
            except FoodItem.DoesNotExist:
                return JsonResponse({'status': 'failed', 'message': 'Food item not found'})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'please login to continue'})


def cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
        return render(request, 'marketplace/cart.html', {'cart_items': cart_items})
    else:
        return redirect('login')

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item.quantity:
                    cart_item.delete()
                    return JsonResponse({'status': 'success', 'message': 'Item removed from cart', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amount(request)})
            except Cart.DoesNotExist:
                return JsonResponse({'status': 'failed', 'message': 'Item not in cart'})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'please login to continue'})

