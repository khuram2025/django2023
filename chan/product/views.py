from django.shortcuts import render, redirect
from .forms import ProductForm, ProductImageFormSet
from django.http import JsonResponse
from .models import Category, City, SellerInformation
from django.contrib import messages

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            try:
                product = form.save(commit=False)
                product.save()  # Save the product to get an ID for the foreign key
                
                formset.instance = product
                formset.save()  # Save the images associated with the product
                
                messages.success(request, 'Product added successfully!')
                return redirect('product_detail', pk=product.pk)  # Assuming you have a view named 'product_detail'
            except Exception as e:
                messages.error(request, f"Error occurred during save process: {e}")
                # Optionally, log the error here
        else:
            messages.error(request, "There was an error with the form. Please check the details.")
    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(request, 'product/add_product.html', {
        'form': form,
        'formset': formset,
    })

from django.http import JsonResponse

def load_subcategories(request):
    main_category_id = request.GET.get('category_id')
    subcategories = Category.objects.filter(parent_id=main_category_id).order_by('name')
    return JsonResponse(list(subcategories.values('id', 'name')), safe=False)


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