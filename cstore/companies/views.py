from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CompanyProfileForm
from .models import CompanyProfile, Schedule
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse
from django.contrib import messages

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

    # Fetching the company associated with the user
    companies = user.owned_companies.all()

    if companies.exists():
        main_company = companies.first()
        main_branch = companies.first().branches.first()  # Get the main branch of the first company
        if main_branch:
            # Print schedules for debugging
            for schedule in main_branch.schedules.all():
                print(f"Day: {schedule.get_day_display()}, Time: {schedule.start_time} - {schedule.end_time}")
    else:
        main_branch = None

    day_choices = Schedule.DAY_CHOICES

    context = {
        
        'profile': profile,
        'companies': companies,
        'branch': main_branch,
        'day_choices': day_choices,
        'main_company': main_company,
    }

    return render(request, 'companies/company_detail.html', context)
