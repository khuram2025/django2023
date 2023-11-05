from django.shortcuts import render, redirect
from .forms import ProductForm, ProductImageFormSet
from django.http import JsonResponse
from .models import Category, City

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            # Redirect to a new URL:
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(request, 'product/create_product.html', {'form': form, 'formset': formset})

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