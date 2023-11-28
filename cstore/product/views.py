from django.shortcuts import render, redirect, get_object_or_404

from account.models import CustomUser, UserProfile
from companies.models import CompanyProfile
from .models import CustomFieldValue, Product
from .forms import CompanyProductForm, ProductForm
from django.http import JsonResponse
from .models import Category, City, ProductImage
from django.contrib import messages
from django.db.models import F
from django.db.models import Count
from django.http import Http404
from .models import CustomField
from .documents import ProductDocument
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone

def ajax_load_custom_fields(request):
    category_id = request.GET.get('category_id')
    if category_id:
        fields = CustomField.objects.filter(categories__id=category_id).values('id', 'name', 'field_type', 'options')
        fields_data = list(fields)
        return JsonResponse({'custom_fields': fields_data})
    else:
        return JsonResponse({'custom_fields': []})
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, user=request.user)
        print("FORM DATA:", request.POST)
        
        if form.is_valid():
            product = form.save(commit=False)
            product.seller_information.user = form.user if form.user.is_authenticated else None
            product.save()

            # Handle custom fields
            for key, value in request.POST.items():
                if key.startswith('custom_field_'):
                    field_id = int(key.split('_')[-1])
                    custom_field = CustomField.objects.get(id=field_id)
                    CustomFieldValue.objects.update_or_create(
                        product=product,
                        custom_field=custom_field,
                        defaults={'value': value}
                    )

            # Handle the images
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
            messages.success(request, 'Product added successfully!')
            return redirect('product:product_detail', pk=product.pk)
        else:
            messages.error(request, "There was an error with the form. Please check the details.")
    else:
        form = ProductForm(user=request.user)

    return render(request, 'product/add_product.html', {'form': form})


def create_company_product(request):
    if request.method == 'POST':
        form = CompanyProductForm(request.POST, request.FILES, user=request.user)
        
        print("Form Received: POST =", request.POST)  # Print the POST data received
        print("Form Received: FILES =", request.FILES)  # Print the FILES data received

        if form.is_valid():
            product = form.save(commit=False)
            product.view_count = 0
            print("View Count Set:", product.view_count)
            company_profile = CompanyProfile.objects.get(owner=request.user)
            product.company_information = company_profile
            product.save()

            print("Product saved:", product)  # Print the saved product

            # Handle custom fields
            for key, value in request.POST.items():
                if key.startswith('custom_field_'):
                    field_id = int(key.split('_')[-1])
                    custom_field = CustomField.objects.get(id=field_id)
                    CustomFieldValue.objects.update_or_create(
                        product=product,
                        custom_field=custom_field,
                        defaults={'value': value}
                    )

            # Handle the images
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
            print("Product images uploaded")  # Confirmation of image upload

            messages.success(request, 'Product added successfully!')
            return redirect('product:product_detail', pk=product.pk)
        else:
            print("Form errors:", form.errors)  # Print form errors
            messages.error(request, "There was an error with the form. Please check the details.")
    else:
        form = CompanyProductForm(user=request.user)

    return render(request, 'product/add_company_product.html', {'form': form})

from django.http import JsonResponse

def load_subcategories(request):
    main_category_id = request.GET.get('category_id')
    subcategories = Category.objects.filter(parent_id=main_category_id).order_by('title')  # Changed 'name' to 'title'
    return JsonResponse(list(subcategories.values('id', 'title')), safe=False)

