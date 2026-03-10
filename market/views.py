from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance


from accounts.models import UserProfile
from market.context_processors import get_cart_counter
from orders.forms import OrderForm
from vendor.models import OpeningHour, Vendor
from menu.models import Category, FoodItem
from market.models import Cart

from datetime import date, datetime

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
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', 'from_hour')
    today = date.today().weekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    return render(request, 'marketplace/vendor_detail.html', {'vendor': vendor, 'categories': categories, 'cart_items': cart_items, 'opening_hours': opening_hours, 'current_opening_hours': current_opening_hours})


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


def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
        
    address = request.GET.get('address')
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    radius = request.GET['radius']
    keyword = request.GET['keyword']

    fetch_vendors_by_fooditems = FoodItem.objects,filter(food_title_icontains=keyword, is_available=True).values_list('vendor', flat=True)
    vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
    if latitude and longitude and radius:
        point = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
        vendors = vendors.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True), user_profile__location__dwithin=(point, D(km=radius))).annotate(distance=Distance('user_profile__location', point)).order_by('distance')

        for v in vendors:
            v.kms = round(v.distance.km, 1)
    vendor_count = vendors.count()

    return render(request, 'marketplace/search.html', {
        'vendors': vendors,
        'vendor_count': vendor_count
    })


@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count == 0:
        return redirect('marketplace')
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    return render(request, 'marketplace/checkout.html', {'form': form, 'cart_items': cart_items, 'cart_count': cart_count, 'user_profile': user_profile})
