from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # ... other url patterns
    path('add_product/', views.create_product, name='add_product'),
    path('search-cities/', views.search_cities, name='search_cities'),
    path('ajax/load-subcategories/', views.load_subcategories, name='ajax_load_subcategories'),  # URL for loading subcategories via AJAX

    path('products/', views.product_list, name='product_list'),
    path('products/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    path('user/<int:user_pk>/products/', views.user_product_list, name='user_product_list'),
    path('ajax/load-custom-fields/', views.ajax_load_custom_fields, name='ajax_load_custom_fields'),
    
]
