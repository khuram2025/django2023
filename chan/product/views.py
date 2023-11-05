from django.shortcuts import render, redirect
from .forms import ProductForm, ProductImageFormSet
from django.http import JsonResponse
from .models import Category, City, SellerInformation

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            # Process the form data and save the models
            # ...
            return redirect('product_detail', pk=product.pk)
        else:
            # If the form is not valid, print the errors to the console
            print(form.errors, formset.errors)
            # You can also add messages to display the errors in the template using Django's messages framework
            for error in form.errors:
                messages.error(request, error)
            for error in formset.errors:
                messages.error(request, error)
    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(request, 'product/create_product.html', {
        'form': form,
        'formset': formset,
    })

def search_cities(request):
    if 'searchTerm' in request.GET:
        query = request.GET.get('searchTerm')
        cities = City.objects.filter(name__icontains=query).values('id', 'name')
        return JsonResponse(list(cities), safe=False)
    return JsonResponse([], safe=False)


def load_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Category.objects.filter(parent_id=category_id).order_by('title')
    subcategory_list = [{'id': sub.id, 'title': sub.title} for sub in subcategories]
    return JsonResponse(subcategory_list, safe=False)