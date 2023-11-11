from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from product.models import Category, Product


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

    today = timezone.now()
    date_7_days_ago = today - timedelta(days=7)
    date_30_days_ago = today - timedelta(days=30)

    root_categories = Category.objects.filter(parent__isnull=True, status=True)
    products_list = Product.objects.annotate(images_count=Count('images')).order_by('-created_at')[:10]

    # Try fetching 10 most viewed products created in the last 7 days
    products = Product.objects.filter(created_at__gte=date_7_days_ago).order_by('-view_count')[:10]

    # If there are less than 10 products, try the last 30 days
    if len(products) < 10:
        products = Product.objects.filter(created_at__gte=date_30_days_ago).order_by('-view_count')[:10]

    # If still less than 10 products, get the most viewed products of all time
    if len(products) < 10:
        products = Product.objects.order_by('-view_count')[:10]

    context = {
        'products_list': products_list,
        'categories': root_categories,
        'products':products
    }
    return render(request, 'home/index.html', context)

def test(request):
    return render(request, 'product/product_detail.html')