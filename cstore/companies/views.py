from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CompanyProfileForm

@login_required
def create_company(request):
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.save()
            # Redirect to a new URL, for example, the company detail page
            return redirect('company_detail', pk=company.pk)
    else:
        form = CompanyProfileForm()
    return render(request, 'companies/create_company.html', {'form': form})
