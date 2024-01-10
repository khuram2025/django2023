from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse
from django.contrib import messages

from companies.models import CompanyProfile
from .forms import SignUpForm
from django.contrib.auth.models import User
from .models import CustomUser, UserProfile  # Import your CustomUser model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.files.base import ContentFile
import base64
from django.contrib.auth.decorators import login_required
from .models import CustomUser, UserProfile
from .forms import UserProfileForm
import requests
import json
from django.views.decorators.csrf import csrf_exempt


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            
            # Log the user in
            login(request, user)

            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('companies:create_company')  # Redirect to create company page after registration
        else:
            print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in the {field}: {error}")
    else:
        form = SignUpForm()
    return render(request, 'account/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        print(f"Attempting to login user with mobile: {mobile}")

        try:
            user_with_mobile = CustomUser.objects.get(mobile=mobile)
            print(f"User with mobile {mobile} exists.")
        except CustomUser.DoesNotExist:
            print(f"No user found with mobile {mobile}.")
            messages.error(request, 'Mobile number is not registered.')
            return render(request, 'account/login.html')

        user = authenticate(request, username=mobile, password=password)
        if user is not None:
            login(request, user)
            print(f"User logged in successfully: {user.mobile}")

            # Check if the user has an associated company
            if CompanyProfile.objects.filter(owner=user).exists():
                return redirect('home:index')  # User has a company, go to home page
            else:
                return redirect('companies:create_company')  # User has no company, go to create company page

        else:
            print(f"Authentication failed for mobile: {mobile}.")
            if not user_with_mobile.is_active:
                print(f"User account with mobile {mobile} is disabled.")
                messages.error(request, 'Your account is disabled.')
            else:
                print(f"Incorrect password for mobile {mobile}.")
                messages.error(request, 'Password is incorrect.')

    return render(request, 'account/login.html')







@csrf_exempt
def mobile_login_api(request):
    print("Request received:", request.method)  # Print the request method

    if request.method == 'POST':
        data = json.loads(request.body)
        mobile = data.get('mobile')
        password = data.get('password')

        print(f"Received mobile: {mobile}")  # Print the received mobile
        print(f"Received password: {password}")  # Print the received password

        try:
            user = CustomUser.objects.get(mobile=mobile)
            if not user.check_password(password):
                print("Incorrect password")
                return JsonResponse({'status': 'error', 'message': 'Incorrect password'}, status=401)
        except CustomUser.DoesNotExist:

            user = authenticate(username=user.username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                print("Login successful")  # Debug print
                return JsonResponse({'status': 'success', 'message': 'Login successful'}, status=200)
            else:
                print("Account disabled")  # Debug print
                return JsonResponse({'status': 'error', 'message': 'Account disabled'}, status=403)
        else:
            print("Invalid credentials")  # Debug print
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)

    print("Invalid request method")  # Debug print
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def dashboard(request):
    # Fetch all companies owned by the user
    companies = request.user.owned_companies.all()

    # Prepare context based on the number of companies
    context = {
        'companies': companies,
        'single_company': companies.first() if companies.exists() else None,
        # ... other context variables ...
    }

    return render(request, 'account/dashboard.html', context)



def get_location_from_ip(ip_address):
    response = requests.get(f'http://ip-api.com/json/{ip_address}')
    data = response.json()

    if data['status'] == 'success':
        return {
            'latitude': data['lat'],
            'longitude': data['lon'],
            'city': data['city']
        }
    else:
        return None

# Example usage
location_data = get_location_from_ip('YOUR_PUBLIC_IP_ADDRESS')
print(location_data)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()



@login_required
def user_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Fetching the company associated with the user
    # Assuming 'user' has a foreign key to 'CompanyProfile' named 'company'
    companies = user.owned_companies.all()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            if 'pp_blob' in request.POST:
                image_data = request.POST['pp_blob']
                if ';base64,' in image_data:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    profile.profile_picture.save(f'profile_{user.pk}.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)
                else:
                    print("Invalid image data format")

            form.save()
            return redirect('account:user_profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'companies': companies,
    }

    return render(request, 'account/user_profile.html', context)


