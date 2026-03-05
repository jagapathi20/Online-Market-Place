from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from django.contrib import messages
from vendor.forms import VendorForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
# Create your views here.


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('myAccount')
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
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('myAccount')
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

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('myAccount')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Logged in successfully')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    if user.role == 1:
        return redirect('vendorDashboard')
    elif user.role == 2:
        return redirect('customerDashboard')
    else:
        return redirect('adminDashboard')

def is_customer(user):
    if user.role == 1:
        return True
    else:
        raise auth.PermissionDenied

def is_vendor(user):
    if user.role == 2:
        return True
    else:
        raise auth.PermissionDenied

@login_required(login_url='login')
@user_passes_test(is_customer)
def customerDashboard(request):
    return render(request, 'accounts/customerDashboard.html')

@login_required(login_url='login')
@user_passes_test(is_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')