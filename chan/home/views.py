from django.shortcuts import render
from django.shortcuts import render, get_object_or_404


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
    return render(request, 'home/index.html')
def test(request):
    return render(request, 'account/register.html')