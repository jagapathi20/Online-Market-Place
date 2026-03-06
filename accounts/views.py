from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from django.contrib import messages
from vendor.forms import VendorForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import send_verification_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
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
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
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
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Vendor created successfully')
            return redirect('registerVendor')
        else:
            print(form.errors)
            print(v_form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    return render(request, 'accounts/registerVendor.html', {'form': form, 'v_form': v_form})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (Exception, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated successfully')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('registerUser')

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

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.get(email_exact=email)
        if user:
            mail_subject = "Reset your Password"
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Password reset link has benn sent to your email address')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('myAccount')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_axtive = True
            user.save()
            messages.success(request, 'Password reset successfull')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'accounts/reset_password.html')