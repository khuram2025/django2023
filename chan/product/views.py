from django.shortcuts import render, redirect, get_object_or_404

from account.models import CustomUser
from .models import Product
from .forms import ProductForm
from django.http import JsonResponse
from .models import Category, City, ProductImage
from django.contrib import messages
from django.db.models import F
from django.db.models import Count
from django.http import Http404

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, user=request.user if request.user.is_authenticated else None)
        
        if form.is_valid():
            try:
                # Attach the user to the form before saving.
                form._user = request.user if request.user.is_authenticated else None
                product = form.save()  # Save the product to get an ID for the foreign key
                
                # Handle the images
                images = request.FILES.getlist('images')
                for image in images:
                    ProductImage.objects.create(product=product, image=image)
                
                messages.success(request, 'Product added successfully!')
                return redirect('product_detail', pk=product.pk)
            except Exception as e:
                messages.error(request, f"Error occurred during save process: {e}")
        else:
            messages.error(request, "There was an error with the form. Please check the details.")
    else:
        form = ProductForm(user=request.user if request.user.is_authenticated else None)

    return render(request, 'product/add_product.html', {
        'form': form
    })


from django.http import JsonResponse

def load_subcategories(request):
    main_category_id = request.GET.get('category_id')
    subcategories = Category.objects.filter(parent_id=main_category_id).order_by('title')  # Changed 'name' to 'title'
    return JsonResponse(list(subcategories.values('id', 'title')), safe=False)

def product_detail(request, pk):
    try:
        # Retrieve the Product instance
        product = get_object_or_404(Product, pk=pk)
        
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
            'related_products': related_products
        }
        return render(request, 'product/product_detail.html', context)
    except Product.DoesNotExist:
        # If the product does not exist, raise a 404 error
        raise Http404("Product does not exist")
    
def product_list(request):
    products = Product.objects.annotate(images_count=Count('images')).all()
    return render(request, 'product/product_listing.html', {'products': products})

def user_product_list(request, user_pk):
    # Get the user object, 404 if not found
    user = get_object_or_404(CustomUser, pk=user_pk)

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
        'products': products,
    }

    return render(request, 'product/users_listings.html', context)


def search_cities(request):
    if 'searchTerm' in request.GET:
        query = request.GET.get('searchTerm')
        cities = City.objects.filter(name__icontains=query).values('id', 'name')
        return JsonResponse(list(cities), safe=False)
    return JsonResponse([], safe=False)


