from django.shortcuts import render, redirect
from .forms import ProductForm, ProductImageFormSet

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

    return render(request, 'product/add_product.html', {'form': form, 'formset': formset})
