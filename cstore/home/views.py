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
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json


def product_detail(request, product_id):
    # Dummy product data
    product = {
        'id': product_id,
        'name': 'Sample Product',
        'description': 'This is a sample product description.',
        'price': '29.99',
    }
    return render(request, 'product/product_detail.html', {'product': product})

@require_POST
def save_location(request):
    try:
        data = json.loads(request.body)
        request.session['latitude'] = data['latitude']
        request.session['longitude'] = data['longitude']
        request.session.save()  # Explicitly save the session
        print(f"Session saved - Latitude: {request.session.get('latitude')}, Longitude: {request.session.get('longitude')}")
        print(f"Session after saving: {request.session.items()}")
        return JsonResponse({'status': 'success', 'message': 'Location saved'})
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_city_from_coordinates(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        address = data.get("address")
        if not address:
            print(f"No address data found in response.")
            return None

        # Try to get the city from various fields
        city = address.get("city") or address.get("municipality") or address.get("suburb") or address.get("state")

        if city is None:
            print(f"City not found in response. Address data: {address}")
        
        return city

    except requests.RequestException as e:
        print(f"Error while fetching data from Nominatim: {e}")
        return None


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

    request.session['latitude'] = '24.7488368'
    request.session['longitude'] = '46.6616983'
    request.session.save()

    latitude = request.session.get('latitude')
    longitude = request.session.get('longitude')
    client_ip = get_client_ip(request)

    print(f"Latitude from session: {latitude}")
    print(f"Longitude from session: {longitude}")

    print(f"Client IP Address: {client_ip}")

    if latitude and longitude:
        user_city = get_city_from_coordinates(latitude, longitude)
        print(f"User's City: {user_city}")
    else:
        print("Location not working")
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



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt  # Use this only if you're not using Django's CSRF protection
@require_POST
def save_location(request):
    data = json.loads(request.body)
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # If the user is authenticated, save to their profile
    if request.user.is_authenticated:
        user_profile = request.user.userprofile
        user_profile.latitude = latitude
        user_profile.longitude = longitude
        user_profile.save()

    # Otherwise, save in session
    else:
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude

    return JsonResponse({'status': 'success', 'message': 'Location saved'})
