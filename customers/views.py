from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from acounts.forms import UserProfileForm, UserInfoForm
from django.contrib import messages

# Create your views here.
@login_required(login_url='login')
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('cprofile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)
    return render(request, 'customers/cprofile.html', {'profile_form': profile_form, 'user_form': user_form, 'profile': profile})
