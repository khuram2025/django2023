from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.models import User
from .models import CustomUser  # Import your CustomUser model

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

