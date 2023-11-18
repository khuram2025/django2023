from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
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

    # Get city from request (e.g., a session variable, a cookie, or a request parameter)
    selected_city = request.session.get('selected_city')  # or any other method you prefer

    # Filter products based on the selected city
    if selected_city:
        products_query = Product.objects.filter(city__name=selected_city)
    else:
        products_query = Product.objects.all()

    products_list = products_query.annotate(images_count=Count('images')).order_by('-created_at')[:10]
    selected_city = request.session.get('selected_city', 'Location')

    # Apply the same city filter for the most viewed products
    products = products_query.filter(created_at__gte=date_7_days_ago).order_by('-view_count')[:10]
    if len(products) < 10:
        products = products_query.filter(created_at__gte=date_30_days_ago).order_by('-view_count')[:10]
    if len(products) < 10:
        products = products_query.order_by('-view_count')[:10]

    top_cities = Product.objects.values('city__name').annotate(product_count=Count('id')).order_by('-product_count')[:5]

    context = {
        'products_list': products_list,
        'categories': root_categories,
        'products': products,
        'selected_city': selected_city,
        'top_cities': top_cities,
    }
    return render(request, 'home/index.html', context)

@require_POST
@csrf_exempt
def update_city(request):
    try:
        data = json.loads(request.body)

        selected_city = data.get('city')
        if selected_city == 'None':  # Check for the 'None' or similar value
            del request.session['selected_city']  # Remove the city from the session
        else:
            request.session['selected_city'] = selected_city

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})




def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')
def terms_conditions(request):
    return render(request, 'home/terms_conditions.html')
def legal_notice(request):
    return render(request, 'home/legal_notice.html')