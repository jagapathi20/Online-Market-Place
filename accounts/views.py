from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from django.contrib import messages
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