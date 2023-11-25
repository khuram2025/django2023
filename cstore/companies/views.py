from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CompanyProfileForm
from .models import CompanyProfile, Schedule
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse
from django.contrib import messages
from .forms import CompanyProfileForm

from companies.models import CompanyProfile

from django.contrib.auth.models import User
from account.models import CustomUser, UserProfile  # Import your CustomUser model
from django.dispatch import receiver
from django.conf import settings
from django.core.files.base import ContentFile
import base64
from django.contrib.auth.decorators import login_required
from account.forms import UserProfileForm



@login_required
def create_company(request):
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user 
            company.save()
            # Redirect to a new URL, for example, the company detail page
            return redirect('company_detail', pk=company.pk)
    else:
        form = CompanyProfileForm()
    return render(request, 'companies/create_company.html', {'form': form})

@login_required
def company_detail(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    companies = user.owned_companies.all()

    if companies.exists():
        main_company = companies.first()
        main_branch = companies.first().branches.first()
        if main_branch:
            for schedule in main_branch.schedules.all():
                print(f"Day: {schedule.get_day_display()}, Time: {schedule.start_time} - {schedule.end_time}")
    else:
        main_branch = None

    if request.method == 'POST':
        print("Received POST request")

        form = CompanyProfileForm(request.POST, request.FILES, instance=main_company)
        print("Form data:", request.POST)

        if form.is_valid():
            print("Form is valid")
            form.save()
            print("Company profile updated")
            return redirect('account:company_detail')  # Adjust the redirect as needed
        else:
            print("Form errors:", form.errors)

    else:
        form = CompanyProfileForm(instance=main_company)

    day_choices = Schedule.DAY_CHOICES

    context = {
        'form': form,
        'profile': profile,
        'companies': companies,
        'branch': main_branch,
        'day_choices': day_choices,
        'main_company': main_company,
    }

    return render(request, 'companies/company_detail.html', context)
