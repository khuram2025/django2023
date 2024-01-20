from django.shortcuts import render, redirect, get_object_or_404

from account.models import CustomUser, UserProfile
from django.urls import reverse

from companies.models import CompanyProfile
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerSerializer
from .models import CustomFieldValue, Customer, Order, OrderItem, Product, StoreProduct, StoreProductStockEntry
from .forms import CompanyProductForm, EditStockEntryForm, OrderForm, ProductForm, StoreProductForm,AddStockForm
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
from django.http import HttpResponse
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db.models import Count

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

@login_required
def create_company_product(request):
    company_profiles = CompanyProfile.objects.filter(owner=request.user)

    if not company_profiles.exists():
        # Redirect to create company page if no company is found
        messages.error(request, "You need to create a company before adding a product.")
        return redirect('home:company_create_message')

    if request.method == 'POST':
        form = CompanyProductForm(request.POST, request.FILES, user=request.user, company_profiles=company_profiles)

        if form.is_valid():
            product = form.save(commit=False)
            product.view_count = 0

            if 'company' in form.cleaned_data and form.cleaned_data['company']:
                product.company = form.cleaned_data['company']
            else:
                messages.error(request, "No Company Assigned")
                return redirect('some_error_handling_view')
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
        if request.method == 'POST':
            form = CompanyProductForm(request.POST, request.FILES, user=request.user, company_profiles=company_profiles)
            # ... [rest of your POST handling code]
        else:
            form = CompanyProductForm(user=request.user, company_profiles=company_profiles)
    # ... [rest of your GET handling code]


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
        if product.company:
            print(f"Company Name: {product.company.name}")
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
    categories = Category.objects.filter(parent__isnull=True).annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:10]
    

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


