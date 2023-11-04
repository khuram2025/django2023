from django.urls import path
from .views import create_product
app_name = 'product'

urlpatterns = [
    # ... other url patterns
    path('add_product/', create_product, name='add_product'),
]