def product_detail(request, pk):
    try:
        # Retrieve the Product instance
        product = get_object_or_404(Product, pk=pk)
        custom_field_values = CustomFieldValue.objects.filter(product=product)

        custom_fields_dict = {cfv.custom_field.name: cfv.value for cfv in custom_field_values}
        
        
        # Update the view count for the product
        Product.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
        
        # Check if the product is part of a subcategory
        related_products_qs = Product.objects.filter(category__in=product.category.get_family()).exclude(pk=pk)

        # Add the count of images for each related product
        related_products_qs = related_products_qs.annotate(images_count=Count('images'))

        # Fetch up to 10 related products
        related_products = related_products_qs[:10]

        # Render the product details in the template with context
        context = {
            'product': product,
            'related_products': related_products,
            'custom_fields': custom_fields_dict,
        }
        return render(request, 'product/product_detail.html', context)
    except Product.DoesNotExist:
        # If the product does not exist, raise a 404 error
        raise Http404("Product does not exist")
    
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.filter(parent__isnull=True)

    products = Product.objects.annotate(images_count=Count('images'))

    # Category filter
    custom_fields = []
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, parent__isnull=True)
        products = products.filter(category__in=category.get_descendants(include_self=True))
        custom_fields = CustomField.objects.filter(categories=category, is_searchable=True)
        for field in custom_fields:
            field.options_list = field.options.split(',') if field.options else []

    # Location filter
    location = request.GET.get('sLocation')
    if location:
        products = products.filter(city__name__icontains=location)

    # Condition filter
    condition = request.GET.get('sCondition')
    if condition:
        products = products.filter(condition=condition)

    # Price range filter
    price_min = request.GET.get('sPriceMin')
    price_max = request.GET.get('sPriceMax')
    if price_min and price_max:
        products = products.filter(price__gte=price_min, price__lte=price_max)

    # Special price conditions
    if request.GET.get('bPriceCheckWithSeller') == '1':
        products = products.filter(check_with_seller=True)
    if request.GET.get('bPriceFree') == '1':
        products = products.filter(price=0)

    # Period filter
    period = request.GET.get('sPeriod')
    if period:
        try:
            days = int(period)
            date_from = timezone.now() - timedelta(days=days)
            products = products.filter(created_at__gte=date_from)
        except ValueError:
            pass
    
    products_count = products.count()

    return render(request, 'product/product_listing.html', {
        'category': category, 
        'categories': categories, 
        'products': products,
        'custom_fields': custom_fields,
        'products_count': products_count,
    })


def user_product_list(request, user_pk):
    # Get the user object, 404 if not found
    user = get_object_or_404(CustomUser, pk=user_pk)
    user_profile = get_object_or_404(UserProfile, user=user)

    # Debug: Print the user's data
    print(f"User: {user.full_name or user.mobile} (ID: {user.pk})")

    # Filter products for the specified user
    products = Product.objects.filter(seller_information__user=user).annotate(images_count=Count('images'))

    # Debug: Print the number of products found
    print(f"Number of products found: {products.count()}")

    # Debug: Print the query that is executed (SQL statement)
    print(f"Query: {products.query}")

    # Pass the user and products to the template
    context = {
        'user': user,
        'user_profile': user_profile,
        'products': products,
    }

    return render(request, 'product/users_listings.html', context)

def search_cities(request):
    if 'searchTerm' in request.GET:
        query = request.GET.get('searchTerm')
        cities = City.objects.filter(name__icontains=query).values('id', 'name')
        return JsonResponse(list(cities), safe=False)
    return JsonResponse([], safe=False)

def product_search(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('sCategory')
    location = request.GET.get('sLocation')
    condition = request.GET.get('sCondition')
    price_min = request.GET.get('sPriceMin')
    price_max = request.GET.get('sPriceMax')
    period = request.GET.get('sPeriod')

    custom_fields = []
    if category_id:
        category = Category.objects.filter(id=category_id).first()
        if category:
            custom_fields_query = CustomField.objects.filter(categories=category, is_searchable=True)
            for field in custom_fields_query:
                field.options_list = field.options.split(',') if field.options else []
                custom_fields.append(field)

    

    print(f"Received query params: query={query}, category_id={category_id}, location={location}, condition={condition}, price_min={price_min}, price_max={price_max}, period={period}")

    base_query = Q()

    # Handle text query
    if query:
        base_query &= (Q(title__icontains=query) | Q(description__icontains=query))

    # Handle category
    if category_id:
        base_query &= Q(category_id=category_id)

    # Handle location
    if location:
        base_query &= Q(city__name__icontains=location)

    # Handle condition
    if condition:
        base_query &= Q(condition=condition)

    # Handle price range
    if price_min:
        base_query &= Q(price__gte=price_min)
    if price_max:
        base_query &= Q(price__lte=price_max)

    # Handle period
    if period:
        try:
            days_ago = timezone.now() - timedelta(days=int(period))
            base_query &= Q(created_at__gte=days_ago)
        except ValueError:
            pass

    print(f"Final query: {base_query}")
    products = Product.objects.filter(base_query)
    print(f"Number of products found: {products.count()}")
    

    context = {
        'products': products,
        'query': query,
        'custom_fields': custom_fields,  # Add custom fields to context
        # ... other context variables ...
    }

    return render(request, 'product/product_listing.html', context)