def product_list_with_offers(request, category_slug=None):
    category = None
    categories = Category.objects.filter(parent__isnull=True).annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:10]
    
    # Join with the Offer model
    products = Product.objects.filter(offers__isnull=False).annotate(images_count=Count('images'))

    # Category filter
    custom_fields = []
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, parent__isnull=True)
        products = products.filter(category__in=category.get_descendants(include_self=True))
        custom_fields = CustomField.objects.filter(categories=category, is_searchable=True)
        for field in custom_fields:
            field.options_list = field.options.split(',') if field.options else []

    # Offer type filter
    offer_type = request.GET.get('sOfferType')
    if offer_type:
        products = products.filter(offers__offer_type=offer_type)
   

    # Other filters (location, condition, price, period) remain the same
    # ...

    products_count = products.count()

    return render(request, 'product/offers.html', {
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
    selected_location = request.GET.get('sLocation', '')

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
        'selected_location': selected_location,
        
        # ... other context variables ...
    }

    return render(request, 'product/product_listing.html', context)


def create_or_import_product(request, pk):
    company = get_object_or_404(CompanyProfile, pk=pk)
    print(f"Company ID: {pk}, Company Name: {company.name}")

    if request.user != company.owner:
        return HttpResponse("Unauthorized", status=401)

    initial_data = {
        'city': company.address.city if company.address else None,
        'address': str(company.address) if company.address else None
    }

    if request.method == 'GET' and 'product_id' in request.GET:
        product_id = request.GET.get('product_id')
        existing_store_product = StoreProduct.objects.filter(store=company, product_id=product_id).first()
        print(f"GET Request - Product ID: {product_id}")
        if existing_store_product:
            print(f"Existing Store Product Found - Store Product ID: {existing_store_product.id}")
            initial_data.update({
                'opening_stock': existing_store_product.current_stock,
                'custom_title': existing_store_product.custom_title or existing_store_product.product.title,
                'custom_description': existing_store_product.custom_description or existing_store_product.product.description,
                'sale_price': existing_store_product.sale_price or existing_store_product.product.price
            })

    form = StoreProductForm(initial=initial_data)
    products = Product.objects.filter(is_published=True)

    if request.method == 'POST':
        form = StoreProductForm(request.POST, request.FILES)
        if form.is_valid():
            product_id = request.POST.get('product_id')
            if product_id:
                existing_store_product = StoreProduct.objects.filter(store=company, product_id=product_id).first()
                if existing_store_product:
                    store_product = existing_store_product
                    additional_quantity = form.cleaned_data.get('stock_quantity')
                    store_product.stock_quantity += additional_quantity
                    store_product.current_stock += additional_quantity
                    print(f"Existing store product updated - Product ID: {product_id}, Store Product ID: {store_product.id}")
                else:
                    store_product = form.save(commit=False)
                    store_product.store = company
                    store_product.current_stock = form.cleaned_data.get('stock_quantity')
                    linked_product = Product.objects.get(id=product_id)
                    store_product.product = linked_product
                    print(f"New StoreProduct linked to existing Product - Product ID: {product_id}")
            else:
                new_product = Product(
                    title=form.cleaned_data['custom_title'],
                    description=form.cleaned_data['custom_description'],
                    price=form.cleaned_data['sale_price'],
                    category=form.cleaned_data['category'],
                    city=form.cleaned_data.get('city') or (company.address.city if company.address else None),
                    address=form.cleaned_data.get('address') or (str(company.address) if company.address else None),
                    is_published=False
                )
                new_product.save()
                store_product = form.save(commit=False)
                store_product.store = company
                store_product.product = new_product
                store_product.current_stock = form.cleaned_data.get('stock_quantity')
                print(f"New product created - New Product ID: {new_product.id}, Linked to Store Product ID: {store_product.id}")

            store_product.purchase_price = form.cleaned_data.get('purchase_price', store_product.purchase_price)
            store_product.opening_stock = store_product.current_stock
            store_product.save()
            for f in request.FILES.getlist('product_images'):
                product_image = ProductImage(product=store_product.product, image=f)
                product_image.save()

            return redirect(reverse('companies:company-inventory', args=[pk]))
        else:
            print("Form Errors:", form.errors)

    return render(request, 'companies/create_or_import_product.html', {
        'form': form, 
        'products': products, 
        'company': company, 
        'pk': pk,
        'store_id': company.pk
    })



def get_product_image(request, product_id):
    print(f"Getting image for product ID: {product_id}")
    product = Product.objects.filter(id=product_id).first()
    if product and product.images.all():
        image_url = product.images.all()[0].image.url
        print(f"Image URL: {image_url}") 
        return JsonResponse({'image_url': image_url})
    print("No image found")  # Debug print
    return JsonResponse({'image_url': None})
    

@login_required
def duplicate_product_to_store(request, product_id):
    # Fetch the product to be duplicated
    product = get_object_or_404(Product, pk=product_id)

    # Check if the product is published site-wide
    if not product.is_published:
        # Handle the error, e.g., show a message or redirect
        return render(request, 'error_page.html', {'error': 'This product is not available for duplication.'})

    if request.method == 'POST':
        form = StoreProductForm(request.POST)
        if form.is_valid():
            store_product = form.save(commit=False)
            store_product.product = product  # Linking the duplicated product
            store_product.store = request.user.companyprofile  # Assuming the user's store is linked to their user account
            store_product.save()
            # Redirect to a success page or the store product list
            return redirect('store_product_list')  # Replace with your actual URL name
    else:
        # Pre-populate the form with product details
        initial_data = {
            'custom_title': product.title,
            'custom_description': product.description,
            'sale_price': product.price,
            # Add other fields as needed
        }
        form = StoreProductForm(initial=initial_data)

    return render(request, 'product/duplicate_product.html', {'form': form, 'product': product})

@login_required
def list_products_for_duplication(request):
    # Fetch products that are published site-wide
    products = Product.objects.filter(is_published=True)

    return render(request, 'product/list_products_for_duplication.html', {'products': products})

def get_product(request, store_id, productId):
    try:
        product = Product.objects.get(id=productId)
        print(f"Found product: {product.title}, ID: {product.id}")

        store = CompanyProfile.objects.get(pk=store_id)
        store_product = StoreProduct.objects.filter(store=store, product=product).first()
        if store_product:
            print(f"Found store product with current stock: {store_product.current_stock}")
        else:
            print(f"No matching store product found for store ID: {store_id}")

        image_url = product.images.first().image.url if product.images.first() else None

        data = {
            'title': product.title,
            'description': product.description,
            'price': str(product.price),  # Convert Decimal to string for JSON serialization
            'category_id': product.category.id if product.category else None,
            'city_id': product.city.id if product.city else None,
            'image_url': image_url,
            'opening_stock': store_product.current_stock if store_product else 0
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except CompanyProfile.DoesNotExist:
        return JsonResponse({'error': 'Store not found'}, status=404)

def add_stock_to_store_product(request, store_id, product_id):
    # Ensure the user is authenticated and has permission to add stock
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    # Retrieve the StoreProduct instance using store_id and product_id
    store_product = get_object_or_404(StoreProduct, store_id=store_id, product_id=product_id)

    # Additional permission checks can be added here

    if request.method == 'POST':
        form = AddStockForm(request.POST, store_owner=request.user)

        if form.is_valid():
            additional_quantity = form.cleaned_data.get('additional_quantity')
            purchase_price = form.cleaned_data.get('purchase_price', store_product.purchase_price)

            # Call the add_stock method of StoreProduct
            store_product.add_stock(additional_quantity, purchase_price)

            # Redirect to a success page or back to the product detail page
            return redirect('some-success-view')
        else:
            # Handle the form errors
            return HttpResponse("Form is invalid", status=400)
    else:
        # If GET request, create an empty form
        form = AddStockForm(store_owner=request.user)

    return render(request, 'companies/add_stock.html', {'form': form, 'store_product': store_product})





def edit_stock_entry(request, entry_id):
    stock_entry = get_object_or_404(StoreProductStockEntry, id=entry_id)

    if request.method == 'POST':
        form = EditStockEntryForm(request.POST, instance=stock_entry)
        if form.is_valid():
            form.save()
            return redirect('stock_detail_view', stock_entry.store_product.id)  # Redirect to stock detail view
    else:
        form = EditStockEntryForm(instance=stock_entry)

    return render(request, 'companies/edit_stock_entry.html', {'form': form, 'entry_id': entry_id})

def delete_stock_entry(request, entry_id):
    stock_entry = get_object_or_404(StoreProductStockEntry, id=entry_id)
    store_product = stock_entry.store_product

    if request.method == 'POST':
        store_product_id = store_product.id
        stock_entry.delete()
        return redirect('some_list_view', store_product_id)

    return render(request, 'companies/confirm_delete_stock_entry.html', {'entry_id': entry_id, 'store_product': store_product})








def get_product_details(request):
    product_id = request.GET.get('id')
    if product_id:
        product = Product.objects.filter(id=product_id).values('title', 'description', 'price', 'stock_quantity').first()
        return JsonResponse(product)
    else:
        return JsonResponse({'error': 'Product not found'}, status=404)




def list_store_products(request, store_id):
    try:
        store_products = StoreProduct.objects.filter(store_id=store_id)
    except StoreProduct.DoesNotExist:
        store_products = []

    context = {
        'store_products': store_products,
        'store_id': store_id
    }

    return render(request, 'companies/items_list.html', context)


@csrf_exempt
def create_customer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))  # Decode and load JSON data
            print("Received Customer Create API:", data)

            store_id = data.get('store')
            store = get_object_or_404(CompanyProfile, pk=store_id)
            data['store'] = store  # You might need to adjust this based on your model and serializer

            serializer = CustomerSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
