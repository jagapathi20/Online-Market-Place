import json
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from accounts.forms import UserProfileForm, UserForm
from django.contrib import messages

from orders.models import OrderedFood, Order

# Create your views here.
@login_required(login_url='login')
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('cprofile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserForm(instance=request.user)
    return render(request, 'customers/cprofile.html', {'profile_form': profile_form, 'user_form': user_form, 'profile': profile})


def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    return render(request, 'customers/y_orders.html', {'orders': orders})


def my_orders(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        ordered_food = OrderedFood.objects.filter(order=order)
        sub_total = 0
        for item in ordered_food:
            sub_total += item.price * item.quantity
        tax_data = json.loads(order.tax_data)
        return render(request, 'customers/order_detail.html', 
        {'order': order, 
        'ordered_food': ordered_food, 
        'sub_total': sub_total, 
        'tax_data': tax_data
        })

    except:
        return redirect('customerDashboard')
    