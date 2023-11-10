from django.shortcuts import render
from django.shortcuts import render, get_object_or_404

from product.models import Category


def product_detail(request, product_id):
    # Dummy product data
    product = {
        'id': product_id,
        'name': 'Sample Product',
        'description': 'This is a sample product description.',
        'price': '29.99',
    }
    return render(request, 'product/product_detail.html', {'product': product})

def index(request):
    root_categories = Category.objects.filter(parent__isnull=True, status=True)
    return render(request, 'home/index.html', {'categories': root_categories})

def test(request):
    return render(request, 'product/product_detail.html')