@login_required
def pos_view(request, store_id):
    selected_category = request.GET.get('category', None)
    store_products = StoreProduct.objects.filter(store_id=store_id).select_related('product')

    if selected_category:
        store_products = store_products.filter(product__category__title=selected_category)

    paginator = Paginator(store_products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all categories for filtering options
    all_categories = set(sp.product.category.title for sp in StoreProduct.objects.filter(store_id=store_id))

    # Fetch customers related to the store
    customers = Customer.objects.filter(store_id=store_id)

    context = {
        'all_categories': all_categories,
        'selected_category': selected_category,
        'page_obj': page_obj,
        'store_id': store_id,
        'customers': customers,  # Add customers to the context
    }
    return render(request, 'product/pos.html', context)


from decimal import Decimal  # Import Decimal for handling currency values
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import OrderForm  # Import your OrderForm
from .models import Order, StoreProduct, Customer  # Import your models

@login_required
def submit_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)  # Use your OrderForm if you have one
          # Print form data for debugging
        if form.is_valid():
            print("Received form data:", form.cleaned_data)
            store_id = form.cleaned_data['store'].id
            total_price = Decimal(form.cleaned_data['total_price'])

            selected_product_ids = request.POST.getlist('product_ids')
            quantities = request.POST.getlist('quantities')

            if not selected_product_ids or not quantities:
                messages.error(request, "No products selected.")
                print("No products selected.")
                return redirect('product:pos-view', store_id=form.cleaned_data['store'].id)

            # Fetch actual StoreProduct objects
            products = [get_object_or_404(StoreProduct, id=product_id) for product_id in selected_product_ids]

            # Calculate subtotal using the actual product objects
            subtotal = sum(
                Decimal(quantity) * product.sale_price
                for product, quantity in zip(products, map(int, quantities))
            )
            customer_id = form.cleaned_data['customer'].id if form.cleaned_data['customer'] else None
            payment_type = form.cleaned_data['payment_type']

            # Handle customer assignment
            if customer_id:
                customer = get_object_or_404(Customer, id=customer_id)
            else:
                # Handle the case where no customer is selected
                # This could be a default 'Walk-in Customer' or similar
                customer = None  # Replace with your logic

            # Calculate subtotal
            subtotal = sum(
                Decimal(quantity) * product.sale_price
                for product, quantity in zip(selected_product_ids, quantities)
            )

            # Create an Order instance
            order = Order(
                customer=customer,
                payment_type=payment_type,
                total_price=total_price,
                subtotal=subtotal,  # Set subtotal
                # Add any other necessary fields
            )
            order.save()

            # Create OrderItem instances
            for product_id, quantity in zip(selected_product_ids, quantities):
                product = get_object_or_404(StoreProduct, id=product_id)
                quantity = int(quantity)  # Convert quantity to an integer

                # Calculate total price for the item
                item_total_price = Decimal(quantity) * product.sale_price

                # Create OrderItem instance for each selected product
                order_item = OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.sale_price,  # or any other logic for price
                    total_price=item_total_price  # Set total price for the item
                )
                order_item.save()

                # Update StoreProduct stock
                product.stock_quantity -= quantity
                product.save()

            # Optional: Add other order-related logic here, e.g., sending confirmation emails

            # Redirect to a confirmation page or return a success response
            messages.success(request, "Order submitted successfully.")
            return redirect('order_confirmation', order_id=order.id)
        else:
            # Handle the case where the form is not valid
            print("Form is not valid. Errors:", form.errors)
            messages.error(request, "There was an error in your form.")

    # Handle invalid form submission or non-POST requests
    messages.error(request, "Invalid request.")
    
    return redirect('home:index')  # Redirect to a default POS page or error page

def list_customers(request):
    # Retrieve all customer instances
    customers = Customer.objects.all()

    # If you want to render to a template
    return render(request, 'product/list_customers.html', {'customers': customers})