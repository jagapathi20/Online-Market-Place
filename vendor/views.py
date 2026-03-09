from django.shortcuts import render, get_object_or_404

from menu.models import Category
from vendor.models import Vendor
from .forms import VendorForm, OpeningHourForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import is_vendor
from .utils import get_vendor
from menu.forms import CategoryForm, FoodItemForm
from django.template.defaultfilters import slugify
from django.contrib import messages

# Create your views here.


@login_required(login_url='login')
@user_passes_test(is_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
    return render(request, 'vendor/vprofile.html', {'profile_form': profile_form, 'vendor_form': vendor_form, 'profile': profile, 'vendor': vendor})

@login_required(login_url='login')
@user_passes_test(is_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    return render(request, 'vendor/menu_builder.html', {'vendor': vendor, 'categories': categories})


@login_required(login_url='login')
@user_passes_test(is_vendor)
def fooditems_by_category(request, pk):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(category=category, vendor=vendor)
    return render(request, 'vendor/fooditems_by_category.html', {'category': category, 'fooditems': fooditems})

@login_required(login_url='login')
@user_passes_test(is_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.save()
            category.slug = slugify(category_name) + '-' + str(category.id)
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
        else:
            form = CategoryForm()
    return render(request, 'vendor/add_category.html', {'form': form})


@login_required(login_url='login')
@user_passes_test(is_vendor)
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
        else:
            form = CategoryForm(instance=category)
    return render(request, 'vendor/edit_category.html', {'form': form, 'category': category})

@login_required(login_url='login')
@user_passes_test(is_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(is_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            food.save()
            messages.success(request, 'Food added successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            form = FoodItemForm()
            form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    return render(request, 'vendor/add_food.html', {'form': form})


def edit_food(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            food.save()
            messages.success(request, 'Food updated successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            form = FoodItemForm(instance=food)
            form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    return render(request, 'vendor/edit_food.html', {'form': form, 'food': food})

def delete_food(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food deleted successfully!')
    return redirect('fooditems_by_category', food.category.id)



def opening_hours(request):
    opening_hours = OpeningHourForm.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    return render(request, 'vendor/opening_hours.html', {'opening_hours': opening_hours, 'form': form})


def add_opening_hour(request):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            try:
                hour = OpeningHourForm.objects.create(
                    vendor=get_vendor(request),
                    day=day,
                    from_hour=from_hour,
                    to_hour=to_hour,
                    is_closed=is_closed
                )
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': day.from_hour, 'to_hour': day.to_hour}
                return JsonResponse(response)
            except Exception as e:
                return JsonResponse({'status': 'failed', 'message': from_hour + '-' + to_hour + 'already exists for this day'})
        else:
            form = OpeningHourForm()
    return render(request, 'vendor/add_opening_hour.html', {'form': form})


def remove_opening_hour(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
            hour = get_object_or_404(OpeningHourForm, pk=pk)
            hour.delete()
            messages.success(request, 'Opening hour removed successfully!')
            return JsonResponse({'status': 'success', 'id': pk})
        else:
            return JsonResponse({'status': 'failed'})
    else:
        return JsonResponse({'status': 'failed'})

