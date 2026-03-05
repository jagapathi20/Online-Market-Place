from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from django.contrib import messages
from vendor.forms import VendorForm
# Create your views here.

def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user = User.objects.create_user(
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                email=user.email,
                password=user.password
            )
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'User created successfully')
            return redirect('registerUser')
        else:
            print(form.errors)
    else:
        form = UserForm()
    return render(request, 'accounts/registerUser.html', {'form': form})

def registerVendor(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            user = form.save(commit=False)
            user = User.objects.create_user(
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                email=user.email,
                password=user.password
            )
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = user.userprofile
            vendor.save()
            messages.success(request, 'Vendor created successfully')
            return redirect('registerVendor')
        else:
            print(form.errors)
            print(v_form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    return render(request, 'accounts/registerVendor.html', {'form': form, 'v_form': v_form})