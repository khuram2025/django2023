from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse
from django.contrib import messages
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


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # You don't need to set user.username = user.mobile if mobile is the USERNAME_FIELD
            user.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect(reverse('login'))  # Redirect to login page after registration
        else:
            # If the form is not valid, print the errors to the console and display them to the user
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
        print(f"Attempting to login user with mobile: {mobile}")  # Print the attempt

        # Check if a user with this mobile exists
        try:
            user_with_mobile = CustomUser.objects.get(mobile=mobile)  # Use CustomUser here
            print(f"User with mobile {mobile} exists.")  # User exists
        except CustomUser.DoesNotExist:  # Use CustomUser here
            print(f"No user found with mobile {mobile}.")  # User does not exist
            messages.error(request, 'Mobile number is not registered.')
            return render(request, 'account/login.html')

        # Attempt to authenticate the user
        user = authenticate(request, username=mobile, password=password)
        if user is not None:
            login(request, user)
            print(f"User logged in successfully: {user.mobile}")  # Print successful login
            return redirect('home:index')  # Replace 'home' with the URL name for your home page.
        else:
            # Authentication failed
            print(f"Authentication failed for mobile: {mobile}.")  # Print failed login
            if not user_with_mobile.is_active:
                print(f"User account with mobile {mobile} is disabled.")
                messages.error(request, 'Your account is disabled.')
            else:
                print(f"Incorrect password for mobile {mobile}.")
                messages.error(request, 'Password is incorrect.')

    return render(request, 'account/login.html')


def dashboard(request):
    return render(request, 'account/dashboard.html')


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

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            if 'pp_blob' in request.POST:
                image_data = request.POST['pp_blob']
                
                # Check if 'image_data' contains the expected separator
                if ';base64,' in image_data:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]

                    # Decode the base64 image and save it
                    profile.profile_picture.save(f'profile_{user.pk}.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)
                else:
                    print("Invalid image data format")

            form.save()
            return redirect('account:user_profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile
    }

    return render(request, 'account/user_profile.html', context)

