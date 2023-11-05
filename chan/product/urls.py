from django.urls import path
from .views import create_product, load_subcategories
from . import views
app_name = 'product'

urlpatterns = [
    # ... other url patterns
    path('add_product/', create_product, name='add_product'),
    path('ajax/load-subcategories/', load_subcategories, name='ajax_load_subcategories'),
    path('search-cities/', views.search_cities, name='search_cities'),
]